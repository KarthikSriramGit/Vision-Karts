# Vision Karts Core Package

This package contains the core functionality for the Vision Karts automated checkout system.

## Modules

### Core Modules

- **`product_detector.py`** - YOLOv8-based product detection with AI acceleration support
- **`billing_engine.py`** - Bill calculation and formatting engine
- **`customer_tracker.py`** - Face recognition and customer tracking

### Accelerators

- **`accelerator_manager.py`** - AI acceleration backend management (TensorRT, ONNX Runtime)

### Utils

- **`image_utils.py`** - Image loading and preprocessing utilities
- **`config_loader.py`** - Configuration file loading

## Usage

```python
from vision_karts.core import ProductDetector, BillingEngine
from vision_karts.utils import load_image

# Initialize detector
detector = ProductDetector(use_acceleration=True)

# Detect products
image = load_image("cart.jpg")
detections, annotated = detector.detect(image, return_image=True)

# Calculate bill
billing = BillingEngine("prices.csv")
bill = billing.generate_bill(detections)
```

## Requirements

See main `requirements.txt` for dependencies.
