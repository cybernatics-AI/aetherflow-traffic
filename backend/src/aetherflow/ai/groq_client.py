"""
Groq API Client for AetherFlow AI Services
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import httpx

from aetherflow.core.config import get_settings
from aetherflow.core.logging import get_logger

logger = get_logger(__name__)


class GroqClient:
    """Client for Groq API integration"""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.groq_api_key
        self.model = getattr(self.settings, 'groq_model', 'llama3-8b-8192')
        self.max_tokens = getattr(self.settings, 'groq_max_tokens', 4096)
        self.temperature = getattr(self.settings, 'groq_temperature', 0.1)
        self.base_url = "https://api.groq.com/openai/v1"
        
        if not self.api_key:
            logger.warning("Groq API key not configured, AI features will be limited")
    
    async def generate_traffic_analysis(
        self, 
        traffic_data: Dict[str, Any],
        context: str = ""
    ) -> Dict[str, Any]:
        """Generate traffic analysis using Groq AI"""
        
        if not self.api_key:
            return self._mock_traffic_analysis(traffic_data)
        
        try:
            prompt = self._build_traffic_analysis_prompt(traffic_data, context)
            
            response = await self._make_api_request(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert traffic engineer and data analyst. Provide detailed, actionable traffic analysis based on the provided data."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            if response and "choices" in response:
                analysis_text = response["choices"][0]["message"]["content"]
                return self._parse_traffic_analysis(analysis_text, traffic_data)
            else:
                logger.error("Invalid response from Groq API")
                return self._mock_traffic_analysis(traffic_data)
                
        except Exception as e:
            logger.error(f"Groq API request failed: {e}")
            return self._mock_traffic_analysis(traffic_data)
    
    async def generate_optimization_recommendations(
        self,
        intersection_data: Dict[str, Any],
        historical_performance: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate traffic optimization recommendations"""
        
        if not self.api_key:
            return self._mock_optimization_recommendations(intersection_data)
        
        try:
            prompt = self._build_optimization_prompt(intersection_data, historical_performance)
            
            response = await self._make_api_request(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a traffic optimization expert. Analyze intersection data and provide specific, implementable recommendations for improving traffic flow."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            if response and "choices" in response:
                recommendations_text = response["choices"][0]["message"]["content"]
                return self._parse_optimization_recommendations(recommendations_text)
            else:
                return self._mock_optimization_recommendations(intersection_data)
                
        except Exception as e:
            logger.error(f"Groq optimization request failed: {e}")
            return self._mock_optimization_recommendations(intersection_data)
    
    async def analyze_congestion_patterns(
        self,
        vehicle_data: List[Dict[str, Any]],
        time_window: str = "1h"
    ) -> Dict[str, Any]:
        """Analyze congestion patterns using AI"""
        
        if not self.api_key:
            return self._mock_congestion_analysis(vehicle_data)
        
        try:
            prompt = self._build_congestion_analysis_prompt(vehicle_data, time_window)
            
            response = await self._make_api_request(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a traffic flow analyst. Identify congestion patterns, bottlenecks, and provide insights for traffic management."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            if response and "choices" in response:
                analysis_text = response["choices"][0]["message"]["content"]
                return self._parse_congestion_analysis(analysis_text, vehicle_data)
            else:
                return self._mock_congestion_analysis(vehicle_data)
                
        except Exception as e:
            logger.error(f"Groq congestion analysis failed: {e}")
            return self._mock_congestion_analysis(vehicle_data)
    
    async def generate_predictive_insights(
        self,
        historical_data: Dict[str, Any],
        prediction_horizon: str = "1h"
    ) -> Dict[str, Any]:
        """Generate predictive traffic insights"""
        
        if not self.api_key:
            return self._mock_predictive_insights(historical_data)
        
        try:
            prompt = self._build_prediction_prompt(historical_data, prediction_horizon)
            
            response = await self._make_api_request(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a predictive traffic analyst. Use historical patterns to forecast future traffic conditions and provide actionable insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            if response and "choices" in response:
                insights_text = response["choices"][0]["message"]["content"]
                return self._parse_predictive_insights(insights_text)
            else:
                return self._mock_predictive_insights(historical_data)
                
        except Exception as e:
            logger.error(f"Groq prediction request failed: {e}")
            return self._mock_predictive_insights(historical_data)
    
    async def _make_api_request(self, messages: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        """Make request to Groq API"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                return None
    
    def _build_traffic_analysis_prompt(
        self, 
        traffic_data: Dict[str, Any], 
        context: str
    ) -> str:
        """Build prompt for traffic analysis"""
        
        return f"""
Analyze the following traffic data and provide insights:

Traffic Data:
- Vehicle Count: {traffic_data.get('vehicle_count', 0)}
- Average Speed: {traffic_data.get('average_speed', 0)} km/h
- Congestion Level: {traffic_data.get('congestion_level', 0):.2f}
- Peak Hour Factor: {traffic_data.get('peak_hour_factor', 1.0):.2f}
- Directional Flow: {traffic_data.get('directional_flow', {})}

Context: {context}

Please provide:
1. Traffic condition assessment
2. Identified bottlenecks or issues
3. Peak hour patterns
4. Directional flow analysis
5. Recommendations for improvement

Format your response as structured analysis with clear sections.
"""
    
    def _build_optimization_prompt(
        self,
        intersection_data: Dict[str, Any],
        historical_performance: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for optimization recommendations"""
        
        return f"""
Analyze this intersection and provide optimization recommendations:

Intersection Data:
- ID: {intersection_data.get('intersection_id')}
- Current Timings: {intersection_data.get('current_timings', {})}
- Traffic Volume: {intersection_data.get('traffic_volume', 0)}
- Congestion Level: {intersection_data.get('congestion_level', 0):.2f}

Historical Performance (last 5 optimizations):
{json.dumps(historical_performance[-5:], indent=2)}

Please provide:
1. Current performance assessment
2. Specific timing recommendations
3. Expected improvement metrics
4. Implementation priority
5. Potential risks or considerations

Format as actionable recommendations with specific values.
"""
    
    def _build_congestion_analysis_prompt(
        self,
        vehicle_data: List[Dict[str, Any]],
        time_window: str
    ) -> str:
        """Build prompt for congestion analysis"""
        
        data_summary = {
            "total_vehicles": len(vehicle_data),
            "avg_speed": sum(v.get('speed', 0) for v in vehicle_data) / len(vehicle_data) if vehicle_data else 0,
            "time_window": time_window,
            "speed_distribution": self._calculate_speed_distribution(vehicle_data)
        }
        
        return f"""
Analyze congestion patterns from vehicle data:

Data Summary:
- Total Vehicles: {data_summary['total_vehicles']}
- Average Speed: {data_summary['avg_speed']:.1f} km/h
- Time Window: {data_summary['time_window']}
- Speed Distribution: {data_summary['speed_distribution']}

Sample Vehicle Data (first 10 records):
{json.dumps(vehicle_data[:10], indent=2)}

Please identify:
1. Congestion hotspots
2. Time-based patterns
3. Speed bottlenecks
4. Flow disruptions
5. Recommended interventions

Provide specific locations and time periods where possible.
"""
    
    def _build_prediction_prompt(
        self,
        historical_data: Dict[str, Any],
        prediction_horizon: str
    ) -> str:
        """Build prompt for predictive insights"""
        
        return f"""
Generate traffic predictions based on historical patterns:

Historical Data Summary:
- Time Period: {historical_data.get('time_period', 'Unknown')}
- Average Daily Volume: {historical_data.get('avg_daily_volume', 0)}
- Peak Hours: {historical_data.get('peak_hours', [])}
- Seasonal Patterns: {historical_data.get('seasonal_patterns', {})}
- Weather Impact: {historical_data.get('weather_correlation', {})}

Prediction Horizon: {prediction_horizon}

Please predict:
1. Expected traffic volume
2. Peak congestion times
3. Potential bottlenecks
4. Weather-related impacts
5. Recommended proactive measures

Include confidence levels and key assumptions.
"""
    
    def _calculate_speed_distribution(self, vehicle_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate speed distribution for analysis"""
        
        distribution = {"0-20": 0, "20-40": 0, "40-60": 0, "60+": 0}
        
        for vehicle in vehicle_data:
            speed = vehicle.get('speed', 0)
            if speed < 20:
                distribution["0-20"] += 1
            elif speed < 40:
                distribution["20-40"] += 1
            elif speed < 60:
                distribution["40-60"] += 1
            else:
                distribution["60+"] += 1
        
        return distribution
    
    def _parse_traffic_analysis(self, analysis_text: str, traffic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI-generated traffic analysis"""
        
        return {
            "analysis_text": analysis_text,
            "timestamp": datetime.utcnow().isoformat(),
            "data_source": traffic_data,
            "ai_model": self.model,
            "confidence": 0.85,  # Mock confidence score
            "key_insights": self._extract_key_insights(analysis_text),
            "recommendations": self._extract_recommendations(analysis_text)
        }
    
    def _parse_optimization_recommendations(self, recommendations_text: str) -> Dict[str, Any]:
        """Parse AI-generated optimization recommendations"""
        
        return {
            "recommendations_text": recommendations_text,
            "timestamp": datetime.utcnow().isoformat(),
            "ai_model": self.model,
            "priority": "high",  # Mock priority
            "implementation_complexity": "medium",
            "expected_improvement": 0.15,  # Mock 15% improvement
            "recommendations": self._extract_recommendations(recommendations_text)
        }
    
    def _parse_congestion_analysis(self, analysis_text: str, vehicle_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse AI-generated congestion analysis"""
        
        return {
            "analysis_text": analysis_text,
            "timestamp": datetime.utcnow().isoformat(),
            "data_points": len(vehicle_data),
            "ai_model": self.model,
            "congestion_score": 0.6,  # Mock congestion score
            "hotspots": self._extract_hotspots(analysis_text),
            "patterns": self._extract_patterns(analysis_text)
        }
    
    def _parse_predictive_insights(self, insights_text: str) -> Dict[str, Any]:
        """Parse AI-generated predictive insights"""
        
        return {
            "insights_text": insights_text,
            "timestamp": datetime.utcnow().isoformat(),
            "ai_model": self.model,
            "confidence": 0.78,  # Mock confidence
            "prediction_accuracy": 0.82,  # Mock historical accuracy
            "predictions": self._extract_predictions(insights_text),
            "recommendations": self._extract_recommendations(insights_text)
        }
    
    def _extract_key_insights(self, text: str) -> List[str]:
        """Extract key insights from AI response"""
        # Simple extraction - in production, use more sophisticated parsing
        insights = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['insight:', 'key:', 'important:', 'critical:']):
                insights.append(line.strip())
        return insights[:5]  # Return top 5 insights
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from AI response"""
        recommendations = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['recommend:', 'suggest:', 'should:', 'consider:']):
                recommendations.append(line.strip())
        return recommendations[:5]  # Return top 5 recommendations
    
    def _extract_hotspots(self, text: str) -> List[str]:
        """Extract congestion hotspots from AI response"""
        hotspots = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['hotspot:', 'bottleneck:', 'congestion at:', 'blocked:']):
                hotspots.append(line.strip())
        return hotspots[:3]  # Return top 3 hotspots
    
    def _extract_patterns(self, text: str) -> List[str]:
        """Extract traffic patterns from AI response"""
        patterns = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['pattern:', 'trend:', 'recurring:', 'typically:']):
                patterns.append(line.strip())
        return patterns[:3]  # Return top 3 patterns
    
    def _extract_predictions(self, text: str) -> List[str]:
        """Extract predictions from AI response"""
        predictions = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['predict:', 'expect:', 'forecast:', 'likely:']):
                predictions.append(line.strip())
        return predictions[:5]  # Return top 5 predictions
    
    # Mock methods for when Groq API is not available
    def _mock_traffic_analysis(self, traffic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock traffic analysis when API is unavailable"""
        
        return {
            "analysis_text": "Mock traffic analysis: Traffic conditions appear moderate with some congestion during peak hours.",
            "timestamp": datetime.utcnow().isoformat(),
            "data_source": traffic_data,
            "ai_model": "mock",
            "confidence": 0.7,
            "key_insights": [
                "Peak hour congestion detected",
                "Average speeds below optimal",
                "Directional flow imbalance observed"
            ],
            "recommendations": [
                "Consider adjusting signal timing",
                "Monitor during peak hours",
                "Implement adaptive control"
            ]
        }
    
    def _mock_optimization_recommendations(self, intersection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock optimization recommendations"""
        
        return {
            "recommendations_text": "Mock optimization: Increase green time by 10-15% during peak hours.",
            "timestamp": datetime.utcnow().isoformat(),
            "ai_model": "mock",
            "priority": "medium",
            "implementation_complexity": "low",
            "expected_improvement": 0.12,
            "recommendations": [
                "Extend green phase duration",
                "Reduce red phase during off-peak",
                "Implement adaptive timing"
            ]
        }
    
    def _mock_congestion_analysis(self, vehicle_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Mock congestion analysis"""
        
        return {
            "analysis_text": "Mock congestion analysis: Moderate congestion with bottlenecks at key intersections.",
            "timestamp": datetime.utcnow().isoformat(),
            "data_points": len(vehicle_data),
            "ai_model": "mock",
            "congestion_score": 0.55,
            "hotspots": [
                "Main Street intersection",
                "Highway on-ramp",
                "Downtown core"
            ],
            "patterns": [
                "Morning rush hour peak",
                "Evening congestion buildup",
                "Weekend traffic variations"
            ]
        }
    
    def _mock_predictive_insights(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock predictive insights"""
        
        return {
            "insights_text": "Mock prediction: Traffic volume expected to increase 15% during next hour.",
            "timestamp": datetime.utcnow().isoformat(),
            "ai_model": "mock",
            "confidence": 0.75,
            "prediction_accuracy": 0.80,
            "predictions": [
                "15% volume increase expected",
                "Peak congestion at 5:30 PM",
                "Weather may impact flow"
            ],
            "recommendations": [
                "Prepare adaptive timing",
                "Monitor weather conditions",
                "Alert traffic management"
            ]
        }


# Global Groq client instance
groq_client = GroqClient()
