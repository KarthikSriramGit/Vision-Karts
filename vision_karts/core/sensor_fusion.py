"""
Sensor Fusion Module

Integrates weight sensors and other hardware sensors with computer vision.
"""

import logging
import time
import requests
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SensorReading:
    """Represents a sensor reading."""
    sensor_id: str
    value: float
    timestamp: float
    unit: str = "kg"
    confidence: float = 1.0


class WeightSensor:
    """
    Interface for weight sensor integration.
    """
    
    def __init__(
        self,
        sensor_id: str,
        api_endpoint: Optional[str] = None,
        simulated: bool = True
    ):
        """
        Initialize weight sensor.
        
        Args:
            sensor_id: Sensor identifier
            api_endpoint: API endpoint for sensor (if hardware)
            simulated: Whether to use simulated sensor
        """
        self.sensor_id = sensor_id
        self.api_endpoint = api_endpoint
        self.simulated = simulated
        self.last_reading: Optional[SensorReading] = None
        
        logger.info(f"WeightSensor {sensor_id} initialized (simulated={simulated})")
    
    def read(self) -> Optional[SensorReading]:
        """
        Read current sensor value.
        
        Returns:
            SensorReading or None if error
        """
        if self.simulated:
            # Simulate weight reading
            reading = SensorReading(
                sensor_id=self.sensor_id,
                value=0.0,  # Simulated
                timestamp=time.time()
            )
        else:
            # Read from API
            try:
                response = requests.get(self.api_endpoint, timeout=1.0)
                if response.status_code == 200:
                    data = response.json()
                    reading = SensorReading(
                        sensor_id=self.sensor_id,
                        value=data.get('weight', 0.0),
                        timestamp=time.time()
                    )
                else:
                    logger.warning(f"Failed to read sensor {self.sensor_id}: {response.status_code}")
                    return None
            except Exception as e:
                logger.error(f"Error reading sensor {self.sensor_id}: {e}")
                return None
        
        self.last_reading = reading
        return reading


class SensorFusion:
    """
    Fuses sensor data with computer vision detections.
    """
    
    def __init__(self, sensors: Optional[List[WeightSensor]] = None):
        """
        Initialize sensor fusion system.
        
        Args:
            sensors: List of WeightSensor instances
        """
        self.sensors: Dict[str, WeightSensor] = {}
        
        if sensors:
            for sensor in sensors:
                self.add_sensor(sensor)
        
        logger.info(f"SensorFusion initialized ({len(self.sensors)} sensors)")
    
    def add_sensor(self, sensor: WeightSensor):
        """Add a sensor to the fusion system."""
        self.sensors[sensor.sensor_id] = sensor
        logger.info(f"Added sensor {sensor.sensor_id}")
    
    def get_sensor_reading(self, sensor_id: str) -> Optional[SensorReading]:
        """Get reading from specific sensor."""
        sensor = self.sensors.get(sensor_id)
        if sensor:
            return sensor.read()
        return None
    
    def fuse_with_detections(
        self,
        sensor_id: str,
        detections: List[Dict],
        threshold: float = 0.1
    ) -> List[Dict]:
        """
        Fuse sensor data with product detections.
        
        Args:
            sensor_id: Sensor identifier
            detections: List of product detections
            threshold: Weight change threshold for validation
        
        Returns:
            Validated detections list
        """
        sensor = self.sensors.get(sensor_id)
        if not sensor:
            logger.warning(f"Sensor {sensor_id} not found")
            return detections
        
        reading = sensor.read()
        if not reading:
            return detections
        
        # Compare with previous reading
        if sensor.last_reading:
            weight_change = reading.value - sensor.last_reading.value
            
            # If weight increased, validate pick events
            # If weight decreased, validate return events
            if abs(weight_change) > threshold:
                logger.info(f"Sensor {sensor_id} detected weight change: {weight_change:.2f} kg")
                # Could enhance detections with sensor confidence
        
        return detections
    
    def get_all_readings(self) -> Dict[str, SensorReading]:
        """Get readings from all sensors."""
        readings = {}
        for sensor_id, sensor in self.sensors.items():
            reading = sensor.read()
            if reading:
                readings[sensor_id] = reading
        return readings
