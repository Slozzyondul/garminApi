import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta
import statistics

class DataAnalyzer:
    """Analyze Garmin data for insights"""
    
    def analyze_heart_rate(self, hr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze heart rate data"""
        if not hr_data:
            return {}
        
        values = hr_data.get('heartRateValues', [])
        
        if not values:
            return {}
        
        hr_values = [v for v in values if v is not None and v > 0]
        
        analysis = {
            'average': statistics.mean(hr_values) if hr_values else 0,
            'max': max(hr_values) if hr_values else 0,
            'min': min(hr_values) if hr_values else 0,
            'resting': hr_data.get('restingHeartRate', 0),
            'zones': self._calculate_hr_zones(hr_values)
        }
        
        return analysis
    
    def _calculate_hr_zones(self, hr_values: List[int], max_hr: int = 190) -> Dict[str, float]:
        """Calculate time in heart rate zones"""
        zones = {
            'zone1': 0,  # 50-60% max HR
            'zone2': 0,  # 60-70% max HR
            'zone3': 0,  # 70-80% max HR
            'zone4': 0,  # 80-90% max HR
            'zone5': 0   # 90-100% max HR
        }
        
        for hr in hr_values:
            percentage = (hr / max_hr) * 100
            
            if percentage < 60:
                zones['zone1'] += 1
            elif percentage < 70:
                zones['zone2'] += 1
            elif percentage < 80:
                zones['zone3'] += 1
            elif percentage < 90:
                zones['zone4'] += 1
            else:
                zones['zone5'] += 1
        
        total = len(hr_values)
        if total > 0:
            for zone in zones:
                zones[zone] = (zones[zone] / total) * 100
        
        return zones
    
    def enrich_activities(self, activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich activity data with additional insights"""
        enriched = []
        
        for activity in activities:
            enriched_activity = activity.copy()
            
            # Add pace calculation for running activities
            if activity.get('activityType', {}).get('typeKey') == 'running':
                distance = activity.get('distance', 0)
                duration = activity.get('duration', 0)
                
                if distance > 0 and duration > 0:
                    # Calculate pace (min/km)
                    pace = (duration / 60) / (distance / 1000)
                    enriched_activity['pace'] = f"{int(pace)}:{int((pace % 1) * 60):02d}"
            
            # Add efficiency metrics
            if activity.get('averageHR') and activity.get('averageSpeed'):
                enriched_activity['efficiency'] = activity['averageSpeed'] / activity['averageHR']
            
            enriched.append(enriched_activity)
        
        return enriched
    
    def analyze_fit_data(self, fit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze parsed FIT file data"""
        records = fit_data.get('records', [])
        
        if not records:
            return {}
        
        df = pd.DataFrame(records)
        
        analysis = {
            'duration': self._calculate_duration(df),
            'distance': self._calculate_distance(df),
            'elevation': self._calculate_elevation(df),
            'heart_rate': self._analyze_hr_from_fit(df),
            'power': self._analyze_power(df) if 'power' in df.columns else None,
            'cadence': self._analyze_cadence(df) if 'cadence' in df.columns else None
        }
        
        return analysis
    
    def _calculate_duration(self, df: pd.DataFrame) -> float:
        """Calculate activity duration in minutes"""
        if 'timestamp' not in df.columns:
            return 0
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        duration = (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 60
        return round(duration, 2)
    
    def _calculate_distance(self, df: pd.DataFrame) -> float:
        """Calculate total distance in km"""
        if 'distance' not in df.columns:
            return 0
        
        return round(df['distance'].max() / 1000, 2)
    
    def _calculate_elevation(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate elevation metrics"""
        if 'altitude' not in df.columns:
            return {}
        
        elevation = {
            'gain': 0,
            'loss': 0,
            'max': df['altitude'].max(),
            'min': df['altitude'].min()
        }
        
        # Calculate elevation gain/loss
        alt_diff = df['altitude'].diff()
        elevation['gain'] = alt_diff[alt_diff > 0].sum()
        elevation['loss'] = abs(alt_diff[alt_diff < 0].sum())
        
        return elevation
    
    def _analyze_hr_from_fit(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze heart rate from FIT data"""
        if 'heart_rate' not in df.columns:
            return {}
        
        hr_data = df['heart_rate'].dropna()
        
        return {
            'average': hr_data.mean(),
            'max': hr_data.max(),
            'min': hr_data.min(),
            'std': hr_data.std()
        }
    
    def _analyze_power(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze power data"""
        power_data = df['power'].dropna()
        
        return {
            'average': power_data.mean(),
            'max': power_data.max(),
            'normalized': self._calculate_normalized_power(power_data),
            'variability': power_data.std() / power_data.mean() if power_data.mean() > 0 else 0
        }
    
    def _analyze_cadence(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze cadence data"""
        cadence_data = df['cadence'].dropna()
        
        return {
            'average': cadence_data.mean(),
            'max': cadence_data.max(),
            'min': cadence_data.min()
        }
    
    def _calculate_normalized_power(self, power_data: pd.Series) -> float:
        """Calculate normalized power (30-second rolling average)"""
        if len(power_data) < 30:
            return power_data.mean()
        
        rolling_avg = power_data.rolling(window=30).mean()
        return rolling_avg.mean()