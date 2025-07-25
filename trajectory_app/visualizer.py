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
        
        # 2. Front camera view (top right)
        ax_camera = plt.subplot(2, 3, 2)
        self._render_camera_view(ax_camera, scene_data)
        
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
                
                ax.plot(
                    filtered_poses[i:i+2, 0], 
                    filtered_poses[i:i+2, 1],
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
                    filtered_poses[idx, 0], 
                    filtered_poses[idx, 1],
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
    
    def _render_camera_view(self, ax: plt.Axes, scene_data: Dict[str, Any]):
        """
        Render front camera view
        """
        try:
            # Get front camera image
            cameras = scene_data["sensors"]["cameras"]
            front_camera = cameras.cam_f0  # Front camera
            
            # Display image
            ax.imshow(front_camera.image)
            ax.set_title("Front Camera View", fontsize=12, fontweight='bold')
            ax.axis('off')
            
            # Add basic info overlay
            ego_status = scene_data["map"]["ego_status"]
            speed = np.linalg.norm(ego_status.ego_velocity)
            
            info_text = f"Speed: {speed:.1f} m/s\nCmd: {ego_status.driving_command}"
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
                   fontsize=10, verticalalignment='top',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
            
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