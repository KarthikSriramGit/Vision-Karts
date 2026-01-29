"""
Analytics Dashboard Module

Provides real-time analytics dashboard for monitoring store operations.
"""

import logging
import time
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AnalyticsDashboard:
    """
    Real-time analytics dashboard for store monitoring.
    """
    
    def __init__(
        self,
        metrics_collector,
        session_manager=None,
        cart_manager=None
    ):
        """
        Initialize analytics dashboard.
        
        Args:
            metrics_collector: MetricsCollector instance
            session_manager: Optional SessionManager instance
            cart_manager: Optional VirtualCartManager instance
        """
        self.metrics_collector = metrics_collector
        self.session_manager = session_manager
        self.cart_manager = cart_manager
        
        logger.info("AnalyticsDashboard initialized")
    
    def get_dashboard_data(self) -> Dict:
        """
        Get complete dashboard data.
        
        Returns:
            Dictionary with all dashboard metrics
        """
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'revenue': self.metrics_collector.get_revenue_stats(hours=24),
            'occupancy': self.metrics_collector.get_occupancy_stats(),
            'popular_products': self.metrics_collector.get_product_popularity(limit=10)
        }
        
        # Add session stats if available
        if self.session_manager:
            dashboard['sessions'] = self.session_manager.get_session_stats()
        
        # Add cart stats if available
        if self.cart_manager:
            dashboard['carts'] = self.cart_manager.get_cart_summary()
        
        return dashboard
    
    def get_realtime_stats(self) -> Dict:
        """Get real-time statistics."""
        return {
            'timestamp': time.time(),
            'revenue_1h': self.metrics_collector.get_revenue_stats(hours=1),
            'revenue_24h': self.metrics_collector.get_revenue_stats(hours=24),
            'occupancy': self.metrics_collector.get_occupancy_stats(),
            'top_products': self.metrics_collector.get_product_popularity(limit=5)
        }
    
    def get_performance_metrics(self) -> Dict:
        """Get system performance metrics."""
        # This would integrate with system monitoring
        return {
            'timestamp': time.time(),
            'system_health': 'good',  # Placeholder
            'camera_status': 'operational',  # Placeholder
            'processing_fps': 0.0  # Placeholder
        }
