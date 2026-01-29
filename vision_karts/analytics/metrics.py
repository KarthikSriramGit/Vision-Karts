"""
Metrics Collection Module

Collects and aggregates business metrics and analytics.
"""

import logging
import time
from typing import Dict, List, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    """Represents a metric value."""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}


class MetricsCollector:
    """
    Collects and aggregates metrics for analytics.
    """
    
    def __init__(self, retention_days: int = 30):
        """
        Initialize metrics collector.
        
        Args:
            retention_days: Number of days to retain metrics
        """
        self.retention_days = retention_days
        self.metrics: deque = deque(maxlen=100000)  # Limit memory usage
        self.aggregated: Dict[str, List[float]] = defaultdict(list)
        
        logger.info(f"MetricsCollector initialized (retention={retention_days} days)")
    
    def record_metric(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Record a metric.
        
        Args:
            name: Metric name
            value: Metric value
            tags: Optional tags for filtering
        """
        metric = Metric(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {}
        )
        
        self.metrics.append(metric)
        self.aggregated[name].append(value)
        
        # Keep only recent values (limit memory)
        if len(self.aggregated[name]) > 10000:
            self.aggregated[name] = self.aggregated[name][-5000:]
    
    def record_transaction(
        self,
        transaction_id: str,
        customer_id: str,
        amount: float,
        item_count: int
    ):
        """Record a transaction metric."""
        self.record_metric('transaction.amount', amount, {'customer_id': customer_id})
        self.record_metric('transaction.items', item_count, {'customer_id': customer_id})
        self.record_metric('transaction.count', 1.0)
    
    def record_session(
        self,
        session_id: str,
        customer_id: str,
        duration: float
    ):
        """Record a session metric."""
        self.record_metric('session.duration', duration, {'customer_id': customer_id})
        self.record_metric('session.count', 1.0)
    
    def record_product_detection(
        self,
        product_name: str,
        confidence: float,
        camera_id: Optional[str] = None
    ):
        """Record product detection metric."""
        tags = {'product': product_name}
        if camera_id:
            tags['camera'] = camera_id
        
        self.record_metric('product.detection', confidence, tags)
    
    def get_metric_stats(
        self,
        metric_name: str,
        since: Optional[float] = None
    ) -> Dict:
        """
        Get statistics for a metric.
        
        Args:
            metric_name: Metric name
            since: Only include metrics after this timestamp
        
        Returns:
            Dictionary with statistics
        """
        values = [
            m.value for m in self.metrics
            if m.name == metric_name and (since is None or m.timestamp >= since)
        ]
        
        if not values:
            return {
                'count': 0,
                'sum': 0.0,
                'avg': 0.0,
                'min': 0.0,
                'max': 0.0
            }
        
        return {
            'count': len(values),
            'sum': sum(values),
            'avg': sum(values) / len(values),
            'min': min(values),
            'max': max(values)
        }
    
    def get_revenue_stats(self, hours: int = 24) -> Dict:
        """Get revenue statistics for specified hours."""
        since = time.time() - (hours * 3600)
        
        amount_stats = self.get_metric_stats('transaction.amount', since)
        count_stats = self.get_metric_stats('transaction.count', since)
        
        return {
            'period_hours': hours,
            'total_revenue': amount_stats['sum'],
            'transaction_count': int(count_stats['sum']),
            'average_transaction': amount_stats['avg'],
            'min_transaction': amount_stats['min'],
            'max_transaction': amount_stats['max']
        }
    
    def get_occupancy_stats(self) -> Dict:
        """Get current store occupancy statistics."""
        active_sessions = self.get_metric_stats('session.count', since=time.time() - 3600)
        
        return {
            'active_customers': int(active_sessions['sum']),
            'timestamp': time.time()
        }
    
    def get_product_popularity(self, limit: int = 10) -> List[Dict]:
        """Get most popular products."""
        product_counts = defaultdict(int)
        
        for metric in self.metrics:
            if metric.name == 'product.detection' and 'product' in metric.tags:
                product_name = metric.tags['product']
                product_counts[product_name] += 1
        
        # Sort by count
        sorted_products = sorted(
            product_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {'product': name, 'detections': count}
            for name, count in sorted_products
        ]
    
    def cleanup_old_metrics(self):
        """Remove metrics older than retention period."""
        cutoff_time = time.time() - (self.retention_days * 86400)
        
        # Remove old metrics
        while self.metrics and self.metrics[0].timestamp < cutoff_time:
            self.metrics.popleft()
        
        logger.debug(f"Cleaned up metrics older than {self.retention_days} days")
