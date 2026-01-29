#!/usr/bin/env python3
"""
Example usage of Vision Karts system.

This script demonstrates how to use the Vision Karts automated checkout system.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vision_karts.core import ProductDetector, BillingEngine, CustomerTracker
from vision_karts.utils import load_image, visualize_detections
import cv2


def example_product_detection():
    """Example: Detect products in an image."""
    print("=" * 60)
    print("Example 1: Product Detection")
    print("=" * 60)
    
    # Initialize detector
    detector = ProductDetector(
        confidence_threshold=0.5,
        use_acceleration=True,
        device='auto'
    )
    
    # Load image (replace with your image path)
    image_path = "path/to/your/image.jpg"
    if not Path(image_path).exists():
        print(f"Image not found: {image_path}")
        print("Please update the image_path variable with a valid image.")
        return
    
    image = load_image(image_path)
    
    # Detect products
    detections, annotated_image = detector.detect(image, return_image=True)
    
    print(f"\nDetected {len(detections)} products:")
    for i, detection in enumerate(detections, 1):
        print(f"  {i}. {detection['class_name']} "
              f"(confidence: {detection['confidence']:.2%})")
    
    # Save annotated image
    cv2.imwrite("output_detections.jpg", annotated_image)
    print("\nAnnotated image saved to: output_detections.jpg")


def example_billing():
    """Example: Generate bill from product detections."""
    print("\n" + "=" * 60)
    print("Example 2: Billing Calculation")
    print("=" * 60)
    
    # Initialize components
    detector = ProductDetector(confidence_threshold=0.5)
    billing = BillingEngine("src/prices.csv")
    
    # Load and detect
    image_path = "path/to/your/image.jpg"
    if not Path(image_path).exists():
        print(f"Image not found: {image_path}")
        return
    
    image = load_image(image_path)
    detections, _ = detector.detect(image)
    
    # Generate bill
    bill = billing.generate_bill(detections, store_name="Vision Karts Store")
    
    # Print formatted bill
    print("\n" + billing.format_bill(bill))


def example_customer_tracking():
    """Example: Track customers using face recognition."""
    print("\n" + "=" * 60)
    print("Example 3: Customer Tracking")
    print("=" * 60)
    
    # Initialize tracker (requires known_faces directory)
    known_faces_dir = "data/customers/"  # Update with your directory
    
    if not Path(known_faces_dir).exists():
        print(f"Known faces directory not found: {known_faces_dir}")
        print("Skipping customer tracking example.")
        return
    
    tracker = CustomerTracker(known_faces_dir=known_faces_dir)
    
    # Load image
    image_path = "path/to/store_image.jpg"
    if not Path(image_path).exists():
        print(f"Image not found: {image_path}")
        return
    
    image = cv2.imread(image_path)
    
    # Track customers
    customers = tracker.track_customers(image)
    
    print(f"\nDetected {len(customers)} customers:")
    for i, customer in enumerate(customers, 1):
        if customer['customer_id']:
            print(f"  {i}. Customer ID: {customer['customer_id']} "
                  f"(confidence: {customer.get('confidence', 0):.2%})")
        else:
            print(f"  {i}. Unknown customer")


def example_complete_checkout():
    """Example: Complete checkout flow."""
    print("\n" + "=" * 60)
    print("Example 4: Complete Checkout Flow")
    print("=" * 60)
    
    # Initialize all components
    detector = ProductDetector(
        confidence_threshold=0.5,
        use_acceleration=True
    )
    billing = BillingEngine("src/prices.csv")
    
    # Process image
    image_path = "path/to/shopping_cart.jpg"
    if not Path(image_path).exists():
        print(f"Image not found: {image_path}")
        return
    
    print(f"\nProcessing image: {image_path}")
    image = load_image(image_path)
    
    # Detect products
    detections, annotated = detector.detect(image, return_image=True)
    print(f"Detected {len(detections)} product instances")
    
    # Generate bill
    bill = billing.generate_bill(detections)
    
    # Display results
    print("\n" + billing.format_bill(bill))
    
    # Save annotated image
    output_path = "checkout_result.jpg"
    cv2.imwrite(output_path, annotated)
    print(f"\nAnnotated image saved to: {output_path}")


if __name__ == "__main__":
    print("\nVision Karts - Usage Examples")
    print("=" * 60)
    print("\nNote: Update image paths in the examples before running.")
    print("\nRunning examples...\n")
    
    # Run examples
    try:
        example_product_detection()
    except Exception as e:
        print(f"Error in example 1: {e}")
    
    try:
        example_billing()
    except Exception as e:
        print(f"Error in example 2: {e}")
    
    try:
        example_customer_tracking()
    except Exception as e:
        print(f"Error in example 3: {e}")
    
    try:
        example_complete_checkout()
    except Exception as e:
        print(f"Error in example 4: {e}")
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
