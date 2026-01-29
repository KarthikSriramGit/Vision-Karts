"""
Report Generation Module

Generates analytics reports in various formats.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates analytics reports.
    """
    
    def __init__(
        self,
        metrics_collector,
        output_dir: str = "outputs/reports"
    ):
        """
        Initialize report generator.
        
        Args:
            metrics_collector: MetricsCollector instance
            output_dir: Directory to save reports
        """
        self.metrics_collector = metrics_collector
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ReportGenerator initialized (output_dir={output_dir})")
    
    def generate_daily_report(
        self,
        date: Optional[datetime] = None,
        format: str = 'json'
    ) -> Dict:
        """
        Generate daily sales report.
        
        Args:
            date: Report date (defaults to today)
            format: Report format ('json', 'text')
        
        Returns:
            Report data dictionary
        """
        if date is None:
            date = datetime.now()
        
        # Get metrics for the day
        start_time = date.replace(hour=0, minute=0, second=0).timestamp()
        end_time = date.replace(hour=23, minute=59, second=59).timestamp()
        
        revenue_stats = self.metrics_collector.get_revenue_stats(hours=24)
        popular_products = self.metrics_collector.get_product_popularity(limit=20)
        
        report = {
            'report_type': 'daily',
            'date': date.isoformat(),
            'period': {
                'start': datetime.fromtimestamp(start_time).isoformat(),
                'end': datetime.fromtimestamp(end_time).isoformat()
            },
            'revenue': revenue_stats,
            'popular_products': popular_products,
            'generated_at': datetime.now().isoformat()
        }
        
        # Save report
        if format == 'json':
            filename = f"daily_report_{date.strftime('%Y%m%d')}.json"
            file_path = self.output_dir / filename
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2)
            report['file_path'] = str(file_path)
        
        logger.info(f"Generated daily report for {date.strftime('%Y-%m-%d')}")
        return report
    
    def generate_sales_report(
        self,
        start_date: datetime,
        end_date: datetime,
        format: str = 'json'
    ) -> Dict:
        """
        Generate sales report for date range.
        
        Args:
            start_date: Start date
            end_date: End date
            format: Report format
        
        Returns:
            Report data dictionary
        """
        # Calculate hours in range
        hours = int((end_date - start_date).total_seconds() / 3600)
        
        revenue_stats = self.metrics_collector.get_revenue_stats(hours=hours)
        popular_products = self.metrics_collector.get_product_popularity(limit=50)
        
        report = {
            'report_type': 'sales',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'revenue': revenue_stats,
            'popular_products': popular_products,
            'generated_at': datetime.now().isoformat()
        }
        
        # Save report
        if format == 'json':
            filename = f"sales_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"
            file_path = self.output_dir / filename
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2)
            report['file_path'] = str(file_path)
        
        logger.info(f"Generated sales report for {start_date} to {end_date}")
        return report
