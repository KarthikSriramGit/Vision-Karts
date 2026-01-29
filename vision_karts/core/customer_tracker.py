"""
Customer Tracking Module

Tracks and identifies customers using modern face recognition technology.
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import pickle

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logging.warning("face_recognition not available. Install with: pip install face-recognition")

logger = logging.getLogger(__name__)


class CustomerTracker:
    """
    Customer tracking and identification using face recognition.
    
    Uses dlib's face recognition model (HOG-based) for efficient real-time tracking.
    """
    
    def __init__(self, known_faces_dir: Optional[str] = None):
        """
        Initialize customer tracker.
        
        Args:
            known_faces_dir: Directory containing known customer face images.
                           Each image should be named with customer ID.
        """
        if not FACE_RECOGNITION_AVAILABLE:
            raise ImportError(
                "face_recognition library required. "
                "Install with: pip install face-recognition"
            )
        
        self.known_encodings = {}
        self.known_names = []
        
        if known_faces_dir and Path(known_faces_dir).exists():
            self._load_known_faces(known_faces_dir)
        
        logger.info(f"CustomerTracker initialized with {len(self.known_encodings)} known faces")
    
    def _load_known_faces(self, faces_dir: str):
        """Load known face encodings from directory."""
        faces_path = Path(faces_dir)
        
        for image_path in faces_path.glob("*.jpg"):
            customer_id = image_path.stem
            try:
                image = face_recognition.load_image_file(str(image_path))
                encodings = face_recognition.face_encodings(image)
                
                if encodings:
                    self.known_encodings[customer_id] = encodings[0]
                    self.known_names.append(customer_id)
                    logger.debug(f"Loaded face encoding for {customer_id}")
            except Exception as e:
                logger.warning(f"Failed to load face from {image_path}: {e}")
    
    def detect_faces(self, image: np.ndarray) -> List[Dict]:
        """
        Detect all faces in an image.
        
        Args:
            image: Input image (RGB format)
        
        Returns:
            List of face detection dictionaries with:
                - 'location': (top, right, bottom, left)
                - 'encoding': face encoding array
        """
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        detections = []
        for location, encoding in zip(face_locations, face_encodings):
            detections.append({
                'location': location,
                'encoding': encoding
            })
        
        return detections
    
    def identify_customer(
        self,
        face_encoding: np.ndarray,
        tolerance: float = 0.6
    ) -> Optional[str]:
        """
        Identify a customer from face encoding.
        
        Args:
            face_encoding: Face encoding from detect_faces()
            tolerance: Matching tolerance (lower = stricter)
        
        Returns:
            Customer ID if match found, None otherwise
        """
        if not self.known_encodings:
            return None
        
        # Compare with known faces
        matches = face_recognition.compare_faces(
            list(self.known_encodings.values()),
            face_encoding,
            tolerance=tolerance
        )
        
        face_distances = face_recognition.face_distance(
            list(self.known_encodings.values()),
            face_encoding
        )
        
        if any(matches):
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                return self.known_names[best_match_index]
        
        return None
    
    def track_customers(self, image: np.ndarray) -> List[Dict]:
        """
        Detect and identify all customers in an image.
        
        Args:
            image: Input image (BGR format, will be converted to RGB)
        
        Returns:
            List of customer dictionaries with:
                - 'customer_id': str or None
                - 'location': (top, right, bottom, left)
                - 'confidence': float (if identified)
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        face_detections = self.detect_faces(rgb_image)
        
        customers = []
        for detection in face_detections:
            customer_id = self.identify_customer(detection['encoding'])
            
            customer = {
                'customer_id': customer_id,
                'location': detection['location']
            }
            
            if customer_id:
                # Calculate confidence based on distance
                distances = face_recognition.face_distance(
                    list(self.known_encodings.values()),
                    detection['encoding']
                )
                customer['confidence'] = 1.0 - min(distances)
            
            customers.append(customer)
        
        return customers
    
    def add_customer(self, customer_id: str, image: np.ndarray):
        """
        Add a new customer to the known faces database.
        
        Args:
            customer_id: Unique identifier for the customer
            image: Customer's face image (RGB format)
        """
        encodings = face_recognition.face_encodings(image)
        
        if not encodings:
            raise ValueError(f"No face found in image for customer {customer_id}")
        
        self.known_encodings[customer_id] = encodings[0]
        if customer_id not in self.known_names:
            self.known_names.append(customer_id)
        
        logger.info(f"Added customer {customer_id} to database")
