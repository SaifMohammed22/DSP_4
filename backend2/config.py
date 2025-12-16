import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'beamforming-simulator-secret')
    
    # File settings
    UPLOAD_FOLDER = 'static/uploads'
    TEMP_FOLDER = 'static/temp'
    RESULTS_FOLDER = 'static/results'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    
    # WebSocket settings
    SOCKETIO_MESSAGE_QUEUE = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Beamforming settings
    DEFAULT_ARRAY_SIZE = 8
    DEFAULT_FREQUENCY = 2.4e9  # 2.4 GHz
    DEFAULT_GRID_SIZE = 200
    DEFAULT_GRID_RANGE = 10.0  # meters
    
    # Scenario paths
    SCENARIO_PATH = 'config/scenarios'
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}