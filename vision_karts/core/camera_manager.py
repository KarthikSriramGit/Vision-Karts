"""
Multi-Camera Management Module

Manages multiple camera streams for store-wide monitoring and tracking.
"""

import cv2
import numpy as np
import logging
import threading
from typing import List, Dict, Optional, Callable
from pathlib import Path
import time

from .video_processor import VideoProcessor, FrameProcessor

logger = logging.getLogger(__name__)


class CameraManager:
    """
    Manages multiple camera streams with synchronized processing.
    """
    
    def __init__(
        self,
        cameras: List[Dict],
        frame_processor: Optional[FrameProcessor] = None,
        sync_mode: bool = False
    ):
        """
        Initialize camera manager.
        
        Args:
            cameras: List of camera configurations, each with:
                - 'id': Camera ID or path
                - 'name': Camera name/description
                - 'position': Optional [x, y] position in store
            frame_processor: FrameProcessor instance for processing frames
            sync_mode: Whether to synchronize frame capture across cameras
        """
        self.cameras_config = cameras
        self.frame_processor = frame_processor
        self.sync_mode = sync_mode
        
        self.video_processors: Dict[str, VideoProcessor] = {}
        self.running = False
        self.frame_callbacks: Dict[str, Callable] = {}
        
        logger.info(f"CameraManager initialized with {len(cameras)} cameras")
    
    def add_camera(
        self,
        camera_id: str,
        camera_config: Dict,
        frame_callback: Optional[Callable] = None
    ):
        """
        Add a camera to the manager.
        
        Args:
            camera_id: Unique identifier for camera
            camera_config: Camera configuration dict
            frame_callback: Optional callback(frame, camera_id, timestamp)
        """
        if camera_id in self.video_processors:
            logger.warning(f"Camera {camera_id} already exists")
            return
        
        # Create video processor
        processor = VideoProcessor(
            camera_id=camera_config.get('id', 0),
            fps=camera_config.get('fps', 30),
            frame_buffer_size=camera_config.get('frame_buffer_size', 10)
        )
        
        self.video_processors[camera_id] = processor
        self.frame_callbacks[camera_id] = frame_callback
        
        logger.info(f"Added camera {camera_id} ({camera_config.get('name', 'Unnamed')})")
    
    def start_all(self):
        """Start all camera streams."""
        if self.running:
            logger.warning("Camera manager already running")
            return
        
        # Initialize cameras from config
        for cam_config in self.cameras_config:
            camera_id = cam_config.get('id', str(cam_config.get('name', 'camera')))
            self.add_camera(camera_id, cam_config)
        
        # Start all processors
        for camera_id, processor in self.video_processors.items():
            try:
                processor.start()
                
                # Setup processing callback if frame processor available
                if self.frame_processor:
                    def make_callback(cam_id):
                        def callback(frame, timestamp):
                            results = self.frame_processor.process_frame(frame, timestamp)
                            results['camera_id'] = cam_id
                            results['camera_name'] = next(
                                (c.get('name', '') for c in self.cameras_config 
                                 if str(c.get('id', '')) == str(cam_id)),
                                'Unknown'
                            )
                            
                            # Call custom callback if set
                            if cam_id in self.frame_callbacks and self.frame_callbacks[cam_id]:
                                self.frame_callbacks[cam_id](results, cam_id, timestamp)
                            
                            return results
                        return callback
                    
                    processor.processing_callback = make_callback(camera_id)
                
                logger.info(f"Started camera {camera_id}")
            except Exception as e:
                logger.error(f"Failed to start camera {camera_id}: {e}", exc_info=True)
        
        self.running = True
        logger.info("All cameras started")
    
    def stop_all(self):
        """Stop all camera streams."""
        self.running = False
        
        for camera_id, processor in self.video_processors.items():
            try:
                processor.stop()
                logger.info(f"Stopped camera {camera_id}")
            except Exception as e:
                logger.error(f"Error stopping camera {camera_id}: {e}")
        
        self.video_processors.clear()
        logger.info("All cameras stopped")
    
    def get_frame(self, camera_id: str, timeout: float = 1.0):
        """
        Get latest frame from specific camera.
        
        Args:
            camera_id: Camera identifier
            timeout: Maximum wait time
        
        Returns:
            Tuple of (frame, timestamp) or None
        """
        if camera_id not in self.video_processors:
            logger.warning(f"Camera {camera_id} not found")
            return None
        
        return self.video_processors[camera_id].get_frame(timeout)
    
    def get_all_frames(self, timeout: float = 1.0) -> Dict[str, tuple]:
        """
        Get latest frames from all cameras.
        
        Args:
            timeout: Maximum wait time per camera
        
        Returns:
            Dictionary mapping camera_id to (frame, timestamp)
        """
        frames = {}
        for camera_id in self.video_processors:
            frame_data = self.get_frame(camera_id, timeout)
            if frame_data:
                frames[camera_id] = frame_data
        
        return frames
    
    def get_camera_stats(self) -> Dict[str, Dict]:
        """
        Get statistics for all cameras.
        
        Returns:
            Dictionary mapping camera_id to stats dict
        """
        stats = {}
        for camera_id, processor in self.video_processors.items():
            stats[camera_id] = {
                'fps': processor.get_current_fps(),
                'frame_count': processor.frame_count,
                'queue_size': processor.frame_queue.qsize()
            }
        
        return stats
    
    def __enter__(self):
        """Context manager entry."""
        self.start_all()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_all()
