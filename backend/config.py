"""
Configuration management for the FT Mixer application.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent


class Config:
    """Base configuration class."""
    
    # Flask settings
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}
    
    # Directory paths
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    FRONTEND_DIR = PROJECT_ROOT / 'frontend'
    TEMPLATE_FOLDER = FRONTEND_DIR / 'templates'
    STATIC_FOLDER = FRONTEND_DIR / 'static'
    
    # CORS settings
    CORS_ORIGINS = '*'  # In production, specify allowed origins
    
    # Server settings
    HOST = '0.0.0.0'
    PORT = 5000
    
    # Processing settings
    DEFAULT_REGION_SIZE = 0.5
    DEFAULT_COMPONENT = 'magnitude'
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with configuration."""
        # Create upload folder if it doesn't exist
        cls.UPLOAD_FOLDER.mkdir(exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    ENV = 'development'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    ENV = 'production'
    
    # Override with environment variables in production
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-in-production')
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with configuration."""
        super().init_app(app)
        # Validate secret key in production
        if cls.SECRET_KEY == 'change-this-in-production':
            app.logger.warning('Using default SECRET_KEY in production! Please set SECRET_KEY environment variable.')


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    UPLOAD_FOLDER = Path('/tmp/test_uploads')


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
