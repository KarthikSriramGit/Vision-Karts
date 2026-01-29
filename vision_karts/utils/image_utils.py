"""Image processing utilities."""

import cv2
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path


def load_image(image_path: str) -> np.ndarray:
    """
    Load an image from file path.
    
    Args:
        image_path: Path to image file
    
    Returns:
        Image as numpy array (BGR format)
    """
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    return image


def preprocess_image(image: np.ndarray, target_size: Optional[tuple] = None) -> np.ndarray:
    """
    Preprocess image for model inference.
    
    Args:
        image: Input image (BGR format)
        target_size: Optional target size (width, height)
    
    Returns:
        Preprocessed image
    """
    if target_size:
        image = cv2.resize(image, target_size)
    
    return image


def visualize_detections(
    image: np.ndarray,
    detections: List[Dict],
    show_confidence: bool = True
) -> np.ndarray:
    """
    Draw bounding boxes and labels on image.
    
    Args:
        image: Input image (BGR format)
        detections: List of detection dictionaries
        show_confidence: Whether to show confidence scores
    
    Returns:
        Annotated image
    """
    annotated = image.copy()
    
    for detection in detections:
        bbox = detection['bbox']
        x1, y1, x2, y2 = map(int, bbox)
        
        # Draw bounding box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Draw label
        label = detection['class_name']
        if show_confidence and 'confidence' in detection:
            label += f" {detection['confidence']:.2f}"
        
        # Calculate text size for background
        (text_width, text_height), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2
        )
        
        # Draw text background
        cv2.rectangle(
            annotated,
            (x1, y1 - text_height - baseline - 5),
            (x1 + text_width, y1),
            (0, 255, 0),
            -1
        )
        
        # Draw text
        cv2.putText(
            annotated,
            label,
            (x1, y1 - baseline - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            2
        )
    
    return annotated
