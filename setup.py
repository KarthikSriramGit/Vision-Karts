"""Setup script for Vision Karts."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="vision-karts",
    version="2.0.0",
    author="Vision Karts Team",
    description="Next-generation automated checkout system using state-of-the-art computer vision",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vision-karts/vision-karts",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "ultralytics>=8.0.0",
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "Pillow>=10.0.0",
        "face-recognition>=1.3.0",
        "dlib>=19.24.0",
        "pandas>=2.0.0",
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "acceleration": [
            "onnxruntime>=1.15.0",
        ],
        "gpu": [
            "onnxruntime-gpu>=1.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "vision-karts=main:main",
        ],
    },
)
