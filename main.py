#!/usr/bin/env python3
"""
Vision Karts - Main Entry Point

Next-generation automated checkout system using state-of-the-art computer vision.
"""

import argparse
import logging
import sys
from pathlib import Path
import cv2

from vision_karts.core import ProductDetector, BillingEngine, CustomerTracker
from vision_karts.utils import load_image, visualize_detections

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for Vision Karts checkout system."""
    parser = argparse.ArgumentParser(
        description='Vision Karts - Automated Checkout System'
    )
    parser.add_argument(
        'image_path',
        type=str,
        help='Path to input image'
    )
    parser.add_argument(
        '--model',
        type=str,
        default=None,
        help='Path to custom YOLOv8 model (optional)'
    )
    parser.add_argument(
        '--prices',
        type=str,
        default='src/prices.csv',
        help='Path to price database CSV file'
    )
    parser.add_argument(
        '--confidence',
        type=float,
        default=0.5,
        help='Confidence threshold for detections (0.0-1.0)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Path to save annotated output image'
    )
    parser.add_argument(
        '--store-name',
        type=str,
        default='Vision Karts Store',
        help='Store name for billing'
    )
    parser.add_argument(
        '--no-acceleration',
        action='store_true',
        help='Disable AI acceleration'
    )
    parser.add_argument(
        '--device',
        type=str,
        default='auto',
        help='Device to use (auto, cpu, cuda, 0, 1, etc.)'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not Path(args.image_path).exists():
        logger.error(f"Image not found: {args.image_path}")
        sys.exit(1)
    
    if not Path(args.prices).exists():
        logger.error(f"Price file not found: {args.prices}")
        sys.exit(1)
    
    try:
        # Initialize components
        logger.info("Initializing Vision Karts system...")
        
        detector = ProductDetector(
            model_path=args.model,
            confidence_threshold=args.confidence,
            use_acceleration=not args.no_acceleration,
            device=args.device
        )
        
        billing_engine = BillingEngine(args.prices)
        
        # Load and process image
        logger.info(f"Processing image: {args.image_path}")
        image = load_image(args.image_path)
        
        # Detect products
        detections, annotated_image = detector.detect(image, return_image=True)
        
        logger.info(f"Detected {len(detections)} products")
        
        # Generate bill
        bill = billing_engine.generate_bill(detections, args.store_name)
        
        # Print bill
        print("\n" + billing_engine.format_bill(bill) + "\n")
        
        # Save annotated image if requested
        if args.output:
            cv2.imwrite(args.output, annotated_image)
            logger.info(f"Saved annotated image to: {args.output}")
        
        logger.info("Processing complete!")
        
    except Exception as e:
        logger.error(f"Error during processing: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
