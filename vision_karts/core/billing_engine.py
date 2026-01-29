"""
Billing Engine Module

Calculates total bill amount based on detected products using price database.
"""

import pandas as pd
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class BillingEngine:
    """
    Engine for calculating billing information from detected products.
    """
    
    def __init__(self, price_file: str):
        """
        Initialize billing engine with price database.
        
        Args:
            price_file: Path to CSV file with product prices.
                       Format: product_name,price
        """
        if not Path(price_file).exists():
            raise FileNotFoundError(f"Price file not found: {price_file}")
        
        self.price_df = pd.read_csv(price_file, header=None, names=['product', 'price'])
        self.price_dict = dict(zip(
            self.price_df['product'].str.lower(),
            self.price_df['price']
        ))
        
        logger.info(f"Loaded {len(self.price_dict)} products from price database")
    
    def calculate_price(self, product_name: str) -> float:
        """
        Get price for a product.
        
        Args:
            product_name: Name of the product (case-insensitive)
        
        Returns:
            Price as float, or 0.0 if product not found
        """
        product_key = product_name.lower()
        price = self.price_dict.get(product_key, 0.0)
        
        if price == 0.0:
            logger.warning(f"Product '{product_name}' not found in price database")
        
        return float(price)
    
    def generate_bill(
        self,
        detections: List[Dict],
        store_name: str = "Vision Karts Store"
    ) -> Dict:
        """
        Generate complete bill from product detections.
        
        Args:
            detections: List of detection dictionaries from ProductDetector
            store_name: Name of the store
        
        Returns:
            Dictionary containing:
                - 'store_name': str
                - 'items': List of item details
                - 'subtotal': float
                - 'total': float
                - 'item_count': int
        """
        items = []
        total = 0.0
        
        # Count products and calculate prices
        product_counts = {}
        for detection in detections:
            product_name = detection['class_name']
            if product_name not in product_counts:
                product_counts[product_name] = {
                    'count': 0,
                    'price': self.calculate_price(product_name),
                    'confidence': []
                }
            product_counts[product_name]['count'] += 1
            product_counts[product_name]['confidence'].append(detection['confidence'])
        
        # Build item list
        for product_name, info in product_counts.items():
            item_total = info['price'] * info['count']
            avg_confidence = sum(info['confidence']) / len(info['confidence'])
            
            items.append({
                'product': product_name,
                'quantity': info['count'],
                'unit_price': info['price'],
                'total': item_total,
                'avg_confidence': avg_confidence
            })
            total += item_total
        
        bill = {
            'store_name': store_name,
            'items': items,
            'subtotal': total,
            'total': round(total, 2),
            'item_count': sum(item['quantity'] for item in items)
        }
        
        return bill
    
    def format_bill(self, bill: Dict) -> str:
        """
        Format bill as printable string.
        
        Args:
            bill: Bill dictionary from generate_bill()
        
        Returns:
            Formatted bill string
        """
        lines = [
            f"{bill['store_name']}",
            "=" * 50,
            ""
        ]
        
        for item in bill['items']:
            lines.append(
                f"{item['quantity']}x {item['product']:<20} "
                f"${item['unit_price']:.2f} each = ${item['total']:.2f} "
                f"(confidence: {item['avg_confidence']:.2%})"
            )
        
        lines.extend([
            "",
            "-" * 50,
            f"Total Items: {bill['item_count']}",
            f"Total Amount: ${bill['total']:.2f}",
            "=" * 50
        ])
        
        return "\n".join(lines)
