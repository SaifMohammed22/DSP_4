"""
Utility functions for data conversion and encoding.
"""
import base64
import cv2
import numpy as np
from typing import Optional, Dict


class Converter:
    """Data conversion utilities."""
    
    @staticmethod
    def numpy_to_base64(image: np.ndarray, format: str = '.png') -> str:
        """
        Convert numpy array to base64 string.
        
        Args:
            image: Input image as numpy array
            format: Image format (e.g., '.png', '.jpg')
        
        Returns:
            Base64 encoded string
        """
        _, buffer = cv2.imencode(format, image)
        return base64.b64encode(buffer).decode('utf-8')
    
    @staticmethod
    def base64_to_numpy(base64_string: str) -> Optional[np.ndarray]:
        """
        Convert base64 string to numpy array.
        
        Args:
            base64_string: Base64 encoded image string
        
        Returns:
            Decoded image as numpy array or None if failed
        """
        try:
            img_bytes = base64.b64decode(base64_string)
            nparr = np.frombuffer(img_bytes, np.uint8)
            return cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        except Exception:
            return None
    
    @staticmethod
    def components_to_base64(components: Dict[str, np.ndarray]) -> Dict[str, str]:
        """
        Convert multiple image components to base64.
        
        Args:
            components: Dictionary of component_name -> image array
        
        Returns:
            Dictionary of component_name -> base64 string
        """
        return {
            name: Converter.numpy_to_base64(img)
            for name, img in components.items()
        }
