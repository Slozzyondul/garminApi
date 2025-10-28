from garminconnect import Garmin
from datetime import datetime, timedelta
import json
import pandas as pd
from typing import Optional, List, Dict, Any

class GarminClient:
    """Wrapper for Garmin Connect API"""
    
    def __init__(self, email: str = None, password: str = None):
        self.email = email
        self.password = password
        self.client = None
        self.logged_in = False
        self._session_data = {}
    
    def login(self) -> bool:
        """Authenticate with Garmin Connect"""
        try:
            self.client = Garmin(self.email, self.password)
            self.client.login()
            self.logged_in = True
            self._session_data['login_time'] = datetime.now()
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    def get_user_summary(self) -> Optional[Dict[str, Any]]:
        """Get user profile and summary statistics"""
        if not self.logged_in:
            return None
        
        try:
            profile = self.client.get_user_summary(datetime.now().strftime('%Y-%m-%d'))
            return profile
        except Exception as e:
            print(f"Error getting user summary: {e}")
            return None
    
    def get_devices(self) -> Optional[List[Dict[str, Any]]]:
        """Get all registered devices"""
        if not self.logged_in:
            return None
        
        try:
            devices = self.client.get_devices()
            return devices
        except Exception as e:
            print(f"Error getting devices: {e}")
            return None
    
    def get_activities(self, limit: int = 20, start: int = 0) -> Optional[List[Dict[str, Any]]]:
        """Get activities with pagination"""
        if not self.logged_in:
            return None
        
        try:
            activities = self.client.get_activities(start, limit)
            return activities
        except Exception as e:
            print(f"Error getting activities: {e}")
            return None
    
    def get_activity_details(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific activity"""
        if not self.logged_in:
            return None
        
        try:
            activity = self.client.get_activity_evaluation(activity_id)
            return activity
        except Exception as e:
            print(f"Error getting activity details: {e}")
            return None
    
    def get_heart_rate_data(self, date: str = None) -> Optional[Dict[str, Any]]:
        """Get heart rate data for a specific date"""
        if not self.logged_in:
            return None
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            hr_data = self.client.get_heart_rates(date)
            return hr_data
        except Exception as e:
            print(f"Error getting heart rate data: {e}")
            return None
    
    def get_sleep_data(self, date: str = None) -> Optional[Dict[str, Any]]:
        """Get sleep data for a specific date"""
        if not self.logged_in:
            return None
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            sleep_data = self.client.get_sleep_data(date)
            return sleep_data
        except Exception as e:
            print(f"Error getting sleep data: {e}")
            return None
    
    def get_stress_data(self, date: str = None) -> Optional[Dict[str, Any]]:
        """Get stress data for a specific date"""
        if not self.logged_in:
            return None
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            stress_data = self.client.get_stress_data(date)
            return stress_data
        except Exception as e:
            print(f"Error getting stress data: {e}")
            return None
    
    def download_activity(self, activity_id: str, dl_format: str = 'FIT') -> Optional[bytes]:
        """Download activity in specified format (FIT, GPX, TCX)"""
        if not self.logged_in:
            return None
        
        try:
            if dl_format == 'FIT':
                return self.client.download_activity(activity_id, dl_fmt=self.client.ActivityDownloadFormat.ORIGINAL)
            elif dl_format == 'GPX':
                return self.client.download_activity(activity_id, dl_fmt=self.client.ActivityDownloadFormat.GPX)
            elif dl_format == 'TCX':
                return self.client.download_activity(activity_id, dl_fmt=self.client.ActivityDownloadFormat.TCX)
        except Exception as e:
            print(f"Error downloading activity: {e}")
            return None
    
    def export_to_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert data to pandas DataFrame for analysis"""
        return pd.DataFrame(data)