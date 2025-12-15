"""
Data storage management for images and FFT data.
Thread-safe storage for image processing pipeline.
"""
import threading
from typing import Dict, Optional, Tuple
import numpy as np


class ImageStorage:
    """Thread-safe storage for image and FFT data."""
    
    def __init__(self):
        """Initialize storage with thread lock."""
        self._lock = threading.Lock()
        self._image_original_data: Dict[str, np.ndarray] = {}
        self._image_resized_data: Dict[str, np.ndarray] = {}
        self._image_fft_data: Dict[str, dict] = {}
        self._current_unified_size: Optional[Tuple[int, int]] = None
        self._current_mix_task = None
    
    def store_original(self, image_id: str, image: np.ndarray) -> None:
        """
        Store original image data.
        
        Args:
            image_id: Unique identifier for the image
            image: Original grayscale image
        """
        with self._lock:
            self._image_original_data[image_id] = image.copy()
    
    def store_resized(self, image_id: str, image: np.ndarray) -> None:
        """
        Store resized image data.
        
        Args:
            image_id: Unique identifier for the image
            image: Resized grayscale image
        """
        with self._lock:
            self._image_resized_data[image_id] = image.copy()
    
    def store_fft(self, image_id: str, fft_data: dict) -> None:
        """
        Store FFT data for an image.
        
        Args:
            image_id: Unique identifier for the image
            fft_data: Dictionary containing FFT components
        """
        with self._lock:
            self._image_fft_data[image_id] = fft_data
    
    def get_original(self, image_id: str) -> Optional[np.ndarray]:
        """Get original image data."""
        with self._lock:
            return self._image_original_data.get(image_id)
    
    def get_resized(self, image_id: str) -> Optional[np.ndarray]:
        """Get resized image data."""
        with self._lock:
            return self._image_resized_data.get(image_id)
    
    def get_fft(self, image_id: str) -> Optional[dict]:
        """Get FFT data for an image."""
        with self._lock:
            return self._image_fft_data.get(image_id)
    
    def get_all_originals(self) -> Dict[str, np.ndarray]:
        """Get all original images."""
        with self._lock:
            return self._image_original_data.copy()
    
    def get_all_fft(self) -> Dict[str, dict]:
        """Get all FFT data."""
        with self._lock:
            return self._image_fft_data.copy()
    
    def remove_image(self, image_id: str) -> None:
        """Remove all data for an image."""
        with self._lock:
            self._image_original_data.pop(image_id, None)
            self._image_resized_data.pop(image_id, None)
            self._image_fft_data.pop(image_id, None)
    
    def clear_all(self) -> None:
        """Clear all stored data."""
        with self._lock:
            self._image_original_data.clear()
            self._image_resized_data.clear()
            self._image_fft_data.clear()
            self._current_unified_size = None
    
    def set_unified_size(self, size: Tuple[int, int]) -> None:
        """Set the current unified size for all images."""
        with self._lock:
            self._current_unified_size = size
    
    def get_unified_size(self) -> Optional[Tuple[int, int]]:
        """Get the current unified size."""
        with self._lock:
            return self._current_unified_size
    
    def has_images(self) -> bool:
        """Check if any images are stored."""
        with self._lock:
            return len(self._image_original_data) > 0
    
    def get_image_count(self) -> int:
        """Get the number of stored images."""
        with self._lock:
            return len(self._image_original_data)
    
    def set_mix_task(self, task) -> None:
        """Set the current mixing task."""
        with self._lock:
            self._current_mix_task = task
    
    def get_mix_task(self):
        """Get the current mixing task."""
        with self._lock:
            return self._current_mix_task


# Global storage instance
storage = ImageStorage()
