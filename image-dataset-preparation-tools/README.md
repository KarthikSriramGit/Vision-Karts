# Image Dataset Preparation Tools

Utilities for preparing image datasets for training computer vision models.

## Tools

### VGG to Pascal VOC Converter

The `vgg2pascal_voc_utility.ipynb` notebook provides functionality to convert VGG Image Annotator format annotations to Pascal VOC XML format, which is compatible with YOLOv8 training pipelines.

### Files

- **`vgg2pascal_voc_utility.ipynb`** - Jupyter notebook for format conversion
- **`pascal_voc_ref.xml`** - Reference Pascal VOC XML structure
- **`vgg_annotations.csv`** - Sample VGG annotation format

## Usage

1. Open `vgg2pascal_voc_utility.ipynb` in Jupyter
2. Load your VGG annotations CSV file
3. Run the conversion cells
4. Export Pascal VOC XML files for each image

## Output Format

The converter generates Pascal VOC XML files compatible with:
- YOLOv8 training pipelines
- Standard object detection frameworks
- Vision Karts model training workflows

## Notes

- Ensure image paths are correctly specified
- Bounding box coordinates are automatically validated
- Output XML files follow Pascal VOC standard format
