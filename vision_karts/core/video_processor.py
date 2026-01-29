"""
Real-Time Video Processing Module

Processes video streams in real-time for automated checkout systems.
Supports single and multi-camera configurations with optimized frame processing.
"""

import cv2
import numpy as np
import logging
import threading
import queue
import time
from typing import List, Dict, Optional, Callable, Tuple
from pathlib import Path
from collections import deque

logger = logging.getLogger(__name__)


class VideoProcessor:
    """
    Real-time video stream processor with frame buffering and multi-threading support.
    """
    
    def __init__(
        self,
        camera_id: int = 0,
        fps: int = 30,
        frame_buffer_size: int = 10,
        processing_callback: Optional[Callable] = None
    ):
        """
        Initialize video processor.
        
        Args:
            camera_id: Camera device ID or video file path
            fps: Target frames per second
            frame_buffer_size: Size of frame buffer queue
            processing_callback: Optional callback function(frame, timestamp) -> results
        """
        self.camera_id = camera_id
        self.fps = fps
        self.frame_buffer_size = frame_buffer_size
        self.processing_callback = processing_callback
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.frame_queue = queue.Queue(maxsize=frame_buffer_size)
        self.running = False
        self.processing_thread: Optional[threading.Thread] = None
        self.capture_thread: Optional[threading.Thread] = None
        
        self.frame_count = 0
        self.fps_counter = deque(maxlen=30)
        self.last_fps_time = time.time()
        
        logger.info(f"VideoProcessor initialized (camera_id={camera_id}, fps={fps})")
    
    def start(self):
        """Start video capture and processing."""
        if self.running:
            logger.warning("Video processor already running")
            return
        
        # Initialize camera
        if isinstance(self.camera_id, (int, str)):
            self.cap = cv2.VideoCapture(self.camera_id)
        else:
            raise ValueError(f"Invalid camera_id: {self.camera_id}")
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera {self.camera_id}")
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce latency
        
        self.running = True
        
        # Start capture thread
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        # Start processing thread
        if self.processing_callback:
            self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
            self.processing_thread.start()
        
        logger.info("Video processor started")
    
    def stop(self):
        """Stop video capture and processing."""
        self.running = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        
        if self.processing_thread:
            self.processing_thread.join(timeout=2.0)
        
        if self.cap:
            self.cap.release()
        
        # Clear queue
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break
        
        logger.info("Video processor stopped")
    
    def _capture_loop(self):
        """Capture frames from camera in separate thread."""
        while self.running:
            ret, frame = self.cap.read()
            
            if not ret:
                logger.warning("Failed to read frame from camera")
                time.sleep(0.1)
                continue
            
            timestamp = time.time()
            
            # Add to queue (non-blocking, drop old frames if queue full)
            try:
                self.frame_queue.put_nowait((frame, timestamp))
            except queue.Full:
                # Drop oldest frame
                try:
                    self.frame_queue.get_nowait()
                    self.frame_queue.put_nowait((frame, timestamp))
                except queue.Empty:
                    pass
            
            # Update FPS counter
            self.frame_count += 1
            current_time = time.time()
            if current_time - self.last_fps_time >= 1.0:
                actual_fps = len(self.fps_counter) / (current_time - self.last_fps_time)
                self.fps_counter.append(actual_fps)
                self.last_fps_time = current_time
    
    def _processing_loop(self):
        """Process frames in separate thread."""
        while self.running:
            try:
                frame, timestamp = self.frame_queue.get(timeout=1.0)
                
                if self.processing_callback:
                    try:
                        results = self.processing_callback(frame, timestamp)
                        # Results can be handled by callback or stored
                    except Exception as e:
                        logger.error(f"Error in processing callback: {e}", exc_info=True)
                
                self.frame_queue.task_done()
            except queue.Empty:
                continue
    
    def get_frame(self, timeout: float = 1.0) -> Optional[Tuple[np.ndarray, float]]:
        """
        Get latest frame from queue.
        
        Args:
            timeout: Maximum time to wait for frame
        
        Returns:
            Tuple of (frame, timestamp) or None if timeout
        """
        try:
            return self.frame_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_current_fps(self) -> float:
        """Get current frames per second."""
        if len(self.fps_counter) == 0:
            return 0.0
        return sum(self.fps_counter) / len(self.fps_counter)
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


class FrameProcessor:
    """
    Frame-by-frame processing pipeline for product detection and tracking.
    """
    
    def __init__(
        self,
        product_detector,
        customer_tracker: Optional = None,
        confidence_threshold: float = 0.5
    ):
        """
        Initialize frame processor.
        
        Args:
            product_detector: ProductDetector instance
            customer_tracker: Optional CustomerTracker instance
            confidence_threshold: Minimum confidence for detections
        """
        self.product_detector = product_detector
        self.customer_tracker = customer_tracker
        self.confidence_threshold = confidence_threshold
        
        logger.info("FrameProcessor initialized")
    
    def process_frame(
        self,
        frame: np.ndarray,
        timestamp: float
    ) -> Dict:
        """
        Process a single frame.
        
        Args:
            frame: Input frame (BGR format)
            timestamp: Frame timestamp
        
        Returns:
            Dictionary with processing results:
                - 'detections': List of product detections
                - 'customers': List of customer detections
                - 'timestamp': float
                - 'frame_id': int
        """
        results = {
            'timestamp': timestamp,
            'detections': [],
            'customers': []
        }
        
        # Detect products
        try:
            detections, _ = self.product_detector.detect(frame, return_image=False)
            results['detections'] = [
                d for d in detections
                if d['confidence'] >= self.confidence_threshold
            ]
        except Exception as e:
            logger.error(f"Error in product detection: {e}", exc_info=True)
        
        # Track customers if tracker available
        if self.customer_tracker:
            try:
                customers = self.customer_tracker.track_customers(frame)
                results['customers'] = customers
            except Exception as e:
                logger.error(f"Error in customer tracking: {e}", exc_info=True)
        
        return results
