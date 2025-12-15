"""
Image processing utilities for the FT Mixer application.
Handles grayscale conversion, resizing, and brightness/contrast adjustments.
"""
import cv2
import numpy as np
from typing import Tuple, Optional


class ImageProcessor:
    """Image processing operations."""
    
    @staticmethod
    def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
        """
        Convert an image to grayscale if it's colored.
        
        Args:
            image: Input image (BGR or grayscale)
        
        Returns:
            Grayscale image
        """
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
    
    @staticmethod
    def resize_image(image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """
        Resize image to target size.
        
        Args:
            image: Input image
            target_size: Tuple of (height, width)
        
        Returns:
            Resized image
        """
        return cv2.resize(image, (target_size[1], target_size[0]), interpolation=cv2.INTER_AREA)
    
    @staticmethod
    def get_smallest_size(images: dict) -> Optional[Tuple[int, int]]:
        """
        Calculate the smallest size among all images.
        
        Args:
            images: Dictionary of image_id -> image array
        
        Returns:
            Tuple of (height, width) or None if no images
        """
        if not images:
            return None
        
        min_height = float('inf')
        min_width = float('inf')
        
        for img in images.values():
            h, w = img.shape[:2]
            min_height = min(min_height, h)
            min_width = min(min_width, w)
        
        return (int(min_height), int(min_width))
    
    @staticmethod
    def adjust_brightness_contrast(
        image: np.ndarray,
        brightness: float = 0,
        contrast: float = 0
    ) -> np.ndarray:
        """
        Adjust brightness and contrast of an image.
        
        Args:
            image: Input grayscale image
            brightness: Brightness adjustment (-100 to 100)
            contrast: Contrast adjustment (-100 to 100)
        
        Returns:
            Adjusted image
        """
        # Contrast: alpha (1.0-3.0), Brightness: beta (0-100)
        alpha = 1 + (contrast / 100.0)  # Contrast control
        beta = brightness * 2.55  # Brightness control (scale to 0-255 range)
        
        return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    
    @staticmethod
    def normalize_for_display(
        data: np.ndarray,
        min_val: float = 0,
        max_val: float = 255
    ) -> np.ndarray:
        """
        Normalize data for display purposes.
        
        Args:
            data: Input data array
            min_val: Minimum output value
            max_val: Maximum output value
        
        Returns:
            Normalized uint8 array
        """
        return cv2.normalize(data, None, min_val, max_val, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    @staticmethod
    def decode_image(image_bytes: bytes, flags=cv2.IMREAD_COLOR) -> Optional[np.ndarray]:
        """
        Decode image from bytes.
        
        Args:
            image_bytes: Image data as bytes
            flags: OpenCV imread flags
        
        Returns:
            Decoded image or None if failed
        """
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            return cv2.imdecode(nparr, flags)
        except Exception:
            return None
    
    @staticmethod
    def encode_image(image: np.ndarray, format: str = '.png') -> Optional[bytes]:
        """
        Encode image to bytes.
        
        Args:
            image: Input image
            format: Output format (e.g., '.png', '.jpg')
        
        Returns:
            Encoded image bytes or None if failed
        """
        try:
            _, buffer = cv2.imencode(format, image)
            return buffer.tobytes()
        except Exception:
            return None
