import os
from datetime import timedelta

class Config:
    """Application configuration"""
    
    # Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Session config
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # Garmin config
    GARMIN_EMAIL = os.environ.get('GARMIN_EMAIL')
    GARMIN_PASSWORD = os.environ.get('GARMIN_PASSWORD')
    
    # File upload config
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'fit', 'gpx', 'tcx'}
    
    # Database config (optional)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///garmin_data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ANT+ config
    ANT_NETWORK_KEY = [0xB9, 0xA5, 0x21, 0xFB, 0xBD, 0x72, 0xC3, 0x45]
    
    # API rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'