# Vision Karts Architecture Documentation

## System Overview

Vision Karts is a comprehensive automated checkout system built with modular architecture for scalability and maintainability.

## Component Architecture

### Core Components

#### Product Detection Layer
- **ProductDetector**: YOLO11-based object detection
- **FrameProcessor**: Frame-by-frame processing pipeline
- **VideoProcessor**: Real-time video stream handling

#### Customer Management Layer
- **CustomerTracker**: Face recognition and tracking
- **CustomerDB**: Customer profile management
- **SessionManager**: Session lifecycle management

#### Cart & Billing Layer
- **VirtualCartManager**: Per-customer cart management
- **BillingEngine**: Price calculation and bill generation
- **EventTracker**: Product interaction tracking

#### Entry/Exit Layer
- **QRAuth**: QR code authentication
- **EntryGate**: Entry gate control
- **ExitProcessor**: Exit processing and finalization

#### Payment & Receipt Layer
- **PaymentProcessor**: Payment processing
- **ReceiptGenerator**: Multi-format receipt generation

#### Infrastructure Layer
- **CameraManager**: Multi-camera coordination
- **StoreLayout**: Spatial mapping and zones
- **SensorFusion**: Hardware sensor integration
- **Database**: Data persistence layer

#### Analytics Layer
- **MetricsCollector**: Metrics aggregation
- **AnalyticsDashboard**: Real-time dashboard
- **ReportGenerator**: Report generation

## Data Flow

```
Entry → QR Scan → Session Creation → Cart Creation
  ↓
Video Processing → Product Detection → Event Tracking
  ↓
Cart Updates → Virtual Cart Management
  ↓
Exit Detection → Cart Finalization → Payment Processing
  ↓
Receipt Generation → Transaction Storage
```

## Module Dependencies

```
core/
├── product_detector.py (depends on: accelerators)
├── video_processor.py (depends on: product_detector)
├── camera_manager.py (depends on: video_processor)
├── virtual_cart.py (depends on: billing_engine)
├── session_manager.py (standalone)
├── qr_auth.py (standalone)
├── customer_db.py (standalone)
├── event_tracker.py (standalone)
├── exit_processor.py (depends on: payment_processor, receipt_generator)
├── receipt_generator.py (standalone)
├── payment_processor.py (depends on: customer_db)
├── store_layout.py (standalone)
└── sensor_fusion.py (standalone)

analytics/
├── metrics.py (standalone)
├── dashboard.py (depends on: metrics)
└── reports.py (depends on: metrics)

data/
├── database.py (standalone)
└── models.py (optional SQLAlchemy)
```

## Configuration System

Configuration is managed through YAML files:
- `configs/default_config.yaml`: Main configuration
- `configs/store_map.yaml`: Store layout definition

## Database Schema

- **customers**: Customer profiles
- **sessions**: Shopping sessions
- **transactions**: Completed transactions
- **transaction_items**: Transaction line items
- **analytics_events**: Analytics metrics

## Performance Considerations

- Multi-threading for video processing
- Frame buffering to prevent blocking
- Batch processing for multiple cameras
- Database connection pooling
- Metrics aggregation for efficiency

## Extension Points

- Custom product detectors
- Additional sensor types
- Payment gateway integrations
- Receipt delivery methods
- Analytics plugins
