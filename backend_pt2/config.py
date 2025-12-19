import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Application settings
    APP_NAME = 'Beamforming Simulator'
    APP_VERSION = '1.0.0'
    
    # API settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    # CORS settings
    CORS_HEADERS = 'Content-Type'
    
    # Logging
    LOG_FILE = 'beamforming.log'
    LOG_LEVEL = 'INFO'
    
    # Scenarios directory
    SCENARIOS_DIR = 'scenarios'
    
    # Computation limits (to prevent server overload)
    MAX_GRID_SIZE = 1000
    MAX_NUM_ELEMENTS = 256
    MAX_FREQUENCY = 1e12  # 1 THz
    
    # Physical constants
    SPEED_OF_LIGHT = 3e8  # m/s
    SPEED_OF_SOUND_AIR = 343  # m/s
    SPEED_OF_SOUND_TISSUE = 1500  # m/s


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # In production, ensure SECRET_KEY is set via environment variable
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration based on environment or name"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    return config.get(config_name, config['default'])