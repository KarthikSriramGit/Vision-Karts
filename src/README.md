# Source Data Directory

This directory contains source data files for the Vision Karts system.

## Files

- **`prices.csv`** - Product price database (format: product_name,price)
- **`dataset.zip`** - Sample dataset archive (if available)

## Price Database Format

The `prices.csv` file should follow this format:

```csv
product_name,price
kitkat,2.99
hershey,5.00
reese,2.99
pringle,1.67
maggie,0.57
cheetos,1.59
```

## Usage

The price database is automatically loaded by the `BillingEngine` class:

```python
from vision_karts.core import BillingEngine

billing = BillingEngine("src/prices.csv")
```

## Notes

- Product names are case-insensitive
- Prices should be numeric values
- Missing products will default to $0.00
