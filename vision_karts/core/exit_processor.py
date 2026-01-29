"""
Exit Processing Module

Handles customer exit, cart finalization, and checkout processing.
"""

import logging
import time
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ExitProcessor:
    """
    Processes customer exit and finalizes transactions.
    """
    
    def __init__(
        self,
        payment_processor=None,
        receipt_generator=None
    ):
        """
        Initialize exit processor.
        
        Args:
            payment_processor: PaymentProcessor instance
            receipt_generator: ReceiptGenerator instance
        """
        self.payment_processor = payment_processor
        self.receipt_generator = receipt_generator
        
        logger.info("ExitProcessor initialized")
    
    def process_exit(
        self,
        session_id: str,
        customer_id: str,
        cart_data: Dict,
        exit_camera: Optional[str] = None
    ) -> Dict:
        """
        Process customer exit and complete transaction.
        
        Args:
            session_id: Session identifier
            customer_id: Customer identifier
            cart_data: Cart data dictionary
            exit_camera: Camera ID where customer exited
        
        Returns:
            Dictionary with transaction details
        """
        logger.info(f"Processing exit for customer {customer_id} (session {session_id})")
        
        # Finalize cart
        total_amount = cart_data.get('total_amount', 0.0)
        items = cart_data.get('items', [])
        
        # Process payment
        payment_result = None
        if self.payment_processor and total_amount > 0:
            payment_result = self.payment_processor.process_payment(
                customer_id=customer_id,
                amount=total_amount,
                items=items
            )
        
        # Generate receipt
        receipt = None
        if self.receipt_generator:
            receipt = self.receipt_generator.generate_receipt(
                customer_id=customer_id,
                session_id=session_id,
                cart_data=cart_data,
                payment_result=payment_result
            )
        
        transaction = {
            'transaction_id': f"TXN-{int(time.time())}-{customer_id}",
            'session_id': session_id,
            'customer_id': customer_id,
            'timestamp': datetime.now().isoformat(),
            'total_amount': total_amount,
            'item_count': sum(item.get('quantity', 0) for item in items),
            'items': items,
            'payment_status': payment_result.get('status') if payment_result else 'pending',
            'receipt': receipt,
            'exit_camera': exit_camera
        }
        
        logger.info(f"Exit processed: Transaction {transaction['transaction_id']}, Amount: ${total_amount:.2f}")
        
        return transaction
