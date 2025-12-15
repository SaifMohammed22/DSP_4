"""
Input validation utilities.
"""
from typing import Optional
from werkzeug.datastructures import FileStorage


class Validator:
    """Input validation utilities."""
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif'}
    
    @staticmethod
    def allowed_file(filename: str, allowed_extensions: Optional[set] = None) -> bool:
        """
        Check if file extension is allowed.
        
        Args:
            filename: Name of the file
            allowed_extensions: Set of allowed extensions (optional)
        
        Returns:
            True if file is allowed, False otherwise
        """
        if allowed_extensions is None:
            allowed_extensions = Validator.ALLOWED_EXTENSIONS
        
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def validate_file_upload(file: FileStorage) -> tuple:
        """
        Validate file upload.
        
        Args:
            file: Uploaded file object
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file:
            return False, 'No file provided'
        
        if file.filename == '':
            return False, 'No file selected'
        
        if not Validator.allowed_file(file.filename):
            return False, f'File type not allowed. Allowed types: {", ".join(Validator.ALLOWED_EXTENSIONS)}'
        
        return True, None
    
    @staticmethod
    def validate_mixing_params(data: dict) -> tuple:
        """
        Validate mixing parameters.
        
        Args:
            data: Request data containing mixing parameters
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        if 'images' not in data:
            return False, 'Missing images parameter'
        
        # Validate component
        component = data.get('component', 'magnitude')
        if component not in ['magnitude', 'phase', 'real', 'imaginary']:
            return False, f'Invalid component: {component}'
        
        # Validate region type
        region_type = data.get('regionType', 'full')
        if region_type not in ['full', 'inner', 'outer']:
            return False, f'Invalid region type: {region_type}'
        
        # Validate region size
        region_size = data.get('regionSize', 0.5)
        if not isinstance(region_size, (int, float)) or region_size < 0 or region_size > 1:
            return False, 'Region size must be between 0 and 1'
        
        return True, None
    
    @staticmethod
    def validate_brightness_contrast(brightness: float, contrast: float) -> tuple:
        """
        Validate brightness and contrast values.
        
        Args:
            brightness: Brightness value
            contrast: Contrast value
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(brightness, (int, float)):
            return False, 'Brightness must be a number'
        
        if not isinstance(contrast, (int, float)):
            return False, 'Contrast must be a number'
        
        if brightness < -100 or brightness > 100:
            return False, 'Brightness must be between -100 and 100'
        
        if contrast < -100 or contrast > 100:
            return False, 'Contrast must be between -100 and 100'
        
        return True, None
