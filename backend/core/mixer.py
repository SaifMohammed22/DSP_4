"""
Image mixing algorithms for the FT Mixer application.
Handles weighted mixing of FFT components and reconstruction.
"""
import numpy as np
import cv2
from typing import Dict
from .fft_processor import FFTProcessor
from .storage import storage


class Mixer:
    """Image mixing based on FFT components."""
    
    @staticmethod
    def mix_images(
        image_weights: Dict[str, float],
        component: str = 'magnitude',
        region_type: str = 'full',
        region_size: float = 0.5
    ) -> np.ndarray:
        """
        Mix images based on FFT components with weighted average.
        
        Args:
            image_weights: Dictionary mapping image_id to weight
            component: Component to mix ('magnitude', 'phase', 'real', 'imaginary')
            region_type: Region selection ('full', 'inner', 'outer')
            region_size: Region size as percentage (0-1)
        
        Returns:
            Mixed image (uint8)
        
        Raises:
            ValueError: If no images available or invalid parameters
        """
        # Get all FFT data
        all_fft_data = storage.get_all_fft()
        
        # Filter to only weighted images
        available_images = {
            k: v for k, v in all_fft_data.items()
            if k in image_weights and image_weights[k] > 0
        }
        
        if not available_images:
            raise ValueError('No images available for mixing')
        
        # Get target shape from first image
        first_key = list(available_images.keys())[0]
        target_shape = available_images[first_key]['shape']
        
        # Mix based on component type
        if component in ['magnitude', 'phase']:
            result_fft = Mixer._mix_magnitude_phase(
                available_images,
                image_weights,
                component,
                target_shape,
                region_type,
                region_size
            )
        else:  # real or imaginary
            result_fft = Mixer._mix_real_imaginary(
                available_images,
                image_weights,
                component,
                target_shape,
                region_type,
                region_size
            )
        
        # Inverse FFT to get result image
        return FFTProcessor.inverse_fft(result_fft)
    
    @staticmethod
    def _mix_magnitude_phase(
        available_images: Dict[str, dict],
        image_weights: Dict[str, float],
        component: str,
        target_shape: tuple,
        region_type: str,
        region_size: float
    ) -> np.ndarray:
        """
        Mix images using magnitude and phase components.
        
        Returns:
            Complex FFT array
        """
        result_magnitude = np.zeros(target_shape, dtype=np.float64)
        result_phase = np.zeros(target_shape, dtype=np.float64)
        total_weight = 0
        
        for img_id, fft_data in available_images.items():
            weight = image_weights.get(img_id, 0)
            if weight > 0:
                mag = fft_data['magnitude']
                ph = fft_data['phase']
                
                # Resize if needed
                if mag.shape != target_shape:
                    mag = cv2.resize(mag, (target_shape[1], target_shape[0]))
                    ph = cv2.resize(ph, (target_shape[1], target_shape[0]))
                
                # Apply region mask
                mask = FFTProcessor.create_region_mask(target_shape, region_type, region_size)
                
                if component == 'magnitude':
                    result_magnitude += weight * mag * mask
                    result_phase += weight * ph
                else:  # phase
                    result_phase += weight * ph * mask
                    result_magnitude += weight * mag
                
                total_weight += weight
        
        if total_weight > 0:
            result_magnitude /= total_weight
            result_phase /= total_weight
        
        # Reconstruct complex FFT
        return result_magnitude * np.exp(1j * result_phase)
    
    @staticmethod
    def _mix_real_imaginary(
        available_images: Dict[str, dict],
        image_weights: Dict[str, float],
        component: str,
        target_shape: tuple,
        region_type: str,
        region_size: float
    ) -> np.ndarray:
        """
        Mix images using real and imaginary components.
        
        Returns:
            Complex FFT array
        """
        result_real = np.zeros(target_shape, dtype=np.float64)
        result_imag = np.zeros(target_shape, dtype=np.float64)
        total_weight = 0
        
        for img_id, fft_data in available_images.items():
            weight = image_weights.get(img_id, 0)
            if weight > 0:
                real = fft_data['real']
                imag = fft_data['imaginary']
                
                # Resize if needed
                if real.shape != target_shape:
                    real = cv2.resize(real, (target_shape[1], target_shape[0]))
                    imag = cv2.resize(imag, (target_shape[1], target_shape[0]))
                
                # Apply region mask
                mask = FFTProcessor.create_region_mask(target_shape, region_type, region_size)
                
                if component == 'real':
                    result_real += weight * real * mask
                    result_imag += weight * imag
                else:  # imaginary
                    result_imag += weight * imag * mask
                    result_real += weight * real
                
                total_weight += weight
        
        if total_weight > 0:
            result_real /= total_weight
            result_imag /= total_weight
        
        # Reconstruct complex FFT
        return result_real + 1j * result_imag
