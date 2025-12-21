"""
Beamforming Simulator Application - Part 2
Digital Signal Processing Lab - Part 2: Beamforming Simulator

This app runs the Beamforming Simulator API on port 5001.
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os
from middleware.error_handlers import register_error_handlers

from api.beamforming_routes import beamforming_bp
from config import config


def create_beamforming_app(config_name=None):
    """
    Application factory for Part 2: Beamforming simulator.
    
    Returns:
        Configured Flask application instance for beamforming
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    app.register_blueprint(beamforming_bp)
    register_error_handlers(app)
    return app


if __name__ == '__main__':
    app = create_beamforming_app('development')
    print("=" * 50)
    print("Beamforming Simulator API - Part 2")
    print("Running on http://localhost:5001")
    print("=" * 50)
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT']
    )