"""
Product Detection Module using YOLOv8

This module provides state-of-the-art product detection capabilities
using Ultralytics YOLOv8, the industry-leading object detection model.
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
from pathlib import Path
import logging

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("YOLOv8 not available. Install with: pip install ultralytics")

from ..accelerators import AcceleratorManager

logger = logging.getLogger(__name__)


class ProductDetector:
    """
    High-performance product detection using YOLOv8.
    
    Supports AI acceleration via TensorRT/ONNX Runtime for real-time inference.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        confidence_threshold: float = 0.5,
        use_acceleration: bool = True,
        device: str = 'auto'
    ):
        """
        Initialize the product detector.
        
        Args:
            model_path: Path to trained YOLOv8 model. If None, uses pretrained COCO weights.
            confidence_threshold: Minimum confidence score for detections (0.0-1.0)
            use_acceleration: Enable AI acceleration (TensorRT/ONNX Runtime)
            device: Device to use ('auto', 'cpu', 'cuda', '0', '1', etc.)
        """
        if not YOLO_AVAILABLE:
            raise ImportError(
                "YOLOv8 is required. Install with: pip install ultralytics"
            )
        
        self.confidence_threshold = confidence_threshold
        self.use_acceleration = use_acceleration
        self.device = self._determine_device(device)
        
        # Initialize YOLOv8 model
        if model_path and Path(model_path).exists():
            logger.info(f"Loading custom model from {model_path}")
            self.model = YOLO(model_path)
        else:
            logger.info("Loading YOLOv8 pretrained model (COCO weights)")
            self.model = YOLO('yolov8n.pt')  # nano for speed, use yolov8m.pt or yolov8l.pt for accuracy
        
        # Setup acceleration if enabled
        self.accelerator = None
        if use_acceleration:
            try:
                self.accelerator = AcceleratorManager(device=self.device)
                logger.info(f"AI acceleration enabled on {self.device}")
            except Exception as e:
                logger.warning(f"Failed to initialize acceleration: {e}")
                self.use_acceleration = False
        
        logger.info(f"ProductDetector initialized (device: {self.device})")
    
    def _determine_device(self, device: str) -> str:
        """Determine the best device to use."""
        if device != 'auto':
            return device
        
        try:
            import torch
            if torch.cuda.is_available():
                return 'cuda'
        except ImportError:
            pass
        
        return 'cpu'
    
    def detect(
        self,
        image: np.ndarray,
        return_image: bool = False
    ) -> Tuple[List[Dict], Optional[np.ndarray]]:
        """
        Detect products in an image.
        
        Args:
            image: Input image as numpy array (BGR format)
            return_image: Whether to return annotated image
        
        Returns:
            Tuple of (detections list, annotated_image)
            Each detection dict contains:
                - 'class_id': int
                - 'class_name': str
                - 'confidence': float
                - 'bbox': [x1, y1, x2, y2]
        """
        if image is None or image.size == 0:
            raise ValueError("Invalid image input")
        
        # Run inference
        results = self.model(
            image,
            conf=self.confidence_threshold,
            device=self.device,
            verbose=False
        )
        
        detections = []
        annotated_image = image.copy() if return_image else None
        
        # Process results
        for result in results:
            boxes = result.boxes
            for i in range(len(boxes)):
                box = boxes.xyxy[i].cpu().numpy()
                conf = float(boxes.conf[i].cpu().numpy())
                cls_id = int(boxes.cls[i].cpu().numpy())
                cls_name = self.model.names[cls_id]
                
                detection = {
                    'class_id': cls_id,
                    'class_name': cls_name,
                    'confidence': conf,
                    'bbox': box.tolist()
                }
                detections.append(detection)
                
                # Draw bounding box if requested
                if return_image:
                    x1, y1, x2, y2 = map(int, box)
                    cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"{cls_name} {conf:.2f}"
                    cv2.putText(
                        annotated_image, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
                    )
        
        return detections, annotated_image
    
    def detect_from_path(self, image_path: str, return_image: bool = False):
        """Detect products from image file path."""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        return self.detect(image, return_image)
    
    def batch_detect(self, images: List[np.ndarray]) -> List[List[Dict]]:
        """Detect products in multiple images (batch processing)."""
        results = self.model(images, conf=self.confidence_threshold, device=self.device)
        
        all_detections = []
        for result in results:
            detections = []
            boxes = result.boxes
            for i in range(len(boxes)):
                box = boxes.xyxy[i].cpu().numpy()
                conf = float(boxes.conf[i].cpu().numpy())
                cls_id = int(boxes.cls[i].cpu().numpy())
                cls_name = self.model.names[cls_id]
                
                detections.append({
                    'class_id': cls_id,
                    'class_name': cls_name,
                    'confidence': conf,
                    'bbox': box.tolist()
                })
            all_detections.append(detections)
        
        return all_detections
