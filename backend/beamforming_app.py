"""
Beamforming Simulator Application - Separate Entry Point
Digital Signal Processing Lab - Part B: Beamforming Simulator

This runs on port 5001, separate from the FT Mixer (port 5000).
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os
import traceback

from api.beamforming_routes import beamforming_bp


def create_beamforming_app():
    """
    Application factory for beamforming simulator.
    
    Returns:
        Configured Flask application instance for beamforming
    """
    # Create Flask application
    app = Flask(__name__)
    
    # Configure
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'beamforming-dev-key')
    app.config['DEBUG'] = True
    
    # Enable CORS for all origins in development
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    
    # Register beamforming blueprint
    app.register_blueprint(beamforming_bp)
    
    # Add error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(error)}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(error)}), 500
    
    return app


if __name__ == '__main__':
    app = create_beamforming_app()
    print("=" * 50)
    print("Beamforming Simulator API")
    print("Running on http://localhost:5001")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=True)
