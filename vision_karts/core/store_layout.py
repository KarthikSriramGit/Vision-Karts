"""
Store Layout Module

Manages store layout, zones, and spatial mapping for tracking.
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)


@dataclass
class Zone:
    """Represents a zone in the store."""
    name: str
    zone_type: str  # 'entrance', 'aisle', 'shelf', 'checkout', 'exit'
    bounds: List[List[float]]  # [[x1, y1], [x2, y2]] or polygon
    camera_ids: List[str] = None
    
    def __post_init__(self):
        if self.camera_ids is None:
            self.camera_ids = []
    
    def contains_point(self, x: float, y: float) -> bool:
        """
        Check if point is within zone bounds.
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Returns:
            True if point is in zone
        """
        if len(self.bounds) < 2:
            return False
        
        # Simple rectangle check (can be extended for polygons)
        if len(self.bounds) == 2:
            x1, y1 = self.bounds[0]
            x2, y2 = self.bounds[1]
            return x1 <= x <= x2 and y1 <= y <= y2
        
        # Polygon check (simplified)
        return True  # Placeholder for polygon implementation


@dataclass
class Shelf:
    """Represents a shelf with product locations."""
    shelf_id: str
    zone_name: str
    position: Tuple[float, float]
    products: List[str] = None
    
    def __post_init__(self):
        if self.products is None:
            self.products = []


class StoreLayout:
    """
    Manages store layout, zones, and spatial relationships.
    """
    
    def __init__(self, layout_file: Optional[str] = None):
        """
        Initialize store layout.
        
        Args:
            layout_file: Path to YAML layout configuration file
        """
        self.zones: Dict[str, Zone] = {}
        self.shelves: Dict[str, Shelf] = {}
        self.camera_positions: Dict[str, Tuple[float, float]] = {}
        
        if layout_file and Path(layout_file).exists():
            self.load_layout(layout_file)
        
        logger.info(f"StoreLayout initialized ({len(self.zones)} zones, {len(self.shelves)} shelves)")
    
    def load_layout(self, layout_file: str):
        """Load layout from YAML file."""
        try:
            with open(layout_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Load zones
            if 'zones' in config:
                for zone_data in config['zones']:
                    zone = Zone(
                        name=zone_data['name'],
                        zone_type=zone_data.get('type', 'general'),
                        bounds=zone_data['bounds'],
                        camera_ids=zone_data.get('cameras', [])
                    )
                    self.zones[zone.name] = zone
            
            # Load shelves
            if 'shelves' in config:
                for shelf_data in config['shelves']:
                    shelf = Shelf(
                        shelf_id=shelf_data['id'],
                        zone_name=shelf_data.get('zone', ''),
                        position=tuple(shelf_data['position']),
                        products=shelf_data.get('products', [])
                    )
                    self.shelves[shelf.shelf_id] = shelf
            
            # Load camera positions
            if 'cameras' in config:
                for cam_data in config['cameras']:
                    self.camera_positions[cam_data['id']] = tuple(cam_data.get('position', [0, 0]))
            
            logger.info(f"Loaded layout from {layout_file}")
        
        except Exception as e:
            logger.error(f"Error loading layout: {e}", exc_info=True)
    
    def add_zone(
        self,
        name: str,
        zone_type: str,
        bounds: List[List[float]],
        camera_ids: Optional[List[str]] = None
    ):
        """Add a zone to the layout."""
        zone = Zone(
            name=name,
            zone_type=zone_type,
            bounds=bounds,
            camera_ids=camera_ids or []
        )
        self.zones[name] = zone
        logger.info(f"Added zone: {name}")
    
    def get_zone(self, name: str) -> Optional[Zone]:
        """Get zone by name."""
        return self.zones.get(name)
    
    def find_zone_for_point(self, x: float, y: float) -> Optional[Zone]:
        """
        Find zone containing a point.
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Returns:
            Zone containing point or None
        """
        for zone in self.zones.values():
            if zone.contains_point(x, y):
                return zone
        return None
    
    def get_zones_by_type(self, zone_type: str) -> List[Zone]:
        """Get all zones of a specific type."""
        return [z for z in self.zones.values() if z.zone_type == zone_type]
    
    def add_shelf(
        self,
        shelf_id: str,
        zone_name: str,
        position: Tuple[float, float],
        products: Optional[List[str]] = None
    ):
        """Add a shelf to the layout."""
        shelf = Shelf(
            shelf_id=shelf_id,
            zone_name=zone_name,
            position=position,
            products=products or []
        )
        self.shelves[shelf_id] = shelf
        logger.info(f"Added shelf: {shelf_id}")
    
    def get_shelf(self, shelf_id: str) -> Optional[Shelf]:
        """Get shelf by ID."""
        return self.shelves.get(shelf_id)
    
    def get_shelves_in_zone(self, zone_name: str) -> List[Shelf]:
        """Get all shelves in a zone."""
        return [s for s in self.shelves.values() if s.zone_name == zone_name]
    
    def set_camera_position(self, camera_id: str, position: Tuple[float, float]):
        """Set camera position in store coordinates."""
        self.camera_positions[camera_id] = position
    
    def get_camera_position(self, camera_id: str) -> Optional[Tuple[float, float]]:
        """Get camera position."""
        return self.camera_positions.get(camera_id)
    
    def to_dict(self) -> Dict:
        """Convert layout to dictionary."""
        return {
            'zones': [
                {
                    'name': z.name,
                    'type': z.zone_type,
                    'bounds': z.bounds,
                    'cameras': z.camera_ids
                }
                for z in self.zones.values()
            ],
            'shelves': [
                {
                    'id': s.shelf_id,
                    'zone': s.zone_name,
                    'position': list(s.position),
                    'products': s.products
                }
                for s in self.shelves.values()
            ],
            'cameras': [
                {
                    'id': cam_id,
                    'position': list(pos)
                }
                for cam_id, pos in self.camera_positions.items()
            ]
        }
