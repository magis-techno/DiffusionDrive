"""
Trajectory Visualizer

This module provides comprehensive trajectory visualization capabilities including 
BEV views and camera projections.
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, Any, List, Optional, Tuple
import cv2
from pathlib import Path
import torch

# Import NavSim visualization components
from navsim.visualization.plots import plot_bev_frame, configure_bev_ax
from navsim.visualization.bev import add_trajectory_to_bev_ax, add_configured_bev_on_ax
from navsim.visualization.config import TRAJECTORY_CONFIG

logger = logging.getLogger(__name__)


class TrajectoryVisualizer:
    """
    Comprehensive trajectory visualization system
    """
    
    def __init__(self, viz_config: Dict[str, Any] = None):
        """
        Initialize visualizer
        
        Args:
            viz_config: Visualization configuration dictionary
        """
        self.config = viz_config or {}
        
        # Define trajectory styles
        self.trajectory_styles = {
            "prediction": {
                "color": "#DC143C", 
                "style": "-", 
                "width": 3, 
                "alpha": 0.8,
                "label": "Model Prediction",
                "marker": "o",
                "marker_size": 4
            },
            "ground_truth": {
                "color": "#2E8B57", 
                "style": "-", 
                "width": 3, 
                "alpha": 0.9,
                "label": "Ground Truth",
                "marker": "s", 
                "marker_size": 4
            },
            "pdm_closed": {
                "color": "#4169E1", 
                "style": "--", 
                "width": 2, 
                "alpha": 0.7,
                "label": "PDM-Closed",
                "marker": "^",
                "marker_size": 3
            }
        }
        
        # Update styles with user config
        if "trajectory_styles" in self.config:
            for name, style in self.config["trajectory_styles"].items():
                if name in self.trajectory_styles:
                    self.trajectory_styles[name].update(style)
        
        logger.info("Trajectory visualizer initialized")
    
    def create_comprehensive_view(
        self, 
        scene_data: Dict[str, Any], 
        all_trajectories: Dict[str, Any],
        time_window: Tuple[float, float] = (0, 3.0),
        save_path: Optional[Path] = None
    ) -> plt.Figure:
        """
        Create comprehensive visualization with BEV and camera views
        
        Args:
            scene_data: Scene data dictionary
            all_trajectories: Dictionary of synchronized trajectories
            time_window: Time window to display (start, end) in seconds
            save_path: Optional path to save the figure
            
        Returns:
            matplotlib Figure object
        """
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 12))
        
        # 1. BEV trajectory view (large, left side)
        ax_bev = plt.subplot(2, 3, (1, 4))
        self._render_bev_trajectories(ax_bev, scene_data, all_trajectories, time_window)
        
        # 2. Front camera view with trajectory projections (top right)
        ax_camera = plt.subplot(2, 3, 2)
        self._render_camera_view(ax_camera, scene_data, all_trajectories, time_window)
        
        # 3. Trajectory comparison plot (middle right)
        ax_comparison = plt.subplot(2, 3, 5)
        self._render_trajectory_comparison(ax_comparison, all_trajectories, time_window)
        
        # 4. Statistics panel (bottom right)
        ax_stats = plt.subplot(2, 3, (3, 6))
        self._render_statistics_panel(ax_stats, scene_data, all_trajectories)
        
        # Add main title
        fig.suptitle(
            f"Trajectory Analysis - {scene_data['metadata']['scenario_type']}\n"
            f"Scene: {scene_data['metadata']['token'][:12]}... | "
            f"Time Window: {time_window[0]:.1f}s - {time_window[1]:.1f}s",
            fontsize=16, fontweight='bold'
        )
        
        plt.tight_layout()
        
        # Save if requested
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved visualization to: {save_path}")
        
        return fig
    
    def create_gif_visualization(
        self,
        scene_data: Dict[str, Any],
        all_trajectories: Dict[str, Any],
        time_windows: List[Tuple[float, float]],
        save_path: Path,
        fps: float = 2.0,
        include_features: Dict[str, bool] = None
    ) -> str:
        """
        Create GIF animation of trajectory visualization across multiple time windows
        
        Args:
            scene_data: Scene data dictionary
            all_trajectories: Dictionary of synchronized trajectories
            time_windows: List of (start, end) time windows for animation frames
            save_path: Path to save the GIF file
            fps: Frames per second for the animation
            include_features: Dict controlling which features to visualize
                {"bev_semantic": True, "attention": True, "diffusion_steps": False}
            
        Returns:
            Path to the created GIF file
        """
        logger.info(f"Creating GIF visualization with {len(time_windows)} frames")
        
        # Default feature inclusion
        if include_features is None:
            include_features = {
                "bev_semantic": False,
                "attention": False, 
                "diffusion_steps": False,
                "multi_scale": False
            }
        
        frames = []
        
        for i, time_window in enumerate(time_windows):
            logger.debug(f"Generating frame {i+1}/{len(time_windows)} for time window {time_window}")
            
            # Create the comprehensive view for this time window
            fig = self.create_comprehensive_view(
                scene_data, all_trajectories, time_window
            )
            
            # Add timestamp overlay
            time_start, time_end = time_window
            fig.suptitle(f"Time Window: {time_start:.1f}s - {time_end:.1f}s", 
                        fontsize=16, fontweight='bold', y=0.95)
            
            # Convert matplotlib figure to PIL Image
            import io
            from PIL import Image
            
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            
            # 重要：复制图像数据到内存，避免BytesIO关闭后的问题
            img = Image.open(buf).copy()  # .copy() 确保图像数据独立存储
            frames.append(img)
            
            plt.close(fig)  # Free memory
            buf.close()  # 现在可以安全关闭缓冲区
        
        # Create GIF
        duration = int(1000 / fps)  # Duration per frame in milliseconds
        
        # Save as GIF
        gif_path = save_path.with_suffix('.gif')
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,  # Infinite loop
            optimize=True
        )
        
        logger.info(f"GIF saved to {gif_path}")
        logger.info(f"GIF specs: {len(frames)} frames, {fps} fps, {duration}ms per frame")
        
        return str(gif_path)
    
    def create_feature_visualization_gif(
        self,
        scene_data: Dict[str, Any],
        model_features: Dict[str, torch.Tensor],
        time_windows: List[Tuple[float, float]],
        feature_type: str,
        save_path: Path,
        fps: float = 1.0
    ) -> str:
        """
        Create GIF for specific model feature visualization
        
        Args:
            scene_data: Scene data dictionary
            model_features: Dictionary of extracted model features
            time_windows: List of time windows
            feature_type: Type of feature ("bev_semantic", "attention", "diffusion", etc.)
            save_path: Path to save the GIF
            fps: Frames per second
            
        Returns:
            Path to the created GIF file
        """
        logger.info(f"Creating {feature_type} feature GIF with {len(time_windows)} frames")
        
        frames = []
        
        for i, time_window in enumerate(time_windows):
            logger.debug(f"Generating {feature_type} frame {i+1}/{len(time_windows)}")
            
            # Create feature-specific visualization (placeholder implementations)
            fig = plt.figure(figsize=(15, 10))
            
            if feature_type == "bev_semantic":
                fig.suptitle(f"BEV Semantic Features: {time_window[0]:.1f}s - {time_window[1]:.1f}s", fontsize=14)
                # TODO: Implement BEV semantic visualization
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, f"BEV Semantic\nFrame {i+1}\n(Coming Soon)", 
                       ha='center', va='center', transform=ax.transAxes, fontsize=16)
                
            elif feature_type == "attention":
                fig.suptitle(f"Attention Maps: {time_window[0]:.1f}s - {time_window[1]:.1f}s", fontsize=14)
                # TODO: Implement attention visualization
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, f"Attention Maps\nFrame {i+1}\n(Coming Soon)", 
                       ha='center', va='center', transform=ax.transAxes, fontsize=16)
                
            elif feature_type == "diffusion":
                fig.suptitle(f"Diffusion Process: {time_window[0]:.1f}s - {time_window[1]:.1f}s", fontsize=14)
                # TODO: Implement diffusion visualization
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, f"Diffusion Process\nFrame {i+1}\n(Coming Soon)", 
                       ha='center', va='center', transform=ax.transAxes, fontsize=16)
                
            elif feature_type == "multi_scale":
                fig.suptitle(f"Multi-Scale Features: {time_window[0]:.1f}s - {time_window[1]:.1f}s", fontsize=14)
                # TODO: Implement multi-scale visualization
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, f"Multi-Scale\nFrame {i+1}\n(Coming Soon)", 
                       ha='center', va='center', transform=ax.transAxes, fontsize=16)
                
            else:
                raise ValueError(f"Unknown feature type: {feature_type}")
            
            # Convert to PIL Image
            import io
            from PIL import Image
            
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            
            # 重要：复制图像数据到内存，避免BytesIO关闭后的问题
            img = Image.open(buf).copy()  # .copy() 确保图像数据独立存储
            frames.append(img)
            
            plt.close(fig)
            buf.close()  # 现在可以安全关闭缓冲区
        
        # Save GIF
        duration = int(1000 / fps)
        gif_path = save_path.with_suffix(f'_{feature_type}.gif')
        
        if frames:
            frames[0].save(
                gif_path,
                save_all=True,
                append_images=frames[1:],
                duration=duration,
                loop=0,
                optimize=True
            )
        
        logger.info(f"{feature_type.upper()} GIF saved to {gif_path}")
        return str(gif_path)
    
    def create_sliding_window_visualization(
        self,
        scene_data: Dict[str, Any],
        frame_predictions: List[Dict[str, Any]],
        reference_trajectories: Dict[str, Any],
        prediction_horizon: float = 4.0,
        show_history: bool = True,
        history_fade_steps: int = 5,
        save_path: Path = None,
        fps: float = 4.0
    ) -> str:
        """
        Create sliding window GIF with time-annotated trajectory predictions
        
        Args:
            scene_data: Scene data dictionary
            frame_predictions: List of frame-by-frame predictions
            reference_trajectories: Reference trajectories (GT, PDM-Closed)
            prediction_horizon: Prediction time horizon in seconds
            show_history: Whether to show faded historical predictions
            history_fade_steps: Number of historical frames to keep
            save_path: Path to save the GIF file
            fps: Frames per second for the animation
            
        Returns:
            Path to the created GIF file
        """
        logger.info(f"Creating sliding window visualization with {len(frame_predictions)} frames")
        
        frames = []
        
        for frame_idx, frame_pred in enumerate(frame_predictions):
            logger.debug(f"Generating sliding window frame {frame_idx+1}/{len(frame_predictions)}")
            
            # Create figure for this frame
            fig = self._create_sliding_window_frame(
                scene_data=scene_data,
                current_prediction=frame_pred,
                reference_trajectories=reference_trajectories,
                frame_idx=frame_idx,
                total_frames=len(frame_predictions),
                history_predictions=frame_predictions[:frame_idx] if show_history else [],
                prediction_horizon=prediction_horizon,
                history_fade_steps=history_fade_steps
            )
            
            # Convert to PIL Image
            import io
            from PIL import Image
            
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
            buf.seek(0)
            
            # 重要：复制图像数据到内存，避免BytesIO关闭后的问题
            img = Image.open(buf).copy()
            frames.append(img)
            
            plt.close(fig)
            buf.close()
        
        # Create GIF
        duration = int(1000 / fps)  # Duration per frame in milliseconds
        
        # Save as GIF
        gif_path = save_path.with_suffix('.gif')
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,  # Infinite loop
            optimize=True
        )
        
        logger.info(f"Sliding window GIF saved to {gif_path}")
        logger.info(f"GIF specs: {len(frames)} frames, {fps} fps, {duration}ms per frame")
        
        return str(gif_path)
    
    def _create_sliding_window_frame(
        self,
        scene_data: Dict[str, Any],
        current_prediction: Dict[str, Any],
        reference_trajectories: Dict[str, Any],
        frame_idx: int,
        total_frames: int,
        history_predictions: List[Dict[str, Any]],
        prediction_horizon: float,
        history_fade_steps: int
    ) -> plt.Figure:
        """
        Create a single frame for sliding window visualization
        """
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Current frame data and prediction
        current_time = current_prediction["time"]
        current_trajectory = current_prediction["prediction"]
        current_frame_data = current_prediction["frame_data"]
        
        # === BEV View (top-left) ===
        bev_ax = axes[0, 0]
        self._render_sliding_bev_view(
            bev_ax, scene_data, current_frame_data, current_trajectory,
            reference_trajectories, history_predictions, 
            current_time, prediction_horizon, history_fade_steps
        )
        
        # === Front Camera View (top-right) ===
        camera_ax = axes[0, 1]
        self._render_sliding_camera_view(
            camera_ax, current_frame_data, current_trajectory,
            current_time, prediction_horizon
        )
        
        # === Trajectory Comparison (bottom-left) ===
        traj_ax = axes[1, 0]
        self._render_trajectory_comparison_view(
            traj_ax, current_trajectory, reference_trajectories,
            current_time, prediction_horizon
        )
        
        # === Status and Metadata (bottom-right) ===
        status_ax = axes[1, 1]
        self._render_status_panel(
            status_ax, current_prediction, frame_idx, total_frames,
            current_time, prediction_horizon
        )
        
        # Add main title
        fig.suptitle(
            f"Sliding Window Trajectory Prediction - Frame {frame_idx+1}/{total_frames}\n"
            f"⏰ t={current_time:.1f}s | 🎯 Prediction: {current_time:.1f}s → {current_time+prediction_horizon:.1f}s",
            fontsize=16, fontweight='bold', y=0.95
        )
        
        plt.tight_layout()
        return fig
    
    def _render_sliding_bev_view(
        self, ax, scene_data, current_frame_data, current_trajectory,
        reference_trajectories, history_predictions, current_time, 
        prediction_horizon, history_fade_steps
    ):
        """Render BEV view with time-annotated trajectories"""
        from navsim.visualization.plots import configure_bev_ax
        from navsim.visualization.bev import add_configured_bev_on_ax
        
        # Configure BEV axes
        configure_bev_ax(ax, 100)  # 100m range
        
        # Add BEV base layers
        current_frame = current_frame_data["frame"]
        add_configured_bev_on_ax(
            ax, 
            current_frame.ego_status.ego_pose,
            scene_data["map"]["api"],
            scene_data["sensors"]["lidar"][0] if scene_data["sensors"]["lidar"] else None
        )
        
        # === Render reference trajectories ===
        if "gt" in reference_trajectories:
            self._add_reference_trajectory_to_bev(ax, reference_trajectories["gt"], "GT", "green", "--")
        
        if "pdm" in reference_trajectories:
            self._add_reference_trajectory_to_bev(ax, reference_trajectories["pdm"], "PDM-Closed", "blue", "-.")
        
        # === Render historical predictions (faded) ===
        if history_predictions:
            self._add_history_trajectories_to_bev(
                ax, history_predictions, history_fade_steps
            )
        
        # === Render current prediction with time annotations ===
        self._add_time_annotated_trajectory_to_bev(
            ax, current_trajectory, current_time, prediction_horizon
        )
        
        ax.set_title(f"BEV View - Time Annotated Trajectories", fontweight='bold')
        ax.legend(loc='upper right', fontsize=8)
    
    def _add_time_annotated_trajectory_to_bev(
        self, ax, trajectory, current_time, prediction_horizon
    ):
        """Add trajectory with time markers and gradient colors"""
        import numpy as np
        from matplotlib.colors import LinearSegmentedColormap
        
        # Extract trajectory poses
        poses = np.array([[state.pose.x, state.pose.y] for state in trajectory.trajectory_states])
        
        if len(poses) < 2:
            return
        
        # 坐标系修复：NavSim BEV uses (Y, X) mapping
        x_coords = poses[:, 1]  # Y coordinates go to matplotlib X
        y_coords = poses[:, 0]  # X coordinates go to matplotlib Y
        
        # Create gradient colors (red -> orange -> yellow -> green -> blue)
        n_points = len(poses)
        colors = self._generate_trajectory_gradient_colors(n_points)
        
        # Plot trajectory segments with gradient colors
        for i in range(len(poses) - 1):
            ax.plot(
                [x_coords[i], x_coords[i+1]], 
                [y_coords[i], y_coords[i+1]],
                color=colors[i], linewidth=3, alpha=0.9, label='Current Prediction' if i == 0 else ""
            )
        
        # Add time markers
        self._add_time_markers_to_trajectory(
            ax, x_coords, y_coords, prediction_horizon
        )
    
    def _generate_trajectory_gradient_colors(self, n_points):
        """Generate gradient colors for trajectory visualization"""
        import numpy as np
        
        # Define color stops: red -> orange -> yellow -> green -> blue
        color_stops = [
            (1.0, 0.0, 0.0),    # Red
            (1.0, 0.5, 0.0),    # Orange  
            (1.0, 1.0, 0.0),    # Yellow
            (0.5, 1.0, 0.0),    # Green
            (0.0, 1.0, 1.0)     # Cyan/Blue
        ]
        
        colors = []
        for i in range(n_points):
            # Interpolate position along the color gradient
            t = i / max(1, n_points - 1)
            
            # Find which color segment we're in
            segment_size = 1.0 / (len(color_stops) - 1)
            segment_idx = min(int(t / segment_size), len(color_stops) - 2)
            local_t = (t - segment_idx * segment_size) / segment_size
            
            # Interpolate between color stops
            color1 = np.array(color_stops[segment_idx])
            color2 = np.array(color_stops[segment_idx + 1])
            color = color1 * (1 - local_t) + color2 * local_t
            
            colors.append(tuple(color))
        
        return colors
    
    def _add_time_markers_to_trajectory(self, ax, x_coords, y_coords, prediction_horizon):
        """Add time markers along the trajectory"""
        import numpy as np
        
        # Calculate time markers (every 1 second)
        time_intervals = [1.0, 2.0, 3.0, 4.0]
        
        # Marker styles for different time points
        marker_styles = {
            1.0: {"marker": "o", "size": 80, "color": "yellow", "text": "1s"},
            2.0: {"marker": "s", "size": 100, "color": "orange", "text": "2s"},
            3.0: {"marker": "D", "size": 120, "color": "red", "text": "3s"},
            4.0: {"marker": "*", "size": 150, "color": "purple", "text": "4s"}
        }
        
        n_points = len(x_coords)
        total_time = prediction_horizon
        
        for time_mark in time_intervals:
            if time_mark <= total_time:
                # Find approximate position along trajectory
                time_ratio = time_mark / total_time
                point_idx = min(int(time_ratio * (n_points - 1)), n_points - 1)
                
                if point_idx < len(x_coords):
                    style = marker_styles[time_mark]
                    
                    # Add marker
                    ax.scatter(
                        x_coords[point_idx], y_coords[point_idx],
                        marker=style["marker"], s=style["size"],
                        c=style["color"], edgecolors='black', linewidth=2,
                        zorder=10, alpha=0.9
                    )
                    
                    # Add text annotation
                    ax.annotate(
                        style["text"],
                        (x_coords[point_idx], y_coords[point_idx]),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=10, fontweight='bold',
                        bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8)
                                         )
    
    def _add_history_trajectories_to_bev(self, ax, history_predictions, history_fade_steps):
        """Add faded historical trajectory predictions"""
        import numpy as np
        
        for i, hist_pred in enumerate(history_predictions[-history_fade_steps:]):
            # Calculate fade amount (more recent = less faded)
            fade_factor = (i + 1) / history_fade_steps
            alpha = 0.15 + 0.55 * fade_factor  # 0.15 to 0.7 alpha
            
            hist_trajectory = hist_pred["prediction"]
            hist_poses = np.array([[state.pose.x, state.pose.y] for state in hist_trajectory.trajectory_states])
            
            if len(hist_poses) < 2:
                continue
            
            # 坐标系修复：NavSim BEV uses (Y, X) mapping
            x_coords = hist_poses[:, 1]
            y_coords = hist_poses[:, 0]
            
            # Plot faded trajectory
            ax.plot(
                x_coords, y_coords, 
                color='gray', linewidth=2, alpha=alpha, linestyle='--',
                label=f'History-{len(history_predictions)-i}' if i == 0 else ""
            )
    
    def _add_reference_trajectory_to_bev(self, ax, trajectory, label, color, linestyle):
        """Add reference trajectory to BEV view"""
        import numpy as np
        
        poses = np.array([[state.pose.x, state.pose.y] for state in trajectory.trajectory_states])
        
        if len(poses) < 2:
            return
        
        # 坐标系修复：NavSim BEV uses (Y, X) mapping
        x_coords = poses[:, 1]
        y_coords = poses[:, 0]
        
        ax.plot(x_coords, y_coords, color=color, linewidth=2, 
                linestyle=linestyle, label=label, alpha=0.8)
    
    def _render_sliding_camera_view(self, ax, current_frame_data, current_trajectory, current_time, prediction_horizon):
        """Render front camera view with projected trajectory"""
        current_frame = current_frame_data["frame"]
        
        # Get front camera image
        front_cameras = [sensor for sensor in current_frame.sensors if 'FRONT' in sensor.sensor_name]
        
        if front_cameras:
            camera_data = front_cameras[0]
            image_data = camera_data.camera
            
            # Display image
            ax.imshow(image_data.data)
            
            # Project trajectory onto camera image
            self._add_trajectory_projections_to_image(
                ax, current_trajectory, current_frame, camera_data,
                current_time, prediction_horizon
            )
            
            ax.set_title(f"Front Camera - Trajectory Projection", fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'No Front Camera Available', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title("Front Camera View", fontweight='bold')
        
        ax.axis('off')
    
    def _render_trajectory_comparison_view(self, ax, current_trajectory, reference_trajectories, current_time, prediction_horizon):
        """Render trajectory comparison in local coordinates"""
        import numpy as np
        
        # Current prediction
        current_poses = np.array([[state.pose.x, state.pose.y] for state in current_trajectory.trajectory_states])
        
        if len(current_poses) > 0:
            ax.plot(current_poses[:, 0], current_poses[:, 1], 'r-', linewidth=3, label='Current Prediction')
        
        # Reference trajectories
        if "gt" in reference_trajectories:
            gt_poses = np.array([[state.pose.x, state.pose.y] for state in reference_trajectories["gt"].trajectory_states])
            if len(gt_poses) > 0:
                ax.plot(gt_poses[:, 0], gt_poses[:, 1], 'g--', linewidth=2, label='Ground Truth')
        
        if "pdm" in reference_trajectories:
            pdm_poses = np.array([[state.pose.x, state.pose.y] for state in reference_trajectories["pdm"].trajectory_states])
            if len(pdm_poses) > 0:
                ax.plot(pdm_poses[:, 0], pdm_poses[:, 1], 'b-.', linewidth=2, label='PDM-Closed')
        
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_title('Trajectory Comparison View', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
    
    def _render_status_panel(self, ax, current_prediction, frame_idx, total_frames, current_time, prediction_horizon):
        """Render status and metadata panel"""
        ax.axis('off')
        
        # Status information
        status_text = [
            f"📊 Frame Status",
            f"  • Frame: {frame_idx + 1} / {total_frames}",
            f"  • Current Time: {current_time:.1f}s",
            f"  • Prediction Window: {current_time:.1f}s → {current_time + prediction_horizon:.1f}s",
            f"  • Horizon: {prediction_horizon:.1f}s",
            "",
            f"🎯 Trajectory Info",
            f"  • Points: {len(current_prediction['prediction'].trajectory_states)}",
            f"  • Time Diff: {current_prediction['frame_data']['time_diff']:.3f}s",
            f"  • Actual Time: {current_prediction['frame_data']['actual_time']:.1f}s",
            "",
            f"🎨 Visualization Legend",
            f"  🔴 Red → Orange: 0-1s",
            f"  🟠 Orange → Yellow: 1-2s", 
            f"  🟡 Yellow → Green: 2-3s",
            f"  🟢 Green → Blue: 3-4s",
            "",
            f"🏷️ Time Markers",
            f"  ⚫ 1s   🔲 2s   ◆ 3s   ⭐ 4s"
        ]
        
        for i, line in enumerate(status_text):
            ax.text(0.05, 0.95 - i * 0.05, line, transform=ax.transAxes, 
                   fontsize=10, verticalalignment='top',
                   fontweight='bold' if line.startswith(('📊', '🎯', '🎨', '🏷️')) else 'normal')
        
        ax.set_title('Status & Info Panel', fontweight='bold')

    def _render_bev_trajectories(
        self, 
        ax: plt.Axes, 
        scene_data: Dict[str, Any], 
        trajectories: Dict[str, Any],
        time_window: Tuple[float, float]
    ):
        """
        Render BEV view with multiple trajectories
        """
        scene = scene_data["scene"]
        frame_idx = scene.scene_metadata.num_history_frames - 1
        
        # Create base BEV plot
        add_configured_bev_on_ax(ax, scene.map_api, scene.frames[frame_idx])
        
        # Filter trajectories by time window
        time_start, time_end = time_window
        
        # Render each trajectory
        for traj_name, traj_data in trajectories.items():
            if traj_name not in self.trajectory_styles:
                continue
                
            poses = traj_data["poses"]
            timestamps = traj_data["timestamps"]
            
            # Filter by time window
            time_mask = (timestamps >= time_start) & (timestamps <= time_end)
            if not np.any(time_mask):
                continue
                
            filtered_poses = poses[time_mask]
            filtered_times = timestamps[time_mask]
            
            # Plot trajectory with time-based alpha
            style = self.trajectory_styles[traj_name]
            
            # Create trajectory line with varying alpha
            for i in range(len(filtered_poses) - 1):
                # Calculate alpha based on time (farther in future = more transparent)
                time_progress = (filtered_times[i] - time_start) / (time_end - time_start)
                alpha = style["alpha"] * (1.0 - 0.3 * time_progress)  # Fade to 70% of original
                
                # 🔥 坐标系修复：NavSim BEV uses (Y, X) mapping
                # X forward (vehicle direction) → matplotlib Y axis
                # Y sideways (vehicle left) → matplotlib X axis  
                ax.plot(
                    filtered_poses[i:i+2, 1],  # 轨迹 Y → matplotlib X
                    filtered_poses[i:i+2, 0],  # 轨迹 X → matplotlib Y
                    color=style["color"],
                    linestyle=style["style"],
                    linewidth=style["width"],
                    alpha=alpha
                )
            
            # Add markers at key points
            marker_indices = np.linspace(0, len(filtered_poses)-1, 
                                       min(5, len(filtered_poses)), dtype=int)
            for idx in marker_indices:
                ax.scatter(
                    filtered_poses[idx, 1],  # 轨迹 Y → matplotlib X
                    filtered_poses[idx, 0],  # 轨迹 X → matplotlib Y
                    c=style["color"],
                    marker=style["marker"],
                    s=style["marker_size"]**2,
                    alpha=style["alpha"],
                    edgecolors='white',
                    linewidth=0.5
                )
        
        # Configure BEV view
        configure_bev_ax(ax)
        
        # Add legend
        legend_elements = []
        for traj_name, style in self.trajectory_styles.items():
            if traj_name in trajectories:
                legend_elements.append(
                    plt.Line2D([0], [0], color=style["color"], 
                             linestyle=style["style"], linewidth=style["width"],
                             label=style["label"])
                )
        
        if legend_elements:
            ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
        
        ax.set_title("Bird's Eye View - Trajectory Comparison", fontsize=14, fontweight='bold')
    
    def _add_trajectory_projections_to_image(
        self,
        image: np.ndarray,
        camera,
        trajectories: Dict[str, Any],
        time_window: Tuple[float, float]
    ) -> np.ndarray:
        """
        Project trajectories onto camera image
        
        Args:
            image: Camera image array
            camera: Camera object with intrinsics and extrinsics
            trajectories: Dictionary of trajectory data
            time_window: Time window to display
            
        Returns:
            Image with trajectory projections drawn
        """
        # Import projection function from NavSim
        from navsim.visualization.camera import _transform_points_to_image
        
        time_start, time_end = time_window
        image_height, image_width = image.shape[:2]
        
        for traj_name, traj_data in trajectories.items():
            if traj_name not in self.trajectory_styles:
                continue
                
            poses = traj_data["poses"]
            timestamps = traj_data["timestamps"]
            
            # Filter by time window
            time_mask = (timestamps >= time_start) & (timestamps <= time_end)
            if not np.any(time_mask):
                continue
                
            filtered_poses = poses[time_mask]
            filtered_times = timestamps[time_mask]
            
            if len(filtered_poses) == 0:
                continue
            
            # Convert 2D poses to 3D points (assume height = 0 for ground level)
            # Trajectory poses are relative to ego vehicle
            trajectory_3d = np.zeros((len(filtered_poses), 3))
            trajectory_3d[:, :2] = filtered_poses[:, :2]  # X, Y from poses
            trajectory_3d[:, 2] = 0.0  # Ground level
            
            try:
                # Transform trajectory points from ego frame to camera frame
                # Use camera's transformation matrices
                trajectory_3d_camera = self._transform_trajectory_to_camera_frame(
                    trajectory_3d, camera
                )
                
                # Project 3D points to 2D image coordinates
                projected_points, in_fov_mask = _transform_points_to_image(
                    trajectory_3d_camera,
                    camera.intrinsics,
                    image_shape=(image_height, image_width)
                )
                
                # Filter points that are in field of view
                valid_points = projected_points[in_fov_mask]
                valid_times = filtered_times[in_fov_mask]
                
                if len(valid_points) > 1:
                    # Draw trajectory on image
                    style = self.trajectory_styles[traj_name]
                    color_bgr = self._hex_to_bgr(style["color"])
                    
                    # Draw connected line segments
                    for i in range(len(valid_points) - 1):
                        # Calculate alpha based on time (fade future points)
                        time_progress = (valid_times[i] - time_start) / (time_end - time_start)
                        alpha = max(0.3, 1.0 - 0.5 * time_progress)
                        
                        pt1 = tuple(map(int, valid_points[i]))
                        pt2 = tuple(map(int, valid_points[i + 1]))
                        
                        # Draw line with varying thickness based on alpha
                        thickness = max(1, int(style["width"] * alpha))
                        cv2.line(image, pt1, pt2, color_bgr, thickness)
                    
                    # Draw markers at key points
                    marker_indices = np.linspace(0, len(valid_points)-1, 
                                               min(5, len(valid_points)), dtype=int)
                    for idx in marker_indices:
                        center = tuple(map(int, valid_points[idx]))
                        radius = max(2, int(style["marker_size"]))
                        cv2.circle(image, center, radius, color_bgr, -1)
                        cv2.circle(image, center, radius + 1, (255, 255, 255), 1)  # White outline
                        
            except Exception as e:
                logger.warning(f"Failed to project trajectory {traj_name}: {e}")
                continue
        
        return image
    
    def _transform_trajectory_to_camera_frame(self, trajectory_3d, camera):
        """
        Transform trajectory points from ego vehicle frame to camera frame
        
        Args:
            trajectory_3d: Trajectory points in ego vehicle frame (N, 3)
            camera: Camera object with transformation matrices
            
        Returns:
            Trajectory points in camera frame (N, 3)
        """
        # Get transformation from lidar (ego) to camera
        lidar2cam_r = np.linalg.inv(camera.sensor2lidar_rotation)
        lidar2cam_t = camera.sensor2lidar_translation @ lidar2cam_r.T
        
        # Create 4x4 transformation matrix
        lidar2cam_rt = np.eye(4)
        lidar2cam_rt[:3, :3] = lidar2cam_r.T
        lidar2cam_rt[3, :3] = -lidar2cam_t
        
        # Add homogeneous coordinate
        trajectory_4d = np.concatenate([
            trajectory_3d, 
            np.ones((len(trajectory_3d), 1))
        ], axis=1)
        
        # Transform to camera frame
        trajectory_cam = (lidar2cam_rt.T @ trajectory_4d.T).T
        
        return trajectory_cam[:, :3]
    
    def _hex_to_bgr(self, hex_color: str) -> Tuple[int, int, int]:
        """
        Convert hex color to BGR tuple for OpenCV
        
        Args:
            hex_color: Hex color string (e.g., "#FF0000")
            
        Returns:
            BGR color tuple
        """
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # Convert RGB to BGR for OpenCV
        return (rgb[2], rgb[1], rgb[0])
    
    def _render_camera_view(
        self, 
        ax: plt.Axes, 
        scene_data: Dict[str, Any],
        trajectories: Optional[Dict[str, Any]] = None,
        time_window: Optional[Tuple[float, float]] = None
    ):
        """
        Render front camera view with trajectory projections
        """
        try:
            # Get front camera image
            cameras = scene_data["sensors"]["cameras"]
            front_camera = cameras.cam_f0  # Front camera
            
            # Copy image to avoid modifying original
            image = front_camera.image.copy()
            
            # Project trajectories onto camera image if provided
            if trajectories is not None and time_window is not None:
                image = self._add_trajectory_projections_to_image(
                    image, front_camera, trajectories, time_window
                )
            
            # Display image with projections
            ax.imshow(image)
            ax.set_title("Front Camera View with Trajectory Projections", fontsize=12, fontweight='bold')
            ax.axis('off')
            
            # Add basic info overlay
            ego_status = scene_data["map"]["ego_status"]
            speed = np.linalg.norm(ego_status.ego_velocity)
            
            info_text = f"Speed: {speed:.1f} m/s\nCmd: {ego_status.driving_command}"
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
                   fontsize=10, verticalalignment='top',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
            
            # Add trajectory legend overlay if trajectories exist
            if trajectories is not None:
                legend_text = "\n".join([
                    f"● {self.trajectory_styles[name]['label']}"
                    for name in trajectories.keys() 
                    if name in self.trajectory_styles
                ])
                if legend_text:
                    ax.text(0.98, 0.98, legend_text, transform=ax.transAxes, 
                           fontsize=9, verticalalignment='top', horizontalalignment='right',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.7),
                           color='white')
            
        except Exception as e:
            logger.warning(f"Could not render camera view: {e}")
            ax.text(0.5, 0.5, "Camera view\nnot available", 
                   transform=ax.transAxes, ha='center', va='center',
                   fontsize=12, style='italic')
            ax.set_title("Front Camera View", fontsize=12, fontweight='bold')
    
    def _render_trajectory_comparison(
        self, 
        ax: plt.Axes, 
        trajectories: Dict[str, Any],
        time_window: Tuple[float, float]
    ):
        """
        Render trajectory comparison plot
        """
        time_start, time_end = time_window
        
        # Plot trajectory paths in x-y space
        for traj_name, traj_data in trajectories.items():
            if traj_name not in self.trajectory_styles:
                continue
                
            poses = traj_data["poses"]
            timestamps = traj_data["timestamps"]
            
            # Filter by time window
            time_mask = (timestamps >= time_start) & (timestamps <= time_end)
            if not np.any(time_mask):
                continue
                
            filtered_poses = poses[time_mask]
            style = self.trajectory_styles[traj_name]
            
            # Plot trajectory
            ax.plot(
                filtered_poses[:, 0], 
                filtered_poses[:, 1],
                color=style["color"],
                linestyle=style["style"],
                linewidth=style["width"],
                alpha=style["alpha"],
                label=style["label"]
            )
            
            # Mark start and end points
            if len(filtered_poses) > 0:
                ax.scatter(filtered_poses[0, 0], filtered_poses[0, 1], 
                          c=style["color"], marker='o', s=50, 
                          edgecolors='white', linewidth=1, alpha=0.9)
                ax.scatter(filtered_poses[-1, 0], filtered_poses[-1, 1], 
                          c=style["color"], marker='s', s=50, 
                          edgecolors='white', linewidth=1, alpha=0.9)
        
        ax.set_xlabel("X Position (m)")
        ax.set_ylabel("Y Position (m)")
        ax.set_title("Trajectory Comparison (Top View)", fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
        ax.legend(fontsize=9)
    
    def _render_statistics_panel(
        self, 
        ax: plt.Axes, 
        scene_data: Dict[str, Any], 
        trajectories: Dict[str, Any]
    ):
        """
        Render statistics and information panel
        """
        ax.axis('off')
        
        # Collect statistics
        metadata = scene_data["metadata"]
        
        # Calculate trajectory metrics if we have ground truth and prediction
        metrics_text = ""
        if "ground_truth" in trajectories and "prediction" in trajectories:
            metrics = self._calculate_trajectory_metrics(
                trajectories["ground_truth"]["poses"],
                trajectories["prediction"]["poses"]
            )
            metrics_text = f"""
Trajectory Metrics:
• ADE: {metrics['ade']:.2f}m
• FDE: {metrics['fde']:.2f}m
• Max Error: {metrics['max_error']:.2f}m
• RMSE: {metrics['rmse']:.2f}m
"""
        
        # Scene information
        info_text = f"""
Scene Information:
• Token: {metadata['token'][:16]}...
• Scenario: {metadata['scenario_type']}
• Log: {metadata['log_name']}
• Timestamp: {metadata['timestamp']}

Trajectory Details:"""
        
        for traj_name, traj_data in trajectories.items():
            if traj_name in self.trajectory_styles:
                style = self.trajectory_styles[traj_name]
                length = len(traj_data["poses"])
                duration = traj_data["timestamps"][-1] - traj_data["timestamps"][0] if length > 0 else 0
                info_text += f"\n• {style['label']}: {length} points, {duration:.1f}s"
        
        # Combine all text
        full_text = info_text + metrics_text
        
        # Display text
        ax.text(0.05, 0.95, full_text, transform=ax.transAxes, 
               fontsize=10, verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
        
        ax.set_title("Scene Statistics", fontsize=12, fontweight='bold')
    
    def _calculate_trajectory_metrics(
        self, 
        gt_poses: np.ndarray, 
        pred_poses: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate trajectory comparison metrics
        
        Args:
            gt_poses: Ground truth poses [N, 3]
            pred_poses: Predicted poses [M, 3]
            
        Returns:
            Dictionary with metrics
        """
        # Ensure same length for comparison
        min_length = min(len(gt_poses), len(pred_poses))
        gt_poses = gt_poses[:min_length]
        pred_poses = pred_poses[:min_length]
        
        if min_length == 0:
            return {"ade": 0, "fde": 0, "max_error": 0, "rmse": 0}
        
        # Calculate position errors (ignore heading for now)
        position_errors = np.linalg.norm(gt_poses[:, :2] - pred_poses[:, :2], axis=1)
        
        # Calculate metrics
        ade = np.mean(position_errors)  # Average Displacement Error
        fde = position_errors[-1]       # Final Displacement Error
        max_error = np.max(position_errors)
        rmse = np.sqrt(np.mean(position_errors**2))
        
        return {
            "ade": ade,
            "fde": fde, 
            "max_error": max_error,
            "rmse": rmse
        }
    
    def create_simple_bev_plot(
        self, 
        scene_data: Dict[str, Any], 
        trajectories: Dict[str, Any],
        time_window: Tuple[float, float] = (0, 3.0),
        figsize: Tuple[int, int] = (10, 8)
    ) -> plt.Figure:
        """
        Create a simple BEV plot with trajectories
        
        Args:
            scene_data: Scene data dictionary
            trajectories: Synchronized trajectories
            time_window: Time window to display
            figsize: Figure size
            
        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(1, 1, figsize=figsize)
        
        # Render BEV trajectories
        self._render_bev_trajectories(ax, scene_data, trajectories, time_window)
        
        # Add title
        metadata = scene_data["metadata"]
        ax.set_title(
            f"BEV Trajectory Comparison\n"
            f"Scene: {metadata['scenario_type']} | Token: {metadata['token'][:12]}...",
            fontsize=14, fontweight='bold'
        )
        
        plt.tight_layout()
        return fig
    
    def export_animation_frames(
        self,
        scene_data: Dict[str, Any],
        trajectories: Dict[str, Any],
        output_dir: Path,
        time_windows: List[Tuple[float, float]],
        frame_prefix: str = "frame"
    ) -> List[Path]:
        """
        Export animation frames for different time windows
        
        Args:
            scene_data: Scene data
            trajectories: Trajectory data
            output_dir: Output directory for frames
            time_windows: List of time windows to render
            frame_prefix: Prefix for frame filenames
            
        Returns:
            List of saved frame paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        frame_paths = []
        
        for i, time_window in enumerate(time_windows):
            fig = self.create_simple_bev_plot(scene_data, trajectories, time_window)
            
            frame_path = output_dir / f"{frame_prefix}_{i:03d}.png"
            fig.savefig(frame_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            frame_paths.append(frame_path)
            logger.debug(f"Exported frame {i+1}/{len(time_windows)}: {frame_path}")
        
        logger.info(f"Exported {len(frame_paths)} animation frames to {output_dir}")
        return frame_paths 