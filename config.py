"""
Configuration management for CFC Rating Processor
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'random-secret-key-for-production-adkgnskdglk-12312kgs')
    
    # Application Settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'csv').split(','))
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 16 * 1024 * 1024))  # 16MB default
    
    # CFC API Configuration
    CFC_API_BASE_URL = os.environ.get('CFC_API_BASE_URL', 'https://server.chess.ca/api/player/v1')
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', 10))
    API_RATE_LIMIT_DELAY = float(os.environ.get('API_RATE_LIMIT_DELAY', 0.1))
    
    # Event Configuration
    DEFAULT_EVENT_DATE = os.environ.get('DEFAULT_EVENT_DATE', '2025-06-16')
    DEFAULT_CFC_ID_COLUMN = int(os.environ.get('DEFAULT_CFC_ID_COLUMN', 2))
    
    # File Processing Configuration
    MAX_PLAYERS_PER_FILE = int(os.environ.get('MAX_PLAYERS_PER_FILE', 1000))
    PROCESSING_TIMEOUT = int(os.environ.get('PROCESSING_TIMEOUT', 300))


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    API_RATE_LIMIT_DELAY = float(os.environ.get('API_RATE_LIMIT_DELAY', 0.5))  # Slower for production


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    # Use in-memory database for testing
    MAX_PLAYERS_PER_FILE = 10  # Smaller limit for testing


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
