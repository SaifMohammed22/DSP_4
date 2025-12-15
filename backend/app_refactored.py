"""
FT Mixer Application - Refactored Entry Point
Digital Signal Processing Lab - Fourier Transform Magnitude/Phase Mixer

This is the main entry point using the application factory pattern.
"""
from flask import Flask
from flask_cors import CORS
import os

from config import config
from api.routes import main_bp
from api.image_routes import image_bp
from api.mixing_routes import mixing_bp
from middleware.error_handlers import register_error_handlers


def create_app(config_name=None):
    """
    Application factory function.
    
    Args:
        config_name: Configuration name ('development', 'production', 'testing')
                    If None, uses environment variable or defaults to 'development'
    
    Returns:
        Configured Flask application instance
    """
    # Determine configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Create Flask application
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(image_bp, url_prefix='/api')
    app.register_blueprint(mixing_bp, url_prefix='/api')
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


if __name__ == '__main__':
    # Create application instance
    app = create_app('development')
    
    # Print startup information
    print("=" * 60)
    print("🎛️  FT Magnitude/Phase Mixer - Server Starting")
    print("=" * 60)
    print(f"📁 Configuration: {app.config['ENV']}")
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print("=" * 60)
    print(f"🌐 Server running on: http://{app.config['HOST']}:{app.config['PORT']}")
    print("⏹️  Press CTRL+C to stop the server")
    print("=" * 60)
    
    # Run the application
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT']
    )
