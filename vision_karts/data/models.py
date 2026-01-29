"""
Database Models

SQLAlchemy models for database operations (optional, can use raw SQL).
"""

import logging
from typing import Optional
from datetime import datetime

try:
    from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, ForeignKey, Text
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, relationship
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    logging.warning("SQLAlchemy not available. Install with: pip install sqlalchemy")

logger = logging.getLogger(__name__)

if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()
    
    class Customer(Base):
        """Customer model."""
        __tablename__ = 'customers'
        
        customer_id = Column(String, primary_key=True)
        name = Column(String)
        email = Column(String)
        phone = Column(String)
        payment_method = Column(String)
        created_at = Column(DateTime, default=datetime.utcnow)
        last_visit = Column(DateTime)
        
        # Relationships
        sessions = relationship("Session", back_populates="customer")
    
    class Session(Base):
        """Session model."""
        __tablename__ = 'sessions'
        
        session_id = Column(String, primary_key=True)
        customer_id = Column(String, ForeignKey('customers.customer_id'))
        entry_time = Column(DateTime)
        exit_time = Column(DateTime)
        status = Column(String)
        entry_camera = Column(String)
        exit_camera = Column(String)
        cart_id = Column(String)
        
        # Relationships
        customer = relationship("Customer", back_populates="sessions")
        transactions = relationship("Transaction", back_populates="session")
    
    class Transaction(Base):
        """Transaction model."""
        __tablename__ = 'transactions'
        
        transaction_id = Column(String, primary_key=True)
        session_id = Column(String, ForeignKey('sessions.session_id'))
        customer_id = Column(String, ForeignKey('customers.customer_id'))
        timestamp = Column(DateTime)
        total_amount = Column(Float)
        item_count = Column(Integer)
        payment_status = Column(String)
        receipt_path = Column(String)
        
        # Relationships
        session = relationship("Session", back_populates="transactions")
        items = relationship("TransactionItem", back_populates="transaction")
    
    class TransactionItem(Base):
        """Transaction item model."""
        __tablename__ = 'transaction_items'
        
        id = Column(Integer, primary_key=True)
        transaction_id = Column(String, ForeignKey('transactions.transaction_id'))
        product_name = Column(String)
        quantity = Column(Integer)
        unit_price = Column(Float)
        total_price = Column(Float)
        
        # Relationships
        transaction = relationship("Transaction", back_populates="items")
    
    class AnalyticsEvent(Base):
        """Analytics event model."""
        __tablename__ = 'analytics_events'
        
        id = Column(Integer, primary_key=True)
        event_type = Column(String)
        customer_id = Column(String)
        session_id = Column(String)
        product_name = Column(String)
        value = Column(Float)
        timestamp = Column(DateTime)
        metadata = Column(Text)
