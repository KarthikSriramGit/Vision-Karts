# Legacy RetinaNet Directory

**Note:** This directory contains legacy RetinaNet implementation references. The current Vision Karts system uses YOLOv8 for superior performance and accuracy.

## Migration

If you have existing RetinaNet models, consider migrating to YOLOv8:

1. Export your RetinaNet annotations to YOLO format
2. Retrain using YOLOv8 (see `trained-model/README.md`)
3. Update your code to use `ProductDetector` from `vision_karts.core`

## Current System

The Vision Karts system now uses:
- **YOLOv8** for object detection (Ultralytics)
- **Modern face recognition** for customer tracking
- **AI acceleration** via TensorRT/ONNX Runtime

See the main README for usage instructions.
