"""
Customer Database Module

Manages customer accounts, profiles, and payment information.
"""

import logging
import json
from typing import Dict, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class CustomerProfile:
    """Customer profile information."""
    customer_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    payment_method: Optional[str] = None
    payment_token: Optional[str] = None  # Encrypted payment info
    created_at: str = None
    last_visit: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class CustomerDB:
    """
    Simple file-based customer database (can be replaced with SQL database).
    """
    
    def __init__(self, db_path: str = "data/customers.json"):
        """
        Initialize customer database.
        
        Args:
            db_path: Path to JSON database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.customers: Dict[str, CustomerProfile] = {}
        self._load_database()
        
        logger.info(f"CustomerDB initialized ({len(self.customers)} customers)")
    
    def _load_database(self):
        """Load customer database from file."""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    for customer_id, profile_data in data.items():
                        self.customers[customer_id] = CustomerProfile(**profile_data)
                logger.info(f"Loaded {len(self.customers)} customers from database")
            except Exception as e:
                logger.error(f"Error loading database: {e}", exc_info=True)
    
    def _save_database(self):
        """Save customer database to file."""
        try:
            data = {
                customer_id: asdict(profile)
                for customer_id, profile in self.customers.items()
            }
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug("Database saved")
        except Exception as e:
            logger.error(f"Error saving database: {e}", exc_info=True)
    
    def register_customer(
        self,
        customer_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> CustomerProfile:
        """
        Register a new customer.
        
        Args:
            customer_id: Unique customer identifier
            name: Customer name
            email: Email address
            phone: Phone number
        
        Returns:
            CustomerProfile instance
        """
        if customer_id in self.customers:
            logger.warning(f"Customer {customer_id} already exists")
            return self.customers[customer_id]
        
        profile = CustomerProfile(
            customer_id=customer_id,
            name=name,
            email=email,
            phone=phone
        )
        
        self.customers[customer_id] = profile
        self._save_database()
        
        logger.info(f"Registered customer {customer_id}")
        return profile
    
    def get_customer(self, customer_id: str) -> Optional[CustomerProfile]:
        """Get customer profile."""
        return self.customers.get(customer_id)
    
    def update_customer(
        self,
        customer_id: str,
        **updates
    ) -> Optional[CustomerProfile]:
        """
        Update customer profile.
        
        Args:
            customer_id: Customer identifier
            **updates: Fields to update
        
        Returns:
            Updated CustomerProfile or None
        """
        profile = self.get_customer(customer_id)
        if not profile:
            logger.warning(f"Customer {customer_id} not found")
            return None
        
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.last_visit = datetime.now().isoformat()
        self._save_database()
        
        logger.info(f"Updated customer {customer_id}")
        return profile
    
    def set_payment_method(
        self,
        customer_id: str,
        payment_method: str,
        payment_token: Optional[str] = None
    ):
        """Set payment method for customer."""
        self.update_customer(
            customer_id,
            payment_method=payment_method,
            payment_token=payment_token
        )
    
    def get_all_customers(self) -> List[CustomerProfile]:
        """Get all customers."""
        return list(self.customers.values())
    
    def delete_customer(self, customer_id: str):
        """Delete customer from database."""
        if customer_id in self.customers:
            del self.customers[customer_id]
            self._save_database()
            logger.info(f"Deleted customer {customer_id}")
