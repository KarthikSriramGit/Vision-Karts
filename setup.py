"""Setup script for Vision Karts."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="vision-karts",
    version="2.1.0",
    author="Vision Karts Team",
    author_email="support@vision-karts.ai",
    description=(
        "Computer-vision powered retail checkout: YOLO11 product detection, "
        "virtual carts, billing, and analytics for smart stores"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vision-karts/vision-karts",
    project_urls={
        "Documentation": "https://github.com/vision-karts/vision-karts#readme",
        "Source": "https://github.com/vision-karts/vision-karts",
        "Tracker": "https://github.com/vision-karts/vision-karts/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords=[
        "computer-vision",
        "object-detection",
        "yolo11",
        "retail",
        "checkout",
        "smart-store",
        "self-checkout",
        "virtual-cart",
        "billing",
        "analytics",
    ],
    python_requires=">=3.8",
    install_requires=[
        "ultralytics>=8.3.0",
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
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "vision-karts=main:main",
        ],
    },
)
