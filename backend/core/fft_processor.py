"""
FFT processing and management for the FT Mixer application.
Handles FFT computation, component extraction, and display preparation.
"""
import numpy as np
import cv2
from typing import Dict, Tuple
from .image_processor import ImageProcessor
from .storage import storage


class FFTProcessor:
    """FFT computation and management."""
    
    @staticmethod
    def compute_fft(image: np.ndarray) -> dict:
        """
        Compute FFT and extract all components.
        
        Args:
            image: Grayscale image
        
        Returns:
            Dictionary containing FFT components
        """
        # Perform FFT
        f = np.fft.fft2(image.astype(np.float64))
        fshift = np.fft.fftshift(f)
        
        return {
            'fft_shifted': fshift,
            'magnitude': np.abs(fshift),
            'phase': np.angle(fshift),
            'real': np.real(fshift),
            'imaginary': np.imag(fshift),
            'shape': image.shape
        }
    
    @staticmethod
    def prepare_display_components(fft_data: dict) -> Dict[str, np.ndarray]:
        """
        Prepare FFT components for display.
        
        Args:
            fft_data: Dictionary containing FFT components
        
        Returns:
            Dictionary of display-ready components (uint8)
        """
        magnitude = fft_data['magnitude']
        phase = fft_data['phase']
        real_part = fft_data['real']
        imag_part = fft_data['imaginary']
        
        # Normalize for display
        magnitude_display = 20 * np.log(magnitude + 1)
        magnitude_display = ImageProcessor.normalize_for_display(magnitude_display)
        phase_display = ImageProcessor.normalize_for_display(phase)
        real_display = ImageProcessor.normalize_for_display(real_part)
        imag_display = ImageProcessor.normalize_for_display(imag_part)
        
        return {
            'magnitude': magnitude_display,
            'phase': phase_display,
            'real': real_display,
            'imaginary': imag_display
        }
    
    @staticmethod
    def reprocess_all_images() -> Dict[str, dict]:
        """
        Resize all images to unified size and recompute FFT.
        
        Returns:
            Dictionary of image_id -> display components
        """
        # Get all original images
        original_images = storage.get_all_originals()
        
        if not original_images:
            return {}
        
        # Calculate unified size
        unified_size = ImageProcessor.get_smallest_size(original_images)
        if unified_size is None:
            return {}
        
        storage.set_unified_size(unified_size)
        updated_images = {}
        
        for img_id, original_img in original_images.items():
            # Resize to unified size
            resized_img = ImageProcessor.resize_image(original_img, unified_size)
            storage.store_resized(img_id, resized_img)
            
            # Compute FFT
            fft_data = FFTProcessor.compute_fft(resized_img)
            storage.store_fft(img_id, fft_data)
            
            # Prepare display components
            display_components = FFTProcessor.prepare_display_components(fft_data)
            
            updated_images[img_id] = display_components
        
        return updated_images
    
    @staticmethod
    def inverse_fft(fft_shifted: np.ndarray) -> np.ndarray:
        """
        Perform inverse FFT to reconstruct image.
        
        Args:
            fft_shifted: Shifted FFT data
        
        Returns:
            Reconstructed image (uint8)
        """
        # Inverse FFT
        f_ishift = np.fft.ifftshift(fft_shifted)
        img_back = np.fft.ifft2(f_ishift)
        img_back = np.abs(img_back)
        
        # Normalize to 0-255
        return ImageProcessor.normalize_for_display(img_back)
    
    @staticmethod
    def create_region_mask(
        shape: Tuple[int, int],
        region_type: str,
        region_size: float
    ) -> np.ndarray:
        """
        Create a mask for inner/outer region selection.
        
        Args:
            shape: Image shape (height, width)
            region_type: 'full', 'inner', or 'outer'
            region_size: Region size as percentage (0-1)
        
        Returns:
            Binary mask
        """
        rows, cols = shape
        crow, ccol = rows // 2, cols // 2
        
        if region_type == 'full':
            return np.ones(shape, dtype=np.float64)
        
        # Calculate region dimensions
        r_height = int(rows * region_size / 2)
        r_width = int(cols * region_size / 2)
        
        mask = np.zeros(shape, dtype=np.float64)
        
        if region_type == 'inner':
            # Inner region (low frequencies)
            mask[crow - r_height:crow + r_height, ccol - r_width:ccol + r_width] = 1
        else:  # outer
            # Outer region (high frequencies)
            mask[:] = 1
            mask[crow - r_height:crow + r_height, ccol - r_width:ccol + r_width] = 0
        
        return mask
