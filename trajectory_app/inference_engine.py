"""
Trajectory Inference Engine

This module provides the core inference engine for trajectory prediction models.
"""

import logging
import time
from typing import Dict, Any, Optional
import torch

from navsim.agents.abstract_agent import AbstractAgent
from navsim.common.dataclasses import AgentInput, Trajectory, Scene

logger = logging.getLogger(__name__)


class TrajectoryInferenceEngine:
    """
    Trajectory prediction inference engine
    Handles model loading, initialization, and inference
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        Initialize the inference engine
        
        Args:
            model_config: Configuration dictionary containing model parameters
                - type: Model type ("diffusiondrive", "transfuser", etc.)
                - checkpoint_path: Path to model checkpoint
                - lr: Learning rate (used during agent initialization)
        """
        self.model_type = model_config.get("type", "diffusiondrive")
        self.checkpoint_path = model_config.get("checkpoint_path")
        self.lr = model_config.get("lr", 6e-4)
        self.agent = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        logger.info(f"Initializing inference engine for {self.model_type} model")
        logger.info(f"Using device: {self.device}")
        
    def load_model(self):
        """
        Load and initialize the model following the evaluation script pattern
        """
        start_time = time.time()
        
        if self.model_type == "diffusiondrive":
            self._load_diffusiondrive_model()
        elif self.model_type == "transfuser":
            self._load_transfuser_model()
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
        
        # Set to evaluation mode and move to device
        self.agent.eval()
        self.agent.to(self.device)
        
        load_time = time.time() - start_time
        logger.info(f"Model loaded successfully in {load_time:.2f}s")
        logger.info(f"Sensor config: {self.agent.get_sensor_config()}")
        
    def _load_diffusiondrive_model(self):
        """Load DiffusionDrive model"""
        try:
            from navsim.agents.diffusiondrive.transfuser_config import TransfuserConfig
            from navsim.agents.diffusiondrive.transfuser_agent import TransfuserAgent
            
            # Create configuration
            config = TransfuserConfig()
            
            # Create agent instance
            self.agent = TransfuserAgent(
                config=config,
                lr=self.lr,
                checkpoint_path=self.checkpoint_path
            )
            
            # Initialize weights if checkpoint provided
            if self.checkpoint_path:
                logger.info(f"Loading checkpoint from: {self.checkpoint_path}")
                self.agent.initialize()
            else:
                logger.warning("No checkpoint provided, using randomly initialized weights")
                
        except Exception as e:
            logger.error(f"Failed to load DiffusionDrive model: {e}")
            raise
            
    def _load_transfuser_model(self):
        """Load Transfuser model"""
        try:
            from navsim.agents.transfuser.transfuser_config import TransfuserConfig
            from navsim.agents.transfuser.transfuser_agent import TransfuserAgent
            
            # Create configuration
            config = TransfuserConfig()
            
            # Create agent instance
            self.agent = TransfuserAgent(
                config=config,
                lr=self.lr,
                checkpoint_path=self.checkpoint_path
            )
            
            # Initialize weights if checkpoint provided
            if self.checkpoint_path:
                logger.info(f"Loading checkpoint from: {self.checkpoint_path}")
                self.agent.initialize()
            else:
                logger.warning("No checkpoint provided, using randomly initialized weights")
                
        except Exception as e:
            logger.error(f"Failed to load Transfuser model: {e}")
            raise
    
    def predict_trajectory(self, agent_input: AgentInput, scene: Optional[Scene] = None) -> Dict[str, Any]:
        """
        Predict trajectory for given agent input
        
        Args:
            agent_input: Input data for the agent
            scene: Optional scene data (required for some models)
            
        Returns:
            Dictionary containing prediction results and metadata
        """
        if self.agent is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        start_time = time.time()
        
        # Perform inference
        with torch.no_grad():
            if hasattr(self.agent, 'requires_scene') and self.agent.requires_scene and scene is not None:
                pred_trajectory = self.agent.compute_trajectory(agent_input, scene)
            else:
                pred_trajectory = self.agent.compute_trajectory(agent_input)
        
        inference_time = time.time() - start_time
        
        # Collect results
        result = {
            "trajectory": pred_trajectory,
            "inference_time": inference_time,
            "model_type": self.model_type,
            "trajectory_length": len(pred_trajectory.poses),
            "time_horizon": pred_trajectory.trajectory_sampling.time_horizon if hasattr(pred_trajectory, 'trajectory_sampling') else None
        }
        
        logger.debug(f"Inference completed in {inference_time:.3f}s")
        logger.debug(f"Predicted trajectory with {len(pred_trajectory.poses)} points")
        
        return result
    
    def get_sensor_config(self):
        """
        Get sensor configuration required for data loading
        """
        if self.agent is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        return self.agent.get_sensor_config()
    
    def get_feature_builders(self):
        """Get feature builders from the agent"""
        if self.agent is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        return self.agent.get_feature_builders()
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model
        """
        if self.agent is None:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "model_type": self.model_type,
            "checkpoint_path": self.checkpoint_path,
            "device": str(self.device),
            "sensor_config": self.agent.get_sensor_config(),
            "num_parameters": sum(p.numel() for p in self.agent.parameters()),
            "trainable_parameters": sum(p.numel() for p in self.agent.parameters() if p.requires_grad)
        } 