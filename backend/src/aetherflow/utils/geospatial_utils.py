"""
Geospatial Utilities for AetherFlow
"""

import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

from aetherflow.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Point:
    """Geographic point with latitude and longitude"""
    latitude: float
    longitude: float
    
    def __post_init__(self):
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Invalid latitude: {self.latitude}")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Invalid longitude: {self.longitude}")


@dataclass
class BoundingBox:
    """Geographic bounding box"""
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float
    
    def __post_init__(self):
        if self.min_lat >= self.max_lat:
            raise ValueError("min_lat must be less than max_lat")
        if self.min_lon >= self.max_lon:
            raise ValueError("min_lon must be less than max_lon")


class GeospatialUtils:
    """Geospatial utility functions for location-based operations"""
    
    # Earth's radius in kilometers
    EARTH_RADIUS_KM = 6371.0
    
    @staticmethod
    def haversine_distance(point1: Point, point2: Point) -> float:
        """Calculate distance between two points using Haversine formula (in km)"""
        
        # Convert latitude and longitude from degrees to radians
        lat1_rad = math.radians(point1.latitude)
        lon1_rad = math.radians(point1.longitude)
        lat2_rad = math.radians(point2.latitude)
        lon2_rad = math.radians(point2.longitude)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return GeospatialUtils.EARTH_RADIUS_KM * c
    
    @staticmethod
    def bearing(point1: Point, point2: Point) -> float:
        """Calculate bearing from point1 to point2 (in degrees)"""
        
        lat1_rad = math.radians(point1.latitude)
        lat2_rad = math.radians(point2.latitude)
        dlon_rad = math.radians(point2.longitude - point1.longitude)
        
        y = math.sin(dlon_rad) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad))
        
        bearing_rad = math.atan2(y, x)
        bearing_deg = math.degrees(bearing_rad)
        
        # Normalize to 0-360 degrees
        return (bearing_deg + 360) % 360
    
    @staticmethod
    def destination_point(point: Point, distance_km: float, bearing_deg: float) -> Point:
        """Calculate destination point given start point, distance, and bearing"""
        
        lat1_rad = math.radians(point.latitude)
        lon1_rad = math.radians(point.longitude)
        bearing_rad = math.radians(bearing_deg)
        
        angular_distance = distance_km / GeospatialUtils.EARTH_RADIUS_KM
        
        lat2_rad = math.asin(
            math.sin(lat1_rad) * math.cos(angular_distance) +
            math.cos(lat1_rad) * math.sin(angular_distance) * math.cos(bearing_rad)
        )
        
        lon2_rad = lon1_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat1_rad),
            math.cos(angular_distance) - math.sin(lat1_rad) * math.sin(lat2_rad)
        )
        
        return Point(
            latitude=math.degrees(lat2_rad),
            longitude=math.degrees(lon2_rad)
        )
    
    @staticmethod
    def point_in_bounding_box(point: Point, bbox: BoundingBox) -> bool:
        """Check if point is within bounding box"""
        
        return (bbox.min_lat <= point.latitude <= bbox.max_lat and
                bbox.min_lon <= point.longitude <= bbox.max_lon)
    
    @staticmethod
    def create_bounding_box_around_point(point: Point, radius_km: float) -> BoundingBox:
        """Create bounding box around a point with given radius"""
        
        # Calculate approximate degree offsets
        lat_offset = radius_km / 111.0  # Approximately 111 km per degree of latitude
        
        # Longitude offset varies with latitude
        lon_offset = radius_km / (111.0 * math.cos(math.radians(point.latitude)))
        
        return BoundingBox(
            min_lat=point.latitude - lat_offset,
            max_lat=point.latitude + lat_offset,
            min_lon=point.longitude - lon_offset,
            max_lon=point.longitude + lon_offset
        )
    
    @staticmethod
    def points_within_radius(
        center: Point,
        points: List[Point],
        radius_km: float
    ) -> List[Tuple[Point, float]]:
        """Find all points within radius of center point"""
        
        result = []
        
        for point in points:
            distance = GeospatialUtils.haversine_distance(center, point)
            if distance <= radius_km:
                result.append((point, distance))
        
        # Sort by distance
        result.sort(key=lambda x: x[1])
        
        return result
    
    @staticmethod
    def calculate_area_km2(bbox: BoundingBox) -> float:
        """Calculate approximate area of bounding box in square kilometers"""
        
        # Create corner points
        sw = Point(bbox.min_lat, bbox.min_lon)
        se = Point(bbox.min_lat, bbox.max_lon)
        nw = Point(bbox.max_lat, bbox.min_lon)
        
        # Calculate width and height
        width_km = GeospatialUtils.haversine_distance(sw, se)
        height_km = GeospatialUtils.haversine_distance(sw, nw)
        
        return width_km * height_km
    
    @staticmethod
    def center_of_bounding_box(bbox: BoundingBox) -> Point:
        """Calculate center point of bounding box"""
        
        center_lat = (bbox.min_lat + bbox.max_lat) / 2
        center_lon = (bbox.min_lon + bbox.max_lon) / 2
        
        return Point(center_lat, center_lon)
    
    @staticmethod
    def expand_bounding_box(bbox: BoundingBox, expansion_km: float) -> BoundingBox:
        """Expand bounding box by given distance in all directions"""
        
        center = GeospatialUtils.center_of_bounding_box(bbox)
        
        # Calculate expansion in degrees
        lat_expansion = expansion_km / 111.0
        lon_expansion = expansion_km / (111.0 * math.cos(math.radians(center.latitude)))
        
        return BoundingBox(
            min_lat=bbox.min_lat - lat_expansion,
            max_lat=bbox.max_lat + lat_expansion,
            min_lon=bbox.min_lon - lon_expansion,
            max_lon=bbox.max_lon + lon_expansion
        )
    
    @staticmethod
    def calculate_speed_kmh(
        point1: Point,
        point2: Point,
        time_diff_seconds: float
    ) -> float:
        """Calculate speed between two points given time difference"""
        
        if time_diff_seconds <= 0:
            return 0.0
        
        distance_km = GeospatialUtils.haversine_distance(point1, point2)
        time_hours = time_diff_seconds / 3600.0
        
        return distance_km / time_hours
    
    @staticmethod
    def is_valid_urban_location(point: Point) -> bool:
        """Check if point is likely in an urban area (basic heuristic)"""
        
        # This is a simplified check - in production, you'd use actual urban area datasets
        
        # Exclude obvious non-urban areas (middle of oceans, polar regions)
        if abs(point.latitude) > 80:  # Polar regions
            return False
        
        # Very rough ocean check (this would need proper land/sea datasets)
        if (abs(point.latitude) < 5 and abs(point.longitude) < 5):  # Near equator/prime meridian
            return False
        
        return True
    
    @staticmethod
    def cluster_points_by_proximity(
        points: List[Point],
        max_distance_km: float
    ) -> List[List[Point]]:
        """Cluster points based on proximity"""
        
        if not points:
            return []
        
        clusters = []
        remaining_points = points.copy()
        
        while remaining_points:
            # Start new cluster with first remaining point
            current_cluster = [remaining_points.pop(0)]
            
            # Find all points within distance of any point in current cluster
            changed = True
            while changed:
                changed = False
                points_to_remove = []
                
                for i, point in enumerate(remaining_points):
                    for cluster_point in current_cluster:
                        if GeospatialUtils.haversine_distance(point, cluster_point) <= max_distance_km:
                            current_cluster.append(point)
                            points_to_remove.append(i)
                            changed = True
                            break
                
                # Remove points that were added to cluster
                for i in reversed(points_to_remove):
                    remaining_points.pop(i)
            
            clusters.append(current_cluster)
        
        return clusters
    
    @staticmethod
    def calculate_route_distance(points: List[Point]) -> float:
        """Calculate total distance of a route through multiple points"""
        
        if len(points) < 2:
            return 0.0
        
        total_distance = 0.0
        
        for i in range(len(points) - 1):
            total_distance += GeospatialUtils.haversine_distance(points[i], points[i + 1])
        
        return total_distance
    
    @staticmethod
    def simplify_route(
        points: List[Point],
        tolerance_km: float = 0.1
    ) -> List[Point]:
        """Simplify route by removing points that are too close together"""
        
        if len(points) <= 2:
            return points
        
        simplified = [points[0]]  # Always keep first point
        
        for i in range(1, len(points) - 1):
            # Check distance to last kept point
            if GeospatialUtils.haversine_distance(simplified[-1], points[i]) >= tolerance_km:
                simplified.append(points[i])
        
        simplified.append(points[-1])  # Always keep last point
        
        return simplified
    
    @staticmethod
    def interpolate_point(point1: Point, point2: Point, fraction: float) -> Point:
        """Interpolate point between two points (fraction 0.0 to 1.0)"""
        
        if not 0.0 <= fraction <= 1.0:
            raise ValueError("Fraction must be between 0.0 and 1.0")
        
        lat = point1.latitude + fraction * (point2.latitude - point1.latitude)
        lon = point1.longitude + fraction * (point2.longitude - point1.longitude)
        
        return Point(lat, lon)
    
    @staticmethod
    def get_intersection_bounds(
        intersection_point: Point,
        radius_meters: float = 200
    ) -> BoundingBox:
        """Get bounding box around an intersection for traffic analysis"""
        
        radius_km = radius_meters / 1000.0
        return GeospatialUtils.create_bounding_box_around_point(intersection_point, radius_km)
    
    @staticmethod
    def calculate_traffic_density(
        vehicle_points: List[Point],
        area_bbox: BoundingBox
    ) -> float:
        """Calculate traffic density (vehicles per km²) in an area"""
        
        # Count vehicles in area
        vehicles_in_area = sum(
            1 for point in vehicle_points
            if GeospatialUtils.point_in_bounding_box(point, area_bbox)
        )
        
        # Calculate area
        area_km2 = GeospatialUtils.calculate_area_km2(area_bbox)
        
        if area_km2 == 0:
            return 0.0
        
        return vehicles_in_area / area_km2
    
    @staticmethod
    def find_nearest_intersection(
        vehicle_point: Point,
        intersection_points: List[Point]
    ) -> Tuple[Optional[Point], float]:
        """Find nearest intersection to a vehicle location"""
        
        if not intersection_points:
            return None, float('inf')
        
        nearest_intersection = None
        min_distance = float('inf')
        
        for intersection in intersection_points:
            distance = GeospatialUtils.haversine_distance(vehicle_point, intersection)
            if distance < min_distance:
                min_distance = distance
                nearest_intersection = intersection
        
        return nearest_intersection, min_distance
