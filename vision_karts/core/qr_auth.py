"""
QR Code Authentication Module

Handles QR code generation, scanning, and validation for customer entry.
"""

import logging
import qrcode
import io
import base64
import hashlib
import time
from typing import Optional, Dict, Tuple
from PIL import Image
import cv2
import numpy as np

try:
    from pyzbar import pyzbar
    ZBAR_AVAILABLE = True
except ImportError:
    try:
        import pyzbar.pyzbar as pyzbar
        ZBAR_AVAILABLE = True
    except ImportError:
        ZBAR_AVAILABLE = False
        logging.warning("pyzbar not available. Install with: pip install pyzbar")

logger = logging.getLogger(__name__)


class QRAuth:
    """
    QR code authentication and validation system.
    """
    
    def __init__(self, secret_key: str = "default-secret-key"):
        """
        Initialize QR authentication system.
        
        Args:
            secret_key: Secret key for token generation
        """
        self.secret_key = secret_key
        
        if not ZBAR_AVAILABLE:
            logger.warning("QR code scanning requires pyzbar. Install with: pip install pyzbar")
        
        logger.info("QRAuth initialized")
    
    def generate_qr_code(
        self,
        customer_id: str,
        additional_data: Optional[Dict] = None
    ) -> Tuple[Image.Image, str]:
        """
        Generate QR code for customer entry.
        
        Args:
            customer_id: Customer identifier
            additional_data: Optional additional data to encode
        
        Returns:
            Tuple of (PIL Image, encoded token string)
        """
        # Create token
        token_data = {
            'customer_id': customer_id,
            'timestamp': int(time.time()),
            'data': additional_data or {}
        }
        
        # Create token string
        token_string = self._create_token(token_data)
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(token_string)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        logger.info(f"Generated QR code for customer {customer_id}")
        return img, token_string
    
    def generate_qr_image_bytes(
        self,
        customer_id: str,
        additional_data: Optional[Dict] = None
    ) -> bytes:
        """
        Generate QR code as image bytes.
        
        Args:
            customer_id: Customer identifier
            additional_data: Optional additional data
        
        Returns:
            QR code image as bytes (PNG format)
        """
        img, _ = self.generate_qr_code(customer_id, additional_data)
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def scan_qr_code(self, image: np.ndarray) -> Optional[str]:
        """
        Scan QR code from image.
        
        Args:
            image: Input image (BGR or RGB format)
        
        Returns:
            Decoded token string or None
        """
        if not ZBAR_AVAILABLE:
            logger.error("QR scanning requires pyzbar")
            return None
        
        # Convert to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image
        
        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_image)
        
        # Scan QR codes
        try:
            decoded_objects = pyzbar.decode(pil_image)
        except:
            # Fallback if pyzbar structure is different
            import pyzbar.pyzbar as pyzbar_module
            decoded_objects = pyzbar_module.decode(pil_image)
        
        if decoded_objects:
            # Return first QR code data
            token = decoded_objects[0].data.decode('utf-8')
            logger.debug(f"Scanned QR code: {token[:50]}...")
            return token
        
        return None
    
    def validate_token(self, token: str, max_age: int = 300) -> Optional[Dict]:
        """
        Validate QR token and extract customer data.
        
        Args:
            token: Token string from QR code
            max_age: Maximum token age in seconds
        
        Returns:
            Dictionary with customer data or None if invalid
        """
        try:
            # Decode token (simple base64 for now, could use JWT in production)
            decoded = base64.b64decode(token).decode('utf-8')
            
            # Parse token data (format: customer_id:timestamp:hash)
            parts = decoded.split(':')
            if len(parts) < 3:
                logger.warning("Invalid token format")
                return None
            
            customer_id = parts[0]
            timestamp = int(parts[1])
            token_hash = parts[2]
            
            # Verify token age
            current_time = int(time.time())
            if current_time - timestamp > max_age:
                logger.warning(f"Token expired (age: {current_time - timestamp}s)")
                return None
            
            # Verify hash
            expected_hash = self._compute_hash(customer_id, timestamp)
            if token_hash != expected_hash:
                logger.warning("Invalid token hash")
                return None
            
            return {
                'customer_id': customer_id,
                'timestamp': timestamp,
                'age': current_time - timestamp
            }
        
        except Exception as e:
            logger.error(f"Error validating token: {e}", exc_info=True)
            return None
    
    def _create_token(self, data: Dict) -> str:
        """Create encoded token from data."""
        customer_id = data['customer_id']
        timestamp = data['timestamp']
        
        # Compute hash
        token_hash = self._compute_hash(customer_id, timestamp)
        
        # Create token string
        token_string = f"{customer_id}:{timestamp}:{token_hash}"
        
        # Encode to base64
        encoded = base64.b64encode(token_string.encode('utf-8')).decode('utf-8')
        
        return encoded
    
    def _compute_hash(self, customer_id: str, timestamp: int) -> str:
        """Compute hash for token validation."""
        data = f"{customer_id}:{timestamp}:{self.secret_key}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()[:16]


class EntryGate:
    """
    Entry gate controller for customer authentication.
    """
    
    def __init__(self, qr_auth: QRAuth, gate_id: str = "main"):
        """
        Initialize entry gate.
        
        Args:
            qr_auth: QRAuth instance
            gate_id: Gate identifier
        """
        self.qr_auth = qr_auth
        self.gate_id = gate_id
        self.is_open = False
        self.last_entry_time = 0.0
        
        logger.info(f"EntryGate {gate_id} initialized")
    
    def scan_and_validate(self, image: np.ndarray) -> Optional[Dict]:
        """
        Scan QR code from image and validate.
        
        Args:
            image: Camera frame with QR code
        
        Returns:
            Customer data if valid, None otherwise
        """
        token = self.qr_auth.scan_qr_code(image)
        
        if not token:
            return None
        
        customer_data = self.qr_auth.validate_token(token)
        
        if customer_data:
            logger.info(f"Valid QR code scanned for customer {customer_data['customer_id']}")
        
        return customer_data
    
    def open_gate(self):
        """Open entry gate."""
        self.is_open = True
        self.last_entry_time = time.time()
        logger.info(f"Gate {self.gate_id} opened")
    
    def close_gate(self):
        """Close entry gate."""
        self.is_open = False
        logger.info(f"Gate {self.gate_id} closed")
    
    def process_entry(self, image: np.ndarray) -> Optional[str]:
        """
        Process entry attempt with QR code scanning.
        
        Args:
            image: Camera frame
        
        Returns:
            Customer ID if entry successful, None otherwise
        """
        customer_data = self.scan_and_validate(image)
        
        if customer_data:
            self.open_gate()
            # Auto-close after 2 seconds
            time.sleep(2)
            self.close_gate()
            return customer_data['customer_id']
        
        return None
