"""
Virtual Cart Management Module

Manages per-customer virtual shopping carts with real-time updates.
"""

import logging
import time
from typing import List, Dict, Optional, Set, Callable
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class CartItem:
    """Represents an item in a virtual cart."""
    product_name: str
    quantity: int = 1
    unit_price: float = 0.0
    first_detected: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    confidence_scores: List[float] = field(default_factory=list)
    
    @property
    def total_price(self) -> float:
        """Calculate total price for this item."""
        return self.unit_price * self.quantity
    
    @property
    def avg_confidence(self) -> float:
        """Calculate average confidence score."""
        if not self.confidence_scores:
            return 0.0
        return sum(self.confidence_scores) / len(self.confidence_scores)


@dataclass
class VirtualCart:
    """Virtual shopping cart for a customer."""
    customer_id: str
    session_id: str
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    items: Dict[str, CartItem] = field(default_factory=dict)
    total_amount: float = 0.0
    
    def add_item(
        self,
        product_name: str,
        unit_price: float,
        confidence: float = 1.0
    ):
        """Add or update an item in the cart."""
        if product_name in self.items:
            # Update existing item
            item = self.items[product_name]
            item.quantity += 1
            item.confidence_scores.append(confidence)
            item.last_updated = time.time()
        else:
            # Add new item
            self.items[product_name] = CartItem(
                product_name=product_name,
                quantity=1,
                unit_price=unit_price,
                confidence_scores=[confidence]
            )
        
        self.last_updated = time.time()
        self._recalculate_total()
    
    def remove_item(self, product_name: str, quantity: int = 1):
        """Remove items from cart."""
        if product_name not in self.items:
            return
        
        item = self.items[product_name]
        item.quantity = max(0, item.quantity - quantity)
        
        if item.quantity == 0:
            del self.items[product_name]
        
        self.last_updated = time.time()
        self._recalculate_total()
    
    def clear(self):
        """Clear all items from cart."""
        self.items.clear()
        self.total_amount = 0.0
        self.last_updated = time.time()
    
    def _recalculate_total(self):
        """Recalculate total cart amount."""
        self.total_amount = sum(item.total_price for item in self.items.values())
    
    def to_dict(self) -> Dict:
        """Convert cart to dictionary."""
        return {
            'customer_id': self.customer_id,
            'session_id': self.session_id,
            'created_at': self.created_at,
            'last_updated': self.last_updated,
            'item_count': sum(item.quantity for item in self.items.values()),
            'total_amount': round(self.total_amount, 2),
            'items': [
                {
                    'product': item.product_name,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'total': item.total_price,
                    'avg_confidence': item.avg_confidence
                }
                for item in self.items.values()
            ]
        }


class VirtualCartManager:
    """
    Manages multiple virtual carts for different customers.
    """
    
    def __init__(
        self,
        price_calculator: Optional[Callable] = None,
        cart_timeout: float = 300.0
    ):
        """
        Initialize cart manager.
        
        Args:
            price_calculator: Function(product_name) -> price
            cart_timeout: Seconds before inactive cart expires
        """
        self.price_calculator = price_calculator
        self.cart_timeout = cart_timeout
        
        # Maps customer_id -> VirtualCart
        self.carts: Dict[str, VirtualCart] = {}
        
        # Maps session_id -> customer_id
        self.session_to_customer: Dict[str, str] = {}
        
        logger.info(f"VirtualCartManager initialized (timeout={cart_timeout}s)")
    
    def create_cart(
        self,
        customer_id: str,
        session_id: str
    ) -> VirtualCart:
        """
        Create a new virtual cart for a customer.
        
        Args:
            customer_id: Unique customer identifier
            session_id: Session identifier
        
        Returns:
            VirtualCart instance
        """
        if customer_id in self.carts:
            logger.warning(f"Cart already exists for customer {customer_id}")
            return self.carts[customer_id]
        
        cart = VirtualCart(
            customer_id=customer_id,
            session_id=session_id
        )
        
        self.carts[customer_id] = cart
        self.session_to_customer[session_id] = customer_id
        
        logger.info(f"Created cart for customer {customer_id} (session {session_id})")
        return cart
    
    def get_cart(self, customer_id: str) -> Optional[VirtualCart]:
        """Get cart for a customer."""
        return self.carts.get(customer_id)
    
    def get_cart_by_session(self, session_id: str) -> Optional[VirtualCart]:
        """Get cart by session ID."""
        customer_id = self.session_to_customer.get(session_id)
        if customer_id:
            return self.carts.get(customer_id)
        return None
    
    def update_cart_from_detections(
        self,
        customer_id: str,
        detections: List[Dict],
        event_type: str = 'pick'
    ):
        """
        Update cart based on product detections.
        
        Args:
            customer_id: Customer identifier
            detections: List of product detection dictionaries
            event_type: 'pick' or 'return'
        """
        cart = self.get_cart(customer_id)
        if not cart:
            logger.warning(f"No cart found for customer {customer_id}")
            return
        
        for detection in detections:
            product_name = detection.get('class_name', '')
            confidence = detection.get('confidence', 0.0)
            
            # Get price
            if self.price_calculator:
                price = self.price_calculator(product_name)
            else:
                price = 0.0
            
            if event_type == 'pick':
                cart.add_item(product_name, price, confidence)
            elif event_type == 'return':
                cart.remove_item(product_name, 1)
        
        logger.debug(f"Updated cart for {customer_id}: {len(cart.items)} items, ${cart.total_amount:.2f}")
    
    def remove_cart(self, customer_id: str):
        """Remove a cart (e.g., after checkout)."""
        if customer_id in self.carts:
            cart = self.carts[customer_id]
            session_id = cart.session_id
            
            del self.carts[customer_id]
            if session_id in self.session_to_customer:
                del self.session_to_customer[session_id]
            
            logger.info(f"Removed cart for customer {customer_id}")
    
    def cleanup_expired_carts(self):
        """Remove carts that have been inactive for too long."""
        current_time = time.time()
        expired_customers = []
        
        for customer_id, cart in self.carts.items():
            if current_time - cart.last_updated > self.cart_timeout:
                expired_customers.append(customer_id)
        
        for customer_id in expired_customers:
            logger.info(f"Removing expired cart for customer {customer_id}")
            self.remove_cart(customer_id)
    
    def get_all_carts(self) -> List[VirtualCart]:
        """Get all active carts."""
        return list(self.carts.values())
    
    def get_cart_summary(self) -> Dict:
        """Get summary of all carts."""
        return {
            'total_carts': len(self.carts),
            'total_items': sum(
                sum(item.quantity for item in cart.items.values())
                for cart in self.carts.values()
            ),
            'total_value': sum(cart.total_amount for cart in self.carts.values()),
            'carts': [cart.to_dict() for cart in self.carts.values()]
        }
