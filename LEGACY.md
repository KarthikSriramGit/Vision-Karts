# Legacy Code Reference

## billing.ipynb

The `billing.ipynb` file contains the original implementation using RetinaNet. This notebook is kept for reference purposes only.

**Note:** The current Vision Karts system has been completely rewritten using:
- YOLOv8 instead of RetinaNet
- Modern Python modules instead of Jupyter notebooks
- AI acceleration support
- Professional code structure

For current usage, see the main `README.md` and use the `vision_karts` Python package.

## Migration Guide

If you have code or models based on the old RetinaNet implementation:

1. **Models**: Retrain using YOLOv8 (see `trained-model/README.md`)
2. **Code**: Use the new `vision_karts` package modules:
   - `ProductDetector` replaces RetinaNet inference
   - `BillingEngine` replaces manual price calculation
   - `CustomerTracker` replaces FaceNet implementation
3. **Notebooks**: Convert to Python scripts using the new modular structure

## Key Differences

| Old (RetinaNet) | New (YOLOv8) |
|----------------|--------------|
| RetinaNet + ResNet50 | YOLOv8 (various sizes) |
| Keras/TensorFlow 1.x | PyTorch/Ultralytics |
| Jupyter notebook | Python modules |
| No acceleration | TensorRT/ONNX Runtime |
| Manual setup | pip install |
