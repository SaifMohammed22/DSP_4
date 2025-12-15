"""
Centralized error handling for the FT Mixer application.
"""
from flask import jsonify
import traceback
import re


def sanitize_traceback(tb_string: str) -> str:
    """
    Sanitize traceback to remove sensitive file paths.
    
    Args:
        tb_string: Raw traceback string
    
    Returns:
        Sanitized traceback with paths simplified
    """
    # Replace full paths with just filenames
    # Pattern matches "/path/to/file.py" and keeps only "file.py"
    sanitized = re.sub(r'/[^\s]+/([^/\s]+\.py)', r'\1', tb_string)
    return sanitized


def register_error_handlers(app):
    """Register error handlers with the Flask application."""
    
    @app.errorhandler(400)
    def bad_request(e):
        """Handle bad request errors."""
        return jsonify({
            'success': False,
            'error': 'Bad request',
            'message': str(e)
        }), 400
    
    @app.errorhandler(404)
    def not_found(e):
        """Handle 404 errors."""
        return jsonify({
            'success': False,
            'error': 'Resource not found'
        }), 404
    
    @app.errorhandler(413)
    def too_large(e):
        """Handle file too large error."""
        return jsonify({
            'success': False,
            'error': 'File is too large. Maximum size is 16MB'
        }), 413
    
    @app.errorhandler(500)
    def server_error(e):
        """Handle server errors."""
        if app.debug:
            # In debug mode, include sanitized traceback
            return jsonify({
                'success': False,
                'error': 'Internal server error',
                'traceback': sanitize_traceback(traceback.format_exc())
            }), 500
        else:
            # In production, hide details
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle uncaught exceptions."""
        if app.debug:
            # In debug mode, include sanitized traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e),
                'type': type(e).__name__,
                'traceback': sanitize_traceback(traceback.format_exc())
            }), 500
        else:
            # In production, log but don't expose
            app.logger.error(f'Unhandled exception: {str(e)}')
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': 'An unexpected error occurred'
            }), 500
