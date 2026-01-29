"""
Session Management Module

Manages customer sessions from entry to exit in automated checkout systems.
"""

import logging
import time
import uuid
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class SessionStatus(Enum):
    """Session status enumeration."""
    ACTIVE = "active"
    EXITING = "exiting"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


@dataclass
class CustomerSession:
    """Represents a customer shopping session."""
    session_id: str
    customer_id: str
    entry_time: float = field(default_factory=time.time)
    exit_time: Optional[float] = None
    status: SessionStatus = SessionStatus.ACTIVE
    entry_camera: Optional[str] = None
    exit_camera: Optional[str] = None
    cart_id: Optional[str] = None
    
    @property
    def duration(self) -> float:
        """Get session duration in seconds."""
        end_time = self.exit_time if self.exit_time else time.time()
        return end_time - self.entry_time
    
    @property
    def is_active(self) -> bool:
        """Check if session is active."""
        return self.status == SessionStatus.ACTIVE
    
    def to_dict(self) -> Dict:
        """Convert session to dictionary."""
        return {
            'session_id': self.session_id,
            'customer_id': self.customer_id,
            'entry_time': self.entry_time,
            'exit_time': self.exit_time,
            'duration': self.duration,
            'status': self.status.value,
            'entry_camera': self.entry_camera,
            'exit_camera': self.exit_camera,
            'cart_id': self.cart_id
        }


class SessionManager:
    """
    Manages customer sessions from entry to exit.
    """
    
    def __init__(
        self,
        session_timeout: float = 3600.0,  # 1 hour default
        max_concurrent_sessions: int = 1000
    ):
        """
        Initialize session manager.
        
        Args:
            session_timeout: Maximum session duration in seconds
            max_concurrent_sessions: Maximum number of concurrent sessions
        """
        self.session_timeout = session_timeout
        self.max_concurrent_sessions = max_concurrent_sessions
        
        # Maps session_id -> CustomerSession
        self.sessions: Dict[str, CustomerSession] = {}
        
        # Maps customer_id -> session_id (for active sessions)
        self.customer_to_session: Dict[str, str] = {}
        
        logger.info(f"SessionManager initialized (timeout={session_timeout}s)")
    
    def create_session(
        self,
        customer_id: str,
        entry_camera: Optional[str] = None
    ) -> CustomerSession:
        """
        Create a new customer session.
        
        Args:
            customer_id: Customer identifier
            entry_camera: Camera ID where customer entered
        
        Returns:
            CustomerSession instance
        """
        # Check if customer already has active session
        if customer_id in self.customer_to_session:
            existing_session_id = self.customer_to_session[customer_id]
            existing_session = self.sessions.get(existing_session_id)
            
            if existing_session and existing_session.is_active:
                logger.warning(f"Customer {customer_id} already has active session {existing_session_id}")
                return existing_session
        
        # Check session limit
        active_count = sum(1 for s in self.sessions.values() if s.is_active)
        if active_count >= self.max_concurrent_sessions:
            logger.error(f"Maximum concurrent sessions reached ({self.max_concurrent_sessions})")
            raise RuntimeError("Maximum concurrent sessions reached")
        
        # Create new session
        session_id = str(uuid.uuid4())
        session = CustomerSession(
            session_id=session_id,
            customer_id=customer_id,
            entry_camera=entry_camera
        )
        
        self.sessions[session_id] = session
        self.customer_to_session[customer_id] = session_id
        
        logger.info(f"Created session {session_id} for customer {customer_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[CustomerSession]:
        """Get session by ID."""
        return self.sessions.get(session_id)
    
    def get_session_by_customer(self, customer_id: str) -> Optional[CustomerSession]:
        """Get active session for a customer."""
        session_id = self.customer_to_session.get(customer_id)
        if session_id:
            return self.sessions.get(session_id)
        return None
    
    def update_session_cart(self, session_id: str, cart_id: str):
        """Update session with cart ID."""
        session = self.get_session(session_id)
        if session:
            session.cart_id = cart_id
            logger.debug(f"Updated session {session_id} with cart {cart_id}")
    
    def mark_exiting(
        self,
        session_id: str,
        exit_camera: Optional[str] = None
    ):
        """
        Mark session as exiting (customer approaching exit).
        
        Args:
            session_id: Session identifier
            exit_camera: Camera ID where customer is exiting
        """
        session = self.get_session(session_id)
        if session:
            session.status = SessionStatus.EXITING
            session.exit_camera = exit_camera
            logger.info(f"Session {session_id} marked as exiting")
    
    def complete_session(
        self,
        session_id: str,
        exit_camera: Optional[str] = None
    ) -> CustomerSession:
        """
        Complete a session (customer exited).
        
        Args:
            session_id: Session identifier
            exit_camera: Camera ID where customer exited
        
        Returns:
            Completed CustomerSession
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.exit_time = time.time()
        session.status = SessionStatus.COMPLETED
        session.exit_camera = exit_camera
        
        # Remove from active customer mapping
        if session.customer_id in self.customer_to_session:
            del self.customer_to_session[session.customer_id]
        
        logger.info(f"Completed session {session_id} (duration: {session.duration:.1f}s)")
        return session
    
    def abandon_session(self, session_id: str):
        """Mark session as abandoned."""
        session = self.get_session(session_id)
        if session:
            session.status = SessionStatus.ABANDONED
            session.exit_time = time.time()
            
            if session.customer_id in self.customer_to_session:
                del self.customer_to_session[session.customer_id]
            
            logger.info(f"Abandoned session {session_id}")
    
    def cleanup_expired_sessions(self):
        """Remove expired or abandoned sessions."""
        current_time = time.time()
        sessions_to_remove = []
        
        for session_id, session in self.sessions.items():
            # Check timeout
            if session.is_active and current_time - session.entry_time > self.session_timeout:
                logger.warning(f"Session {session_id} expired (timeout)")
                self.abandon_session(session_id)
            
            # Remove old completed/abandoned sessions (older than 24 hours)
            if session.status in [SessionStatus.COMPLETED, SessionStatus.ABANDONED]:
                if session.exit_time and current_time - session.exit_time > 86400:  # 24 hours
                    sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
            logger.debug(f"Removed old session {session_id}")
    
    def get_active_sessions(self) -> List[CustomerSession]:
        """Get all active sessions."""
        return [s for s in self.sessions.values() if s.is_active]
    
    def get_session_stats(self) -> Dict:
        """Get session statistics."""
        active = len(self.get_active_sessions())
        exiting = sum(1 for s in self.sessions.values() if s.status == SessionStatus.EXITING)
        completed = sum(1 for s in self.sessions.values() if s.status == SessionStatus.COMPLETED)
        abandoned = sum(1 for s in self.sessions.values() if s.status == SessionStatus.ABANDONED)
        
        return {
            'total_sessions': len(self.sessions),
            'active': active,
            'exiting': exiting,
            'completed': completed,
            'abandoned': abandoned
        }
