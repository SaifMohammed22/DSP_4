"""
Helper utility functions.
"""
from typing import Any, Dict


class Helper:
    """General helper functions."""
    
    @staticmethod
    def create_success_response(data: Any = None, message: str = 'Success') -> Dict:
        """
        Create a standardized success response.
        
        Args:
            data: Response data
            message: Success message
        
        Returns:
            Dictionary with success response
        """
        response = {'success': True, 'message': message}
        if data is not None:
            if isinstance(data, dict):
                response.update(data)
            else:
                response['data'] = data
        return response
    
    @staticmethod
    def create_error_response(error: str, status_code: int = 400) -> tuple:
        """
        Create a standardized error response.
        
        Args:
            error: Error message
            status_code: HTTP status code
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        return {'success': False, 'error': error}, status_code
