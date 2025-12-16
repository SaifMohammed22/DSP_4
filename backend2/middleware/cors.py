from flask import request, make_response
from functools import wraps
import json

def setup_cors(app):
    """Setup CORS headers for all routes"""
    
    @app.after_request
    def after_request(response):
        """Add CORS headers to all responses"""
        # Get allowed origins from config
        allowed_origins = app.config.get('CORS_ORIGINS', [])
        origin = request.headers.get('Origin', '')
        
        if origin in allowed_origins:
            response.headers.add('Access-Control-Allow-Origin', origin)
        
        response.headers.add('Access-Control-Allow-Headers', 
                            'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 
                            'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '86400')  # 24 hours
        
        return response
    
    @app.before_request
    def handle_preflight():
        """Handle preflight OPTIONS requests"""
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers.add('Access-Control-Allow-Origin', 
                               request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Headers', 
                               'Content-Type,Authorization,X-Requested-With')
            response.headers.add('Access-Control-Allow-Methods', 
                               'GET,PUT,POST,DELETE,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            response.headers.add('Access-Control-Max-Age', '86400')
            return response
    
    return app

def cors_decorator(func):
    """Decorator to add CORS headers to specific routes"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Handle preflight
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 
                               'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 
                               'GET,PUT,POST,DELETE,OPTIONS')
            return response
        
        # Call original function
        response = func(*args, **kwargs)
        
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 
                           'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 
                           'GET,PUT,POST,DELETE,OPTIONS')
        
        return response
    return wrapper

def json_response(func):
    """Decorator to ensure JSON responses"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            
            # If already a response, return it
            if isinstance(result, tuple) and len(result) == 2:
                response, status = result
                if isinstance(response, dict):
                    return json.dumps(response), status, {'Content-Type': 'application/json'}
                return response, status
            
            # Convert to JSON response
            if isinstance(result, dict):
                return json.dumps(result), 200, {'Content-Type': 'application/json'}
            
            return result
        except Exception as e:
            error_response = {
                'error': str(e),
                'status': 'error'
            }
            return json.dumps(error_response), 500, {'Content-Type': 'application/json'}
    return wrapper