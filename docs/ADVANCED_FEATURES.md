# Advanced Features Documentation

This document provides detailed documentation for Vision Karts advanced features.

## Table of Contents

1. [Real-Time Video Processing](#real-time-video-processing)
2. [Virtual Cart Management](#virtual-cart-management)
3. [QR Code Authentication](#qr-code-authentication)
4. [Session Management](#session-management)
5. [Product Event Tracking](#product-event-tracking)
6. [Store Layout System](#store-layout-system)
7. [Analytics & Reporting](#analytics--reporting)
8. [Receipt Generation](#receipt-generation)
9. [Sensor Fusion](#sensor-fusion)
10. [Database Persistence](#database-persistence)

## Real-Time Video Processing

The video processing system enables real-time analysis of camera feeds for automated checkout.

### Features

- Multi-camera support
- Threaded frame capture and processing
- Configurable frame buffering
- Real-time FPS monitoring
- Frame queue management

### Usage

```python
from vision_karts.core import VideoProcessor, FrameProcessor, ProductDetector

# Initialize detector
detector = ProductDetector()
processor = FrameProcessor(detector)

# Process video stream
with VideoProcessor(camera_id=0, fps=30) as vp:
    while True:
        frame, timestamp = vp.get_frame(timeout=1.0)
        if frame is not None:
            results = processor.process_frame(frame, timestamp)
            print(f"Detected {len(results['detections'])} products")
```

### Multi-Camera Setup

```python
from vision_karts.core import CameraManager, FrameProcessor

cameras = [
    {'id': 0, 'name': 'Entrance', 'fps': 30},
    {'id': 1, 'name': 'Aisle 1', 'fps': 30}
]

processor = FrameProcessor(detector)
camera_mgr = CameraManager(cameras, processor)

camera_mgr.start_all()

# Get frames from all cameras
all_frames = camera_mgr.get_all_frames()
```

## Virtual Cart Management

Virtual carts track customer selections in real-time without physical carts.

### Features

- Per-customer cart isolation
- Real-time quantity tracking
- Automatic price calculation
- Cart persistence
- Confidence-based item tracking

### Usage

```python
from vision_karts.core import VirtualCartManager, BillingEngine

billing = BillingEngine("prices.csv")
cart_mgr = VirtualCartManager(price_calculator=billing.calculate_price)

# Create cart
cart = cart_mgr.create_cart("customer_123", "session_456")

# Update from detections
cart_mgr.update_cart_from_detections("customer_123", detections, 'pick')

# Get cart summary
summary = cart_mgr.get_cart_summary()
```

## QR Code Authentication

QR code system provides secure customer entry and identification.

### Features

- QR code generation
- Token-based authentication
- Entry gate control
- Customer registration

### Usage

```python
from vision_karts.core import QRAuth, EntryGate

qr_auth = QRAuth(secret_key="your-secret-key")

# Generate QR code
qr_image, token = qr_auth.generate_qr_code("customer_123")

# Entry gate processing
gate = EntryGate(qr_auth)
customer_id = gate.process_entry(camera_frame)
```

## Session Management

Session manager tracks customer journey from entry to exit.

### Features

- Session lifecycle tracking
- Entry/exit monitoring
- Session timeout handling
- Multi-session support

### Usage

```python
from vision_karts.core import SessionManager

session_mgr = SessionManager()

# Create session on entry
session = session_mgr.create_session("customer_123", entry_camera="cam_0")

# Mark exiting
session_mgr.mark_exiting(session.session_id, exit_camera="cam_3")

# Complete session
completed = session_mgr.complete_session(session.session_id)
```

## Product Event Tracking

Event tracker identifies product pick and return actions.

### Features

- Temporal analysis
- Pick/return detection
- Event history
- Confidence validation

### Usage

```python
from vision_karts.core import EventTracker

tracker = EventTracker()

# Process detections
events = tracker.process_detections(
    customer_id="customer_123",
    detections=detections,
    timestamp=time.time()
)

# Get recent events
picks = tracker.get_recent_events(
    customer_id="customer_123",
    event_type="pick"
)
```

## Store Layout System

Store layout system manages spatial relationships and zones.

### Features

- Zone definitions
- Shelf mapping
- Camera positioning
- Spatial queries

### Usage

```python
from vision_karts.core import StoreLayout

layout = StoreLayout("configs/store_map.yaml")

# Find zone for position
zone = layout.find_zone_for_point(10.5, 5.2)

# Get shelves in zone
shelves = layout.get_shelves_in_zone("Aisle 1")
```

## Analytics & Reporting

Analytics system provides business intelligence and reporting.

### Features

- Real-time metrics
- Revenue analytics
- Product popularity
- Automated reports

### Usage

```python
from vision_karts.analytics import MetricsCollector, ReportGenerator

metrics = MetricsCollector()

# Record metrics
metrics.record_transaction("txn_123", "customer_123", 45.99, 5)

# Generate reports
reporter = ReportGenerator(metrics)
daily_report = reporter.generate_daily_report()
```

## Receipt Generation

Automated receipt generation in multiple formats.

### Features

- PDF, text, JSON formats
- Automatic generation
- Email/SMS support (configurable)
- Transaction history

### Usage

```python
from vision_karts.core import ReceiptGenerator

receipt_gen = ReceiptGenerator()

receipt = receipt_gen.generate_receipt(
    customer_id="customer_123",
    session_id="session_456",
    cart_data=cart.to_dict(),
    format="pdf"
)
```

## Sensor Fusion

Integrates hardware sensors with computer vision.

### Features

- Weight sensor support
- Multi-sensor fusion
- Hardware API integration
- Simulated sensors

### Usage

```python
from vision_karts.core import SensorFusion, WeightSensor

sensor = WeightSensor("shelf_a1", simulated=True)
fusion = SensorFusion([sensor])

# Fuse with detections
validated = fusion.fuse_with_detections("shelf_a1", detections)
```

## Database Persistence

Database layer for transaction and customer data storage.

### Features

- SQLite (default)
- PostgreSQL/MySQL support
- Transaction history
- Customer profiles

### Usage

```python
from vision_karts.data import Database

db = Database("data/vision_karts.db")

# Execute queries
results = db.execute_query(
    "SELECT * FROM transactions WHERE customer_id = ?",
    ("customer_123",)
)
```
