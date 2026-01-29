# Image Dataset Preparation Tools

Utilities for preparing image datasets for training computer vision models.

## Tools

### VGG to Pascal VOC Converter

Reference files for converting VGG Image Annotator format annotations to Pascal VOC XML format, which is compatible with YOLO11 training pipelines.

### Files

- **`pascal_voc_ref.xml`** - Reference Pascal VOC XML structure
- **`vgg_annotations.csv`** - Sample VGG annotation format

## Usage

1. Use the reference XML structure (`pascal_voc_ref.xml`) as a template
2. Load your VGG annotations CSV file (see `vgg_annotations.csv` for format)
3. Convert annotations to Pascal VOC XML format following the reference structure
4. Export Pascal VOC XML files for each image

## Output Format

The converter generates Pascal VOC XML files compatible with:
- YOLO11 training pipelines
- Standard object detection frameworks
- Vision Karts model training workflows

## Notes

- Ensure image paths are correctly specified
- Bounding box coordinates are automatically validated
- Output XML files follow Pascal VOC standard format
