"""
Main routes for the FT Mixer API.
"""
from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)


@main_bp.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'status': 'ok',
        'message': 'FT Mixer API is running'
    })
