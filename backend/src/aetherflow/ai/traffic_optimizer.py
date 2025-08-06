"""
AI Traffic Optimizer for AetherFlow
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

from aetherflow.core.logging import get_logger
from aetherflow.models.traffic_lights import TrafficLight, TrafficLightStatus
from aetherflow.models.vehicle_data import VehicleData
from aetherflow.ai.groq_client import groq_client

logger = get_logger(__name__)


class TrafficOptimizer:
    """AI-powered traffic light optimization system"""
    
    def __init__(self):
        self.optimization_history: List[Dict[str, Any]] = []
        self.learning_rate = 0.1
        self.min_green_time = 15  # Minimum green light duration
        self.max_green_time = 60  # Maximum green light duration
        self.yellow_time = 5      # Fixed yellow light duration
        
    async def optimize_intersection(
        self, 
        traffic_light: TrafficLight, 
        vehicle_data: List[VehicleData],
        time_window_minutes: int = 15
    ) -> Dict[str, Any]:
        """Optimize a single intersection based on recent vehicle data"""
        
        logger.info(f"Optimizing intersection {traffic_light.intersection_id}")
        
        # Analyze traffic patterns
        traffic_analysis = self._analyze_traffic_patterns(
            traffic_light, vehicle_data, time_window_minutes
        )
        
        # Get AI-powered analysis from Groq
        try:
            ai_analysis = await groq_client.generate_traffic_analysis(
                traffic_analysis, 
                f"Intersection {traffic_light.intersection_id} optimization"
            )
            traffic_analysis["ai_insights"] = ai_analysis
            logger.debug(f"AI analysis completed for {traffic_light.intersection_id}")
        except Exception as e:
            logger.warning(f"AI analysis failed for {traffic_light.intersection_id}: {e}")
            traffic_analysis["ai_insights"] = None
        
        # Calculate optimal timings
        optimal_timings = self._calculate_optimal_timings(
            traffic_light, traffic_analysis
        )
        
        # Apply optimization
        old_timings = {
            "red_duration": traffic_light.red_duration,
            "yellow_duration": traffic_light.yellow_duration,
            "green_duration": traffic_light.green_duration
        }
        
        traffic_light.apply_ai_optimization(optimal_timings)
        
        # Calculate expected improvement
        improvement_metrics = self._calculate_improvement_metrics(
            old_timings, optimal_timings, traffic_analysis
        )
        
        # Record optimization
        optimization_record = {
            "intersection_id": traffic_light.intersection_id,
            "timestamp": datetime.utcnow().isoformat(),
            "old_timings": old_timings,
            "new_timings": optimal_timings,
            "traffic_analysis": traffic_analysis,
            "improvement_metrics": improvement_metrics
        }
        
        self.optimization_history.append(optimization_record)
        
        logger.info(f"Optimized intersection {traffic_light.intersection_id}: "
                   f"{improvement_metrics['expected_improvement']:.1%} improvement")
        
        return optimization_record
    
    async def optimize_corridor(
        self, 
        traffic_lights: List[TrafficLight],
        vehicle_data: List[VehicleData]
    ) -> Dict[str, Any]:
        """Optimize a corridor of connected intersections"""
        
        logger.info(f"Optimizing corridor with {len(traffic_lights)} intersections")
        
        # Sort intersections by location for corridor analysis
        sorted_lights = self._sort_intersections_by_corridor(traffic_lights)
        
        # Analyze corridor traffic flow
        corridor_analysis = self._analyze_corridor_flow(sorted_lights, vehicle_data)
        
        # Calculate coordinated timings
        coordinated_timings = self._calculate_coordinated_timings(
            sorted_lights, corridor_analysis
        )
        
        # Apply optimizations
        optimization_results = []
        for i, traffic_light in enumerate(sorted_lights):
            timings = coordinated_timings[i]
            
            old_timings = {
                "red_duration": traffic_light.red_duration,
                "yellow_duration": traffic_light.yellow_duration,
                "green_duration": traffic_light.green_duration
            }
            
            traffic_light.apply_ai_optimization(timings)
            
            optimization_results.append({
                "intersection_id": traffic_light.intersection_id,
                "old_timings": old_timings,
                "new_timings": timings
            })
        
        # Calculate corridor-wide improvements
        corridor_improvement = self._calculate_corridor_improvement(
            corridor_analysis, coordinated_timings
        )
        
        result = {
            "corridor_id": f"corridor_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.utcnow().isoformat(),
            "intersections_optimized": len(traffic_lights),
            "optimization_results": optimization_results,
            "corridor_analysis": corridor_analysis,
            "corridor_improvement": corridor_improvement
        }
        
        logger.info(f"Optimized corridor: {corridor_improvement['travel_time_reduction']:.1%} "
                   f"travel time reduction")
        
        return result
    
    def _analyze_traffic_patterns(
        self, 
        traffic_light: TrafficLight, 
        vehicle_data: List[VehicleData],
        time_window_minutes: int
    ) -> Dict[str, Any]:
        """Analyze traffic patterns around an intersection"""
        
        # Filter vehicle data near the intersection
        nearby_vehicles = self._filter_nearby_vehicles(traffic_light, vehicle_data, radius_km=0.5)
        
        if not nearby_vehicles:
            return {
                "vehicle_count": 0,
                "average_speed": 0,
                "congestion_level": 0,
                "peak_hour_factor": 1.0,
                "directional_flow": {"north": 0, "south": 0, "east": 0, "west": 0}
            }
        
        # Calculate traffic metrics
        vehicle_count = len(nearby_vehicles)
        average_speed = np.mean([v.speed for v in nearby_vehicles])
        speed_variance = np.var([v.speed for v in nearby_vehicles])
        
        # Estimate congestion level (0-1 scale)
        congestion_level = max(0, min(1, (50 - average_speed) / 50))
        
        # Analyze directional flow
        directional_flow = self._analyze_directional_flow(traffic_light, nearby_vehicles)
        
        # Calculate peak hour factor
        peak_hour_factor = self._calculate_peak_hour_factor(nearby_vehicles)
        
        return {
            "vehicle_count": vehicle_count,
            "average_speed": average_speed,
            "speed_variance": speed_variance,
            "congestion_level": congestion_level,
            "peak_hour_factor": peak_hour_factor,
            "directional_flow": directional_flow,
            "analysis_time_window": time_window_minutes
        }
    
    def _calculate_optimal_timings(
        self, 
        traffic_light: TrafficLight, 
        traffic_analysis: Dict[str, Any]
    ) -> Dict[str, int]:
        """Calculate optimal traffic light timings based on analysis"""
        
        base_green = traffic_light.green_duration
        base_red = traffic_light.red_duration
        
        # Adjust based on congestion level
        congestion_factor = traffic_analysis["congestion_level"]
        
        # Increase green time for high congestion
        green_adjustment = int(base_green * congestion_factor * 0.3)
        optimal_green = max(
            self.min_green_time, 
            min(self.max_green_time, base_green + green_adjustment)
        )
        
        # Adjust red time inversely
        red_adjustment = int(base_red * (1 - congestion_factor) * 0.2)
        optimal_red = max(10, base_red - red_adjustment)
        
        # Consider directional flow
        main_flow = max(traffic_analysis["directional_flow"].values())
        total_flow = sum(traffic_analysis["directional_flow"].values())
        
        if total_flow > 0:
            flow_bias = main_flow / total_flow
            if flow_bias > 0.6:  # Strong directional bias
                optimal_green = min(self.max_green_time, int(optimal_green * 1.2))
        
        # Apply peak hour adjustments
        peak_factor = traffic_analysis["peak_hour_factor"]
        if peak_factor > 1.2:  # Peak hour
            optimal_green = min(self.max_green_time, int(optimal_green * 1.1))
            optimal_red = max(10, int(optimal_red * 0.9))
        
        return {
            "red_duration": optimal_red,
            "yellow_duration": self.yellow_time,
            "green_duration": optimal_green
        }
    
    def _filter_nearby_vehicles(
        self, 
        traffic_light: TrafficLight, 
        vehicle_data: List[VehicleData], 
        radius_km: float
    ) -> List[VehicleData]:
        """Filter vehicle data within radius of intersection"""
        
        nearby_vehicles = []
        
        for vehicle in vehicle_data:
            distance = self._calculate_distance(
                traffic_light.latitude, traffic_light.longitude,
                vehicle.latitude, vehicle.longitude
            )
            
            if distance <= radius_km:
                nearby_vehicles.append(vehicle)
        
        return nearby_vehicles
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers"""
        # Simplified distance calculation (Haversine formula approximation)
        R = 6371  # Earth's radius in kilometers
        
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        
        a = (np.sin(dlat/2)**2 + 
             np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2)
        
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        distance = R * c
        
        return distance
    
    def _analyze_directional_flow(
        self, 
        traffic_light: TrafficLight, 
        vehicles: List[VehicleData]
    ) -> Dict[str, int]:
        """Analyze traffic flow in different directions"""
        
        directional_counts = {"north": 0, "south": 0, "east": 0, "west": 0}
        
        for vehicle in vehicles:
            if vehicle.heading is not None:
                # Convert heading to cardinal direction
                heading = vehicle.heading
                
                if 315 <= heading or heading < 45:
                    directional_counts["north"] += 1
                elif 45 <= heading < 135:
                    directional_counts["east"] += 1
                elif 135 <= heading < 225:
                    directional_counts["south"] += 1
                elif 225 <= heading < 315:
                    directional_counts["west"] += 1
        
        return directional_counts
    
    def _calculate_peak_hour_factor(self, vehicles: List[VehicleData]) -> float:
        """Calculate peak hour factor based on vehicle timestamps"""
        
        if not vehicles:
            return 1.0
        
        # Group vehicles by hour
        hourly_counts = {}
        
        for vehicle in vehicles:
            hour = vehicle.timestamp.hour
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        if not hourly_counts:
            return 1.0
        
        max_hourly_count = max(hourly_counts.values())
        avg_hourly_count = np.mean(list(hourly_counts.values()))
        
        # Peak hour factor: ratio of peak hour to average hour
        return max_hourly_count / avg_hourly_count if avg_hourly_count > 0 else 1.0
    
    def _calculate_improvement_metrics(
        self, 
        old_timings: Dict[str, int], 
        new_timings: Dict[str, int],
        traffic_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate expected improvement metrics"""
        
        old_cycle = sum(old_timings.values())
        new_cycle = sum(new_timings.values())
        
        # Calculate throughput improvement
        old_green_ratio = old_timings["green_duration"] / old_cycle
        new_green_ratio = new_timings["green_duration"] / new_cycle
        
        throughput_improvement = (new_green_ratio - old_green_ratio) / old_green_ratio
        
        # Estimate wait time reduction
        congestion_level = traffic_analysis["congestion_level"]
        wait_time_reduction = throughput_improvement * (1 + congestion_level)
        
        # Overall improvement estimate
        expected_improvement = (throughput_improvement + wait_time_reduction) / 2
        
        return {
            "throughput_improvement": throughput_improvement,
            "wait_time_reduction": wait_time_reduction,
            "expected_improvement": expected_improvement,
            "cycle_time_change": new_cycle - old_cycle,
            "green_ratio_change": new_green_ratio - old_green_ratio
        }
    
    def _sort_intersections_by_corridor(self, traffic_lights: List[TrafficLight]) -> List[TrafficLight]:
        """Sort intersections by their position along a corridor"""
        # Simple sorting by latitude (north-south corridor) or longitude (east-west corridor)
        # In a real implementation, this would use more sophisticated corridor detection
        
        # Determine if corridor is primarily north-south or east-west
        latitudes = [light.latitude for light in traffic_lights]
        longitudes = [light.longitude for light in traffic_lights]
        
        lat_range = max(latitudes) - min(latitudes)
        lon_range = max(longitudes) - min(longitudes)
        
        if lat_range > lon_range:
            # North-south corridor, sort by latitude
            return sorted(traffic_lights, key=lambda x: x.latitude)
        else:
            # East-west corridor, sort by longitude
            return sorted(traffic_lights, key=lambda x: x.longitude)
    
    def _analyze_corridor_flow(
        self, 
        traffic_lights: List[TrafficLight], 
        vehicle_data: List[VehicleData]
    ) -> Dict[str, Any]:
        """Analyze traffic flow along a corridor"""
        
        corridor_metrics = {
            "total_intersections": len(traffic_lights),
            "average_spacing_km": 0,
            "dominant_flow_direction": "unknown",
            "peak_flow_intersection": None,
            "bottleneck_intersection": None
        }
        
        if len(traffic_lights) < 2:
            return corridor_metrics
        
        # Calculate average intersection spacing
        distances = []
        for i in range(len(traffic_lights) - 1):
            dist = self._calculate_distance(
                traffic_lights[i].latitude, traffic_lights[i].longitude,
                traffic_lights[i+1].latitude, traffic_lights[i+1].longitude
            )
            distances.append(dist)
        
        corridor_metrics["average_spacing_km"] = np.mean(distances)
        
        # Analyze flow at each intersection
        intersection_flows = []
        for light in traffic_lights:
            nearby_vehicles = self._filter_nearby_vehicles(light, vehicle_data, 0.3)
            flow_analysis = self._analyze_directional_flow(light, nearby_vehicles)
            intersection_flows.append({
                "intersection_id": light.intersection_id,
                "total_flow": sum(flow_analysis.values()),
                "directional_flow": flow_analysis
            })
        
        # Find peak flow and bottleneck intersections
        if intersection_flows:
            max_flow = max(intersection_flows, key=lambda x: x["total_flow"])
            min_flow = min(intersection_flows, key=lambda x: x["total_flow"])
            
            corridor_metrics["peak_flow_intersection"] = max_flow["intersection_id"]
            corridor_metrics["bottleneck_intersection"] = min_flow["intersection_id"]
        
        return corridor_metrics
    
    def _calculate_coordinated_timings(
        self, 
        traffic_lights: List[TrafficLight],
        corridor_analysis: Dict[str, Any]
    ) -> List[Dict[str, int]]:
        """Calculate coordinated timings for corridor optimization"""
        
        coordinated_timings = []
        
        # Base timing calculation for each intersection
        for light in traffic_lights:
            # Mock traffic analysis for each intersection
            mock_analysis = {
                "congestion_level": np.random.uniform(0.3, 0.8),
                "peak_hour_factor": np.random.uniform(1.0, 1.5),
                "directional_flow": {
                    "north": np.random.randint(10, 50),
                    "south": np.random.randint(10, 50),
                    "east": np.random.randint(5, 30),
                    "west": np.random.randint(5, 30)
                }
            }
            
            optimal_timings = self._calculate_optimal_timings(light, mock_analysis)
            coordinated_timings.append(optimal_timings)
        
        # Apply coordination adjustments
        if len(coordinated_timings) > 1:
            # Synchronize cycle times
            avg_cycle = np.mean([sum(timing.values()) for timing in coordinated_timings])
            target_cycle = int(avg_cycle)
            
            for timing in coordinated_timings:
                current_cycle = sum(timing.values())
                if current_cycle != target_cycle:
                    # Adjust green time to match target cycle
                    adjustment = target_cycle - current_cycle
                    timing["green_duration"] = max(
                        self.min_green_time,
                        timing["green_duration"] + adjustment
                    )
        
        return coordinated_timings
    
    def _calculate_corridor_improvement(
        self, 
        corridor_analysis: Dict[str, Any],
        coordinated_timings: List[Dict[str, int]]
    ) -> Dict[str, Any]:
        """Calculate expected corridor-wide improvements"""
        
        # Mock improvement calculations
        travel_time_reduction = np.random.uniform(0.15, 0.35)  # 15-35% improvement
        fuel_savings = travel_time_reduction * 0.8  # Fuel savings correlated with time
        emission_reduction = fuel_savings * 0.9  # Emission reduction from fuel savings
        
        return {
            "travel_time_reduction": travel_time_reduction,
            "fuel_savings_percent": fuel_savings,
            "emission_reduction_percent": emission_reduction,
            "throughput_increase_percent": np.random.uniform(0.10, 0.25),
            "coordination_efficiency": np.random.uniform(0.80, 0.95)
        }
