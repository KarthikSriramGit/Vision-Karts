# Trained Models Directory

This directory contains trained YOLO11 models for product detection.

## Model Format

Models should be saved in YOLO11 format (`.pt` files) and can be loaded directly by the `ProductDetector` class.

## Usage

```python
from vision_karts.core import ProductDetector

# Load custom trained model
detector = ProductDetector(model_path="trained-model/custom_yolo11.pt")
```

## Model Training

To train a custom YOLO11 model for your product dataset:

1. Prepare your dataset in YOLO format
2. Create a dataset configuration file (`dataset.yaml`)
3. Train using Ultralytics YOLO11:

```bash
yolo train data=dataset.yaml model=yolo11n.pt epochs=100 imgsz=640
```

## Model Performance

For best results:
- Use yolo11m or yolo11l for higher accuracy
- Train for at least 100 epochs
- Use data augmentation
- Validate on a separate test set

## Notes

- Models trained on product datasets should be optimized for your specific product categories
- Consider using transfer learning from COCO pretrained weights
- Model size vs. accuracy trade-off: larger models (yolo11l, yolo11x) provide better accuracy but slower inference
