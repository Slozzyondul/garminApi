from fitparse import FitFile
import json
from typing import Dict, List, Any
from datetime import datetime

class FitParser:
    """Parse and analyze FIT files"""
    
    def __init__(self):
        self.supported_fields = [
            'timestamp', 'position_lat', 'position_long',
            'heart_rate', 'cadence', 'speed', 'power',
            'temperature', 'altitude', 'distance'
        ]
    
    def parse_fit_file(self, file_path: str) -> Dict[str, Any]:
        """Parse FIT file and extract data"""
        try:
            fitfile = FitFile(file_path)
            
            # Extract metadata
            metadata = self._extract_metadata(fitfile)
            
            # Extract records
            records = self._extract_records(fitfile)
            
            # Extract laps
            laps = self._extract_laps(fitfile)
            
            # Extract sessions
            sessions = self._extract_sessions(fitfile)
            
            return {
                'metadata': metadata,
                'records': records,
                'laps': laps,
                'sessions': sessions,
                'summary': self._generate_summary(records)
            }
        except Exception as e:
            raise Exception(f"Error parsing FIT file: {e}")
    
    def _extract_metadata(self, fitfile: FitFile) -> Dict[str, Any]:
        """Extract file metadata"""
        metadata = {}
        
        for message in fitfile.get_messages('file_id'):
            for field in message:
                metadata[field.name] = field.value
        
        for message in fitfile.get_messages('device_info'):
            for field in message:
                metadata[f'device_{field.name}'] = field.value
        
        return metadata
    
    def _extract_records(self, fitfile: FitFile) -> List[Dict[str, Any]]:
        """Extract data records"""
        records = []
        
        for record in fitfile.get_messages('record'):
            data_point = {}
            
            for data in record:
                if data.name in self.supported_fields:
                    # Convert timestamp to ISO format
                    if data.name == 'timestamp':
                        data_point[data.name] = data.value.isoformat()
                    else:
                        data_point[data.name] = data.value
            
            if data_point:
                records.append(data_point)
        
        return records
    
    def _extract_laps(self, fitfile: FitFile) -> List[Dict[str, Any]]:
        """Extract lap information"""
        laps = []
        
        for lap in fitfile.get_messages('lap'):
            lap_data = {}
            
            for field in lap:
                if field.value is not None:
                    if hasattr(field.value, 'isoformat'):
                        lap_data[field.name] = field.value.isoformat()
                    else:
                        lap_data[field.name] = field.value
            
            if lap_data:
                laps.append(lap_data)
        
        return laps
    
    def _extract_sessions(self, fitfile: FitFile) -> List[Dict[str, Any]]:
        """Extract session information"""
        sessions = []
        
        for session in fitfile.get_messages('session'):
            session_data = {}
            
            for field in session:
                if field.value is not None:
                    if hasattr(field.value, 'isoformat'):
                        session_data[field.name] = field.value.isoformat()
                    else:
                        session_data[field.name] = field.value
            
            if session_data:
                sessions.append(session_data)
        
        return sessions
    
    def _generate_summary(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from records"""
        if not records:
            return {}
        
        summary = {
            'total_records': len(records),
            'start_time': records[0].get('timestamp'),
            'end_time': records[-1].get('timestamp')
        }
        
        # Calculate averages and ranges for numeric fields
        numeric_fields = ['heart_rate', 'speed', 'cadence', 'power', 'altitude']
        
        for field in numeric_fields:
            values = [r.get(field) for r in records if r.get(field) is not None]
            
            if values:
                summary[f'{field}_avg'] = sum(values) / len(values)
                summary[f'{field}_max'] = max(values)
                summary[f'{field}_min'] = min(values)
        
        return summary