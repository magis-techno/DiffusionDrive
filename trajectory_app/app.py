"""
Trajectory Prediction Application

Main application class that coordinates inference, data management, and visualization.
"""

import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import yaml
import os

from .inference_engine import TrajectoryInferenceEngine
from .data_manager import TrajectoryDataManager
from .visualizer import TrajectoryVisualizer

logger = logging.getLogger(__name__)


class TrajectoryPredictionApp:
    """
    Main trajectory prediction application
    
    Coordinates model inference, data management, and visualization
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the application
        
        Args:
            config: Configuration dictionary or path to config file
        """
        if isinstance(config, (str, Path)):
            self.config = self._load_config(config)
        else:
            self.config = config
            
        # Initialize logging
        self._setup_logging()
        
        # Initialize components
        self.inference_engine = None
        self.data_manager = None
        self.visualizer = None
        
        # Initialize all components
        self._initialize_components()
        
        logger.info("Trajectory prediction application initialized successfully")
        
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = self.config.get("logging", {}).get("level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """
        Load configuration from YAML file
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Expand environment variables
        config = self._expand_env_vars(config)
        
        return config
    
    def _expand_env_vars(self, obj):
        """Recursively expand environment variables in config"""
        if isinstance(obj, dict):
            return {k: self._expand_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._expand_env_vars(v) for v in obj]
        elif isinstance(obj, str):
            return os.path.expandvars(obj)
        else:
            return obj
    
    def _initialize_components(self):
        """
        Initialize all application components in correct order
        """
        logger.info("Initializing trajectory prediction application components...")
        
        # 1. Initialize inference engine and load model
        logger.info("Loading model...")
        self.inference_engine = TrajectoryInferenceEngine(self.config["model"])
        self.inference_engine.load_model()
        
        # 2. Initialize data manager with inference engine
        logger.info("Initializing data manager...")
        self.data_manager = TrajectoryDataManager(
            self.config["data"], 
            self.inference_engine
        )
        
        # 3. Initialize visualizer
        logger.info("Initializing visualizer...")
        self.visualizer = TrajectoryVisualizer(
            self.config.get("visualization", {})
        )
        
        # Log initialization summary
        stats = self.data_manager.get_scene_statistics()
        model_info = self.inference_engine.get_model_info()
        
        logger.info(f"Initialization complete!")
        logger.info(f"Model: {model_info['model_type']} ({model_info['status']})")
        logger.info(f"Available scenes: {stats['total_scenes']}")
        logger.info(f"Metric cache: {'available' if stats['has_metric_cache'] else 'not available'}")
    
    def predict_single_scene(
        self, 
        scene_token: str, 
        time_window: Tuple[float, float] = (0, 3.0),
        save_visualization: bool = True,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Predict trajectory for a single scene and create visualization
        
        Args:
            scene_token: Scene token to process
            time_window: Time window for visualization (start, end) in seconds
            save_visualization: Whether to save visualization
            output_dir: Output directory for results
            
        Returns:
            Dictionary containing prediction results and paths
        """
        logger.info(f"Processing scene: {scene_token}")
        start_time = time.time()
        
        # 1. Load scene data
        scene_data = self.data_manager.load_scene_data(scene_token)
        
        # 2. Get existing trajectories (GT, PDM)
        existing_trajectories = self.data_manager.get_all_trajectories(scene_token)
        
        # 3. Predict trajectory
        agent_input = scene_data["scene"].get_agent_input()
        prediction_result = self.inference_engine.predict_trajectory(
            agent_input, scene_data["scene"]
        )
        
        # 4. Combine all trajectories
        all_trajectories = existing_trajectories.copy()
        all_trajectories["prediction"] = prediction_result["trajectory"]
        
        # 5. Synchronize trajectories
        synchronized_trajectories = self.data_manager.synchronize_trajectories(
            all_trajectories, 
            time_horizon=time_window[1] + 1.0,  # Add buffer
            dt=0.1
        )
        
        # 6. Create visualization
        if save_visualization:
            output_dir = Path(output_dir) if output_dir else Path("./output")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            viz_path = output_dir / f"scene_{scene_token[:12]}_prediction.png"
            fig = self.visualizer.create_comprehensive_view(
                scene_data, 
                synchronized_trajectories, 
                time_window=time_window,
                save_path=viz_path
            )
        else:
            fig = self.visualizer.create_comprehensive_view(
                scene_data, 
                synchronized_trajectories, 
                time_window=time_window
            )
            viz_path = None
        
        # 7. Calculate metrics if ground truth available
        metrics = {}
        if "ground_truth" in synchronized_trajectories and "prediction" in synchronized_trajectories:
            gt_poses = synchronized_trajectories["ground_truth"]["poses"]
            pred_poses = synchronized_trajectories["prediction"]["poses"]
            metrics = self.visualizer._calculate_trajectory_metrics(gt_poses, pred_poses)
        
        processing_time = time.time() - start_time
        
        result = {
            "scene_token": scene_token,
            "scene_metadata": scene_data["metadata"],
            "trajectories": {
                "raw": all_trajectories,
                "synchronized": synchronized_trajectories
            },
            "prediction_result": prediction_result,
            "metrics": metrics,
            "visualization": {
                "figure": fig,
                "save_path": viz_path
            },
            "processing_time": processing_time
        }
        
        logger.info(f"Scene {scene_token} processed in {processing_time:.2f}s")
        if metrics:
            logger.info(f"Metrics - ADE: {metrics['ade']:.2f}m, FDE: {metrics['fde']:.2f}m")
        
        return result
    
    def create_trajectory_gif(
        self,
        scene_token: str,
        total_duration: float = 6.0,
        window_size: float = 3.0,
        step_size: float = 0.5,
        fps: float = 2.0,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Create GIF animation showing trajectory evolution over time
        
        Args:
            scene_token: Scene identifier
            total_duration: Total time duration to cover (seconds)
            window_size: Size of each time window (seconds)  
            step_size: Step between time windows (seconds)
            fps: Frames per second for GIF
            output_dir: Directory to save outputs
            
        Returns:
            Dictionary with GIF paths and metadata
        """
        logger.info(f"Creating trajectory GIF for scene {scene_token}")
        logger.info(f"Duration: {total_duration}s, Window: {window_size}s, Step: {step_size}s")
        
        start_time = time.time()
        
        # Set up output directory
        if output_dir is None:
            output_dir = Path("./trajectory_gifs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Load scene data once
        scene_data = self.data_manager.load_scene_data(scene_token)
        existing_trajectories = self.data_manager.get_all_trajectories(scene_token)
        
        # 2. Predict trajectory
        agent_input = scene_data["scene"].get_agent_input()
        prediction_result = self.inference_engine.predict_trajectory(
            agent_input, scene_data["scene"]
        )
        
        # 3. Synchronize all trajectories
        all_trajectories = self.data_manager.synchronize_trajectories({
            **existing_trajectories,
            "prediction": prediction_result["trajectory"]
        }, time_horizon=total_duration, dt=0.1)
        
        # 4. Generate time windows
        time_windows = []
        current_start = 0.0
        while current_start + window_size <= total_duration:
            time_windows.append((current_start, current_start + window_size))
            current_start += step_size
        
        logger.info(f"Generated {len(time_windows)} time windows")
        
        # 5. Create basic trajectory GIF
        basic_gif_path = self.visualizer.create_gif_visualization(
            scene_data=scene_data,
            all_trajectories=all_trajectories,
            time_windows=time_windows,
            save_path=output_dir / f"trajectory_{scene_token}",
            fps=fps
        )
        
        # 6. Collect results
        processing_time = time.time() - start_time
        
        result = {
            "scene_token": scene_token,
            "gif_path": basic_gif_path,
            "time_windows": time_windows,
            "total_frames": len(time_windows),
            "duration_seconds": total_duration,
            "window_size": window_size,
            "step_size": step_size,
            "fps": fps,
            "processing_time": processing_time,
            "file_size_mb": Path(basic_gif_path).stat().st_size / (1024 * 1024)
        }
        
        logger.info(f"Trajectory GIF created successfully in {processing_time:.2f}s")
        logger.info(f"GIF saved to: {basic_gif_path}")
        logger.info(f"File size: {result['file_size_mb']:.2f} MB")
        
        return result
    
    def create_sliding_window_gif(
        self,
        scene_token: str,
        sampling_rate: float = 2.0,      # 2Hz采样
        total_duration: float = 8.0,     # 总共8秒时间线
        prediction_horizon: float = 4.0, # 每次预测4秒
        show_history: bool = True,       # 显示历史预测
        history_fade_steps: int = 5,     # 历史轨迹保持5帧
        fps: float = 4.0,                # GIF 4fps播放
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Create sliding window trajectory GIF with time-annotated predictions
        
        Args:
            scene_token: Scene identifier
            sampling_rate: Sampling frequency in Hz (2.0 = every 0.5s)
            total_duration: Total timeline duration in seconds
            prediction_horizon: Prediction time horizon for each frame
            show_history: Whether to show faded historical predictions
            history_fade_steps: Number of historical frames to keep
            fps: GIF playback frame rate
            output_dir: Directory to save outputs
            
        Returns:
            Dictionary with GIF path and detailed metadata
        """
        logger.info(f"Creating sliding window GIF for scene {scene_token}")
        logger.info(f"Sampling: {sampling_rate}Hz, Duration: {total_duration}s, Prediction: {prediction_horizon}s")
        
        start_time = time.time()
        
        # Set up output directory
        if output_dir is None:
            output_dir = Path("./sliding_trajectory_gifs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Generate sampling timeline
        sampling_interval = 1.0 / sampling_rate  # 0.5s for 2Hz
        sampling_times = []
        current_time = 0.0
        while current_time <= total_duration:
            sampling_times.append(current_time)
            current_time += sampling_interval
            
        logger.info(f"Generated {len(sampling_times)} sampling points: {sampling_times[:5]}...{sampling_times[-5:]}")
        
        # 2. Load scene data once
        scene_data = self.data_manager.load_scene_data(scene_token)
        scene = scene_data["scene"]
        
        # 3. Generate predictions for each sampling time
        frame_predictions = []
        frame_metadata = []
        
        for i, sample_time in enumerate(sampling_times):
            logger.debug(f"Processing frame {i+1}/{len(sampling_times)} at t={sample_time:.1f}s")
            
            try:
                # Get frame data at this time
                frame_data = self._get_frame_at_time(scene, sample_time)
                if frame_data is None:
                    logger.warning(f"No frame data available at t={sample_time:.1f}s")
                    continue
                
                # Perform prediction for this time point
                agent_input = frame_data["agent_input"]
                prediction_result = self.inference_engine.predict_trajectory(
                    agent_input, scene
                )
                
                # Extract trajectory for the prediction horizon
                trajectory = prediction_result["trajectory"]
                
                frame_predictions.append({
                    "time": sample_time,
                    "frame_data": frame_data,
                    "prediction": trajectory,
                    "metadata": prediction_result.get("metadata", {})
                })
                
                frame_metadata.append({
                    "sample_time": sample_time,
                    "prediction_horizon": prediction_horizon,
                    "frame_index": i
                })
                
            except Exception as e:
                logger.error(f"Failed to process frame at t={sample_time:.1f}s: {e}")
                continue
        
        logger.info(f"Successfully processed {len(frame_predictions)} frames")
        
        # 4. Get reference trajectories (GT, PDM-Closed)
        reference_trajectories = self.data_manager.get_all_trajectories(scene_token)
        
        # 5. Create sliding window visualization
        gif_path = output_dir / f"sliding_trajectory_{scene_token}_{total_duration:.0f}s.gif"
        
        sliding_gif_path = self.visualizer.create_sliding_window_visualization(
            scene_data=scene_data,
            frame_predictions=frame_predictions,
            reference_trajectories=reference_trajectories,
            prediction_horizon=prediction_horizon,
            show_history=show_history,
            history_fade_steps=history_fade_steps,
            save_path=gif_path,
            fps=fps
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Sliding window GIF created in {processing_time:.2f}s: {sliding_gif_path}")
        
        return {
            "sliding_gif": str(sliding_gif_path),
            "metadata": {
                "scene_token": scene_token,
                "method": "sliding_window",
                "sampling_rate": sampling_rate,
                "sampling_interval": sampling_interval,
                "total_duration": total_duration,
                "prediction_horizon": prediction_horizon,
                "total_frames": len(frame_predictions),
                "actual_sampling_times": sampling_times,
                "show_history": show_history,
                "history_fade_steps": history_fade_steps,
                "fps": fps,
                "processing_time": processing_time,
                "file_size_mb": Path(sliding_gif_path).stat().st_size / (1024*1024) if Path(sliding_gif_path).exists() else 0
            }
        }
    
    def _get_frame_at_time(self, scene, target_time: float) -> Optional[Dict[str, Any]]:
        """
        Get frame data at a specific time point within the scene
        
        Args:
            scene: Scene object
            target_time: Target time in seconds
            
        Returns:
            Dictionary with frame data or None if not available
        """
        try:
            # Find the closest frame to target_time
            best_frame = None
            best_time_diff = float('inf')
            
            for frame in scene.frames:
                frame_time = frame.timestamp / 1e6  # Convert microseconds to seconds
                time_diff = abs(frame_time - target_time)
                
                if time_diff < best_time_diff:
                    best_time_diff = time_diff
                    best_frame = frame
            
            if best_frame is None:
                return None
            
            # Get agent input for this frame
            agent_input = best_frame.get_agent_input()
            
            return {
                "frame": best_frame,
                "agent_input": agent_input,
                "actual_time": best_frame.timestamp / 1e6,
                "time_diff": best_time_diff
            }
            
        except Exception as e:
            logger.error(f"Error getting frame at time {target_time}: {e}")
            return None

    def predict_batch_scenes(
        self, 
        scene_tokens: List[str], 
        time_window: Tuple[float, float] = (0, 3.0),
        output_dir: Optional[Path] = None,
        max_scenes: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Predict trajectories for multiple scenes
        
        Args:
            scene_tokens: List of scene tokens to process
            time_window: Time window for visualization
            output_dir: Output directory for results
            max_scenes: Maximum number of scenes to process
            
        Returns:
            List of prediction results
        """
        if max_scenes:
            scene_tokens = scene_tokens[:max_scenes]
            
        logger.info(f"Processing {len(scene_tokens)} scenes...")
        
        output_dir = Path(output_dir) if output_dir else Path("./output/batch")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        failed_scenes = []
        
        for i, scene_token in enumerate(scene_tokens):
            try:
                logger.info(f"Processing scene {i+1}/{len(scene_tokens)}: {scene_token}")
                
                result = self.predict_single_scene(
                    scene_token,
                    time_window=time_window,
                    save_visualization=True,
                    output_dir=output_dir
                )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to process scene {scene_token}: {e}")
                failed_scenes.append({"token": scene_token, "error": str(e)})
        
        # Create summary
        summary = self._create_batch_summary(results, failed_scenes, output_dir)
        
        logger.info(f"Batch processing complete!")
        logger.info(f"Successful: {len(results)}, Failed: {len(failed_scenes)}")
        logger.info(f"Results saved to: {output_dir}")
        
        return results
    
    def _create_batch_summary(
        self, 
        results: List[Dict[str, Any]], 
        failed_scenes: List[Dict[str, str]], 
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Create summary of batch processing results
        """
        if not results:
            return {}
        
        # Calculate aggregate metrics
        all_ades = [r["metrics"]["ade"] for r in results if r["metrics"]]
        all_fdes = [r["metrics"]["fde"] for r in results if r["metrics"]]
        processing_times = [r["processing_time"] for r in results]
        
        summary = {
            "total_scenes": len(results) + len(failed_scenes),
            "successful_scenes": len(results),
            "failed_scenes": len(failed_scenes),
            "success_rate": len(results) / (len(results) + len(failed_scenes)) * 100,
            "aggregate_metrics": {
                "mean_ade": sum(all_ades) / len(all_ades) if all_ades else 0,
                "mean_fde": sum(all_fdes) / len(all_fdes) if all_fdes else 0,
                "mean_processing_time": sum(processing_times) / len(processing_times)
            },
            "scenario_breakdown": {}
        }
        
        # Breakdown by map location (more meaningful than scenario_type which is always "unknown")
        for result in results:
            map_name = result["scene_metadata"].get("map_name", "unknown_map")
            if map_name not in summary["scenario_breakdown"]:
                summary["scenario_breakdown"][map_name] = {
                    "count": 0,
                    "ades": [],
                    "fdes": []
                }
            
            summary["scenario_breakdown"][map_name]["count"] += 1
            if result["metrics"]:
                summary["scenario_breakdown"][map_name]["ades"].append(result["metrics"]["ade"])
                summary["scenario_breakdown"][map_name]["fdes"].append(result["metrics"]["fde"])
        
        # Calculate location-specific metrics
        for map_name, data in summary["scenario_breakdown"].items():
            if data["ades"]:
                data["mean_ade"] = sum(data["ades"]) / len(data["ades"])
                data["mean_fde"] = sum(data["fdes"]) / len(data["fdes"])
            else:
                data["mean_ade"] = 0
                data["mean_fde"] = 0
            # Remove raw lists to keep summary clean
            del data["ades"]
            del data["fdes"]
        
        # Save summary to file
        summary_path = output_dir / "batch_summary.yaml"
        with open(summary_path, 'w') as f:
            yaml.dump(summary, f, default_flow_style=False, indent=2)
        
        logger.info(f"Batch summary saved to: {summary_path}")
        return summary
    
    def get_random_scenes(self, num_scenes: int = 5) -> List[str]:
        """
        Get random scene tokens for testing
        
        Args:
            num_scenes: Number of random scenes to return
            
        Returns:
            List of scene tokens
        """
        available_scenes = self.data_manager.get_available_scenes()
        
        if len(available_scenes) < num_scenes:
            logger.warning(f"Requested {num_scenes} scenes but only {len(available_scenes)} available")
            num_scenes = len(available_scenes)
        
        import random
        return random.sample(available_scenes, num_scenes)
    
    def get_app_info(self) -> Dict[str, Any]:
        """
        Get information about the application state
        
        Returns:
            Dictionary with application information
        """
        model_info = self.inference_engine.get_model_info()
        data_stats = self.data_manager.get_scene_statistics()
        
        # Get available scenes
        available_scenes = self.data_manager.scene_loader.tokens if self.data_manager.scene_loader else []
        
        # Create standardized data info
        data_info = {
            "total_scenes": data_stats.get("total_scenes", 0),
            "num_scenes": data_stats.get("total_scenes", 0),  # Alias for compatibility
            "available_scenes": available_scenes,
            "sample_size": data_stats.get("sample_size", 0),
            "map_locations": data_stats.get("map_locations", []),
            "num_map_locations": data_stats.get("num_map_locations", 0),
            "log_names": data_stats.get("log_names", []),
            "num_logs": data_stats.get("num_logs", 0),
            "has_metric_cache": data_stats.get("has_metric_cache", False),
            "metric_cache_scenes": data_stats.get("metric_cache_scenes", 0)
        }
        
        return {
            "model": model_info,
            "data": data_info,
            "config": {
                "model_type": self.config["model"]["type"],
                "data_split": Path(self.config["data"]["navsim_log_path"]).name,
                "has_checkpoint": self.config["model"].get("checkpoint_path") is not None
            },
            "status": "ready"
        }
    
    def create_demo_visualization(
        self, 
        num_scenes: int = 3, 
        time_windows: List[Tuple[float, float]] = None,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Create demo visualizations for showcase
        
        Args:
            num_scenes: Number of demo scenes
            time_windows: List of time windows to demonstrate
            output_dir: Output directory
            
        Returns:
            Demo results summary
        """
        if time_windows is None:
            time_windows = [(0, 1.5), (0, 3.0), (0, 6.0)]
        
        output_dir = Path(output_dir) if output_dir else Path("./demo")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get diverse scenes
        random_scenes = self.get_random_scenes(num_scenes)
        
        demo_results = []
        
        for i, scene_token in enumerate(random_scenes):
            logger.info(f"Creating demo {i+1}/{len(random_scenes)}: {scene_token}")
            
            for j, time_window in enumerate(time_windows):
                try:
                    result = self.predict_single_scene(
                        scene_token,
                        time_window=time_window,
                        save_visualization=True,
                        output_dir=output_dir / f"scene_{i+1}"
                    )
                    
                    # Rename file to include time window info
                    if result["visualization"]["save_path"]:
                        old_path = result["visualization"]["save_path"]
                        new_path = old_path.parent / f"{old_path.stem}_t{time_window[1]:.1f}s{old_path.suffix}"
                        old_path.rename(new_path)
                        result["visualization"]["save_path"] = new_path
                    
                    demo_results.append({
                        "scene_index": i+1,
                        "scene_token": scene_token,
                        "time_window": time_window,
                        "result": result
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to create demo for scene {scene_token}, time window {time_window}: {e}")
        
        logger.info(f"Demo complete! Created {len(demo_results)} visualizations in {output_dir}")
        return {"results": demo_results, "output_dir": output_dir} 