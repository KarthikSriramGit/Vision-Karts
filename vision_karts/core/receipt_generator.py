"""
Receipt Generation Module

Generates electronic receipts in various formats (PDF, email, SMS).
"""

import logging
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("reportlab not available. Install with: pip install reportlab")

logger = logging.getLogger(__name__)


class ReceiptGenerator:
    """
    Generates electronic receipts in multiple formats.
    """
    
    def __init__(self, output_dir: str = "outputs/receipts"):
        """
        Initialize receipt generator.
        
        Args:
            output_dir: Directory to save receipts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ReceiptGenerator initialized (output_dir={output_dir})")
    
    def generate_receipt(
        self,
        customer_id: str,
        session_id: str,
        cart_data: Dict,
        payment_result: Optional[Dict] = None,
        store_name: str = "Vision Karts Store",
        format: str = "pdf"
    ) -> Dict:
        """
        Generate receipt for transaction.
        
        Args:
            customer_id: Customer identifier
            session_id: Session identifier
            cart_data: Cart data dictionary
            payment_result: Payment processing result
            store_name: Store name
            format: Receipt format ('pdf', 'text', 'json')
        
        Returns:
            Dictionary with receipt information
        """
        timestamp = datetime.now()
        receipt_id = f"RCP-{int(timestamp.timestamp())}-{customer_id}"
        
        receipt_data = {
            'receipt_id': receipt_id,
            'store_name': store_name,
            'customer_id': customer_id,
            'session_id': session_id,
            'timestamp': timestamp.isoformat(),
            'items': cart_data.get('items', []),
            'subtotal': cart_data.get('subtotal', 0.0),
            'total': cart_data.get('total_amount', 0.0),
            'item_count': cart_data.get('item_count', 0),
            'payment_status': payment_result.get('status') if payment_result else 'pending',
            'payment_method': payment_result.get('method') if payment_result else None
        }
        
        # Generate in requested format
        if format == 'pdf' and REPORTLAB_AVAILABLE:
            file_path = self._generate_pdf(receipt_data, store_name)
            receipt_data['file_path'] = str(file_path)
        elif format == 'text':
            file_path = self._generate_text(receipt_data, store_name)
            receipt_data['file_path'] = str(file_path)
        elif format == 'json':
            file_path = self._generate_json(receipt_data)
            receipt_data['file_path'] = str(file_path)
        
        logger.info(f"Generated receipt {receipt_id} ({format})")
        return receipt_data
    
    def _generate_pdf(self, receipt_data: Dict, store_name: str) -> Path:
        """Generate PDF receipt."""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab required for PDF generation")
        
        filename = f"{receipt_data['receipt_id']}.pdf"
        file_path = self.output_dir / filename
        
        doc = SimpleDocTemplate(str(file_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"<b>{store_name}</b>", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Receipt info
        info_text = f"""
        Receipt ID: {receipt_data['receipt_id']}<br/>
        Customer: {receipt_data['customer_id']}<br/>
        Date: {receipt_data['timestamp']}<br/>
        """
        info = Paragraph(info_text, styles['Normal'])
        story.append(info)
        story.append(Spacer(1, 0.2*inch))
        
        # Items table
        data = [['Product', 'Qty', 'Unit Price', 'Total']]
        for item in receipt_data['items']:
            data.append([
                item['product'],
                str(item['quantity']),
                f"${item['unit_price']:.2f}",
                f"${item['total']:.2f}"
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
        # Total
        total_text = f"<b>Total: ${receipt_data['total']:.2f}</b>"
        total = Paragraph(total_text, styles['Normal'])
        story.append(total)
        
        # Payment status
        if receipt_data.get('payment_status'):
            payment_text = f"Payment Status: {receipt_data['payment_status']}"
            payment = Paragraph(payment_text, styles['Normal'])
            story.append(payment)
        
        doc.build(story)
        return file_path
    
    def _generate_text(self, receipt_data: Dict, store_name: str) -> Path:
        """Generate text receipt."""
        filename = f"{receipt_data['receipt_id']}.txt"
        file_path = self.output_dir / filename
        
        lines = [
            "=" * 50,
            store_name,
            "=" * 50,
            f"Receipt ID: {receipt_data['receipt_id']}",
            f"Customer: {receipt_data['customer_id']}",
            f"Date: {receipt_data['timestamp']}",
            "-" * 50,
            ""
        ]
        
        for item in receipt_data['items']:
            lines.append(
                f"{item['quantity']}x {item['product']:<20} "
                f"${item['unit_price']:.2f} each = ${item['total']:.2f}"
            )
        
        lines.extend([
            "",
            "-" * 50,
            f"Total: ${receipt_data['total']:.2f}",
            f"Payment Status: {receipt_data.get('payment_status', 'pending')}",
            "=" * 50
        ])
        
        with open(file_path, 'w') as f:
            f.write('\n'.join(lines))
        
        return file_path
    
    def _generate_json(self, receipt_data: Dict) -> Path:
        """Generate JSON receipt."""
        import json
        
        filename = f"{receipt_data['receipt_id']}.json"
        file_path = self.output_dir / filename
        
        with open(file_path, 'w') as f:
            json.dump(receipt_data, f, indent=2)
        
        return file_path
