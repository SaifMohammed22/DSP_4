from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
from config import config
from api.beamforming.routes import beamforming_bp
from middleware.cors import setup_cors

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Setup CORS
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # Setup WebSocket
    socketio = SocketIO(app, 
                       cors_allowed_origins=app.config['CORS_ORIGINS'],
                       message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'],
                       async_mode='eventlet')
    
    # Create directories
    os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
    os.makedirs(app.config['SCENARIO_PATH'], exist_ok=True)
    
    # Register Blueprints
    app.register_blueprint(beamforming_bp, url_prefix='/api/beamforming')
    
    # WebSocket events
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        emit('connected', {'status': 'connected', 'service': 'beamforming'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')
    
    @socketio.on('beamforming_update')
    def handle_beamforming_update(data):
        """Handle real-time beamforming parameter updates"""
        emit('beamforming_progress', {'progress': 50, 'message': 'Processing...'})
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'Beamforming Simulator',
            'version': '1.0.0'
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': 'The requested resource was not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error', 'message': str(error)}), 500
    
    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)