"""
Product Pick/Return Event Tracking Module

Tracks product interactions (pick up, return) using temporal analysis.
"""

import logging
import time
import numpy as np
from typing import List, Dict, Optional, Tuple
from collections import deque
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProductEvent:
    """Represents a product interaction event."""
    event_type: str  # 'pick' or 'return'
    product_name: str
    customer_id: str
    timestamp: float
    confidence: float
    location: Optional[Tuple[float, float]] = None
    camera_id: Optional[str] = None


class EventTracker:
    """
    Tracks product pick/return events using temporal analysis of detections.
    """
    
    def __init__(
        self,
        detection_window: float = 2.0,
        min_pick_duration: float = 0.5,
        min_return_duration: float = 0.5
    ):
        """
        Initialize event tracker.
        
        Args:
            detection_window: Time window (seconds) for tracking detections
            min_pick_duration: Minimum duration for pick event
            min_return_duration: Minimum duration for return event
        """
        self.detection_window = detection_window
        self.min_pick_duration = min_pick_duration
        self.min_return_duration = min_return_duration
        
        # Track detection history per customer-product pair
        # Structure: (customer_id, product_name) -> deque of (timestamp, detected)
        self.detection_history: Dict[Tuple[str, str], deque] = {}
        
        # Recent events
        self.recent_events: deque = deque(maxlen=1000)
        
        logger.info("EventTracker initialized")
    
    def process_detections(
        self,
        customer_id: str,
        detections: List[Dict],
        timestamp: float,
        camera_id: Optional[str] = None
    ) -> List[ProductEvent]:
        """
        Process detections and generate events.
        
        Args:
            customer_id: Customer identifier
            detections: List of product detections
            timestamp: Current timestamp
            camera_id: Optional camera identifier
        
        Returns:
            List of ProductEvent objects
        """
        events = []
        
        # Get currently detected products
        current_products = {d['class_name']: d for d in detections}
        
        # Update detection history
        for product_name in current_products.keys():
            key = (customer_id, product_name)
            
            if key not in self.detection_history:
                self.detection_history[key] = deque(maxlen=100)
            
            self.detection_history[key].append((timestamp, True))
        
        # Check for events (products that disappeared = return, new products = pick)
        for key, history in self.detection_history.items():
            cust_id, product_name = key
            
            if cust_id != customer_id:
                continue
            
            # Clean old entries
            while history and timestamp - history[0][0] > self.detection_window:
                history.popleft()
            
            if not history:
                continue
            
            # Check if product was detected recently
            recent_detections = [ts for ts, detected in history if detected]
            
            if not recent_detections:
                continue
            
            # Check if product is currently detected
            is_currently_detected = product_name in current_products
            
            # Analyze pattern to determine event
            if len(recent_detections) >= 3:
                # Product was detected but now missing = return
                if not is_currently_detected:
                    last_detection_time = recent_detections[-1]
                    duration = timestamp - last_detection_time
                    
                    if duration >= self.min_return_duration:
                        event = ProductEvent(
                            event_type='return',
                            product_name=product_name,
                            customer_id=customer_id,
                            timestamp=timestamp,
                            confidence=0.8,  # Could be improved with better tracking
                            camera_id=camera_id
                        )
                        events.append(event)
                        self.recent_events.append(event)
                        logger.info(f"Return event: {customer_id} returned {product_name}")
            
            # Check for new product detection = pick
            if is_currently_detected and len(recent_detections) == 1:
                # First time detecting this product
                detection = current_products[product_name]
                event = ProductEvent(
                    event_type='pick',
                    product_name=product_name,
                    customer_id=customer_id,
                    timestamp=timestamp,
                    confidence=detection.get('confidence', 0.5),
                    camera_id=camera_id
                )
                events.append(event)
                self.recent_events.append(event)
                logger.info(f"Pick event: {customer_id} picked {product_name}")
        
        return events
    
    def get_recent_events(
        self,
        customer_id: Optional[str] = None,
        event_type: Optional[str] = None,
        since: Optional[float] = None
    ) -> List[ProductEvent]:
        """
        Get recent events with optional filtering.
        
        Args:
            customer_id: Filter by customer
            event_type: Filter by event type ('pick' or 'return')
            since: Only return events after this timestamp
        
        Returns:
            List of ProductEvent objects
        """
        events = list(self.recent_events)
        
        if customer_id:
            events = [e for e in events if e.customer_id == customer_id]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if since:
            events = [e for e in events if e.timestamp >= since]
        
        return events
    
    def clear_history(self, customer_id: Optional[str] = None):
        """Clear detection history for a customer or all customers."""
        if customer_id:
            keys_to_remove = [k for k in self.detection_history.keys() if k[0] == customer_id]
            for key in keys_to_remove:
                del self.detection_history[key]
        else:
            self.detection_history.clear()
        
        logger.info(f"Cleared history for {'customer' if customer_id else 'all customers'}")
