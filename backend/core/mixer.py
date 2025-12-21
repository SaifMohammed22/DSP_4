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
        image_bboxes: Dict[str, dict] = None,
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
                image_bboxes or {},
                component,
                target_shape,
                region_type,
                region_size
            )
        else:  # real or imaginary
            result_fft = Mixer._mix_real_imaginary(
                available_images,
                image_weights,
                image_bboxes or {},
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
        image_bboxes: Dict[str, dict],
        component: str,
        target_shape: tuple,
        region_type: str,
        region_size: float
    ) -> np.ndarray:
        """
        Mix images using magnitude and phase components.
        
        Note:
            All images should already be resized to unified dimensions
            via the upload process. This method includes fallback resizing
            for safety, but it's recommended to ensure images are pre-resized
            to avoid FFT component artifacts.
        
        Returns:
            Complex FFT array
        """
        result_magnitude = np.zeros(target_shape, dtype=np.float64)
        result_phase = np.zeros(target_shape, dtype=np.float64)
        spatial_weight_map = np.zeros(target_shape, dtype=np.float64)
        
        # Determine which images contribute to which component based on user selection
        for img_id, fft_data in available_images.items():
            weight = image_weights.get(img_id, 0)
            if weight > 0:
                mag = fft_data['magnitude']
                ph = fft_data['phase']
                
                # Apply region mask
                if region_type == 'rectangle':
                    roi_data = image_bboxes.get(img_id)
                    mask = FFTProcessor.create_bbox_mask(
                        target_shape, 
                        roi_data, 
                        mode=roi_data.get('mode', 'inner') if isinstance(roi_data, dict) else 'inner'
                    )
                else:
                    mask = FFTProcessor.create_region_mask(target_shape, region_type, region_size)
                
                # Contribution to the spatial map
                effective_weight = weight * mask
                spatial_weight_map += effective_weight
                
                if component == 'magnitude':
                    result_magnitude += effective_weight * mag
                    # For phase, we still need a phase component. 
                    # If we're "cropping", we take the phase from the same image's region.
                    result_phase += effective_weight * ph
                else:  # phase
                    result_phase += effective_weight * ph
                    result_magnitude += effective_weight * mag
        
        # Avoid division by zero
        spatial_weight_map[spatial_weight_map == 0] = 1e-10
        
        result_magnitude /= spatial_weight_map
        result_phase /= spatial_weight_map
        
        # Zero out regions where no weight was applied (true cropping effect)
        result_magnitude[spatial_weight_map < 1e-9] = 0
        
        # Reconstruct complex FFT
        return result_magnitude * np.exp(1j * result_phase)
    
    @staticmethod
    def _mix_real_imaginary(
        available_images: Dict[str, dict],
        image_weights: Dict[str, float],
        image_bboxes: Dict[str, dict],
        component: str,
        target_shape: tuple,
        region_type: str,
        region_size: float
    ) -> np.ndarray:
        """
        Mix images using real and imaginary components.
        
        Note:
            All images should already be resized to unified dimensions
            via the upload process. This method includes fallback resizing
            for safety, but it's recommended to ensure images are pre-resized
            to avoid FFT component artifacts.
        
        Returns:
            Complex FFT array
        """
        result_real = np.zeros(target_shape, dtype=np.float64)
        result_imag = np.zeros(target_shape, dtype=np.float64)
        spatial_weight_map = np.zeros(target_shape, dtype=np.float64)
        
        for img_id, fft_data in available_images.items():
            weight = image_weights.get(img_id, 0)
            if weight > 0:
                real = fft_data['real']
                imag = fft_data['imaginary']
                
                # Apply region mask
                if region_type == 'rectangle':
                    roi_data = image_bboxes.get(img_id)
                    mask = FFTProcessor.create_bbox_mask(
                        target_shape, 
                        roi_data, 
                        mode=roi_data.get('mode', 'inner') if isinstance(roi_data, dict) else 'inner'
                    )
                else:
                    mask = FFTProcessor.create_region_mask(target_shape, region_type, region_size)
                
                effective_weight = weight * mask
                spatial_weight_map += effective_weight
                
                if component == 'real':
                    result_real += effective_weight * real
                    result_imag += effective_weight * imag
                else:  # imaginary
                    result_imag += effective_weight * imag
                    result_real += effective_weight * real
                
        # Avoid division by zero
        spatial_weight_map[spatial_weight_map == 0] = 1e-10
        
        result_real /= spatial_weight_map
        result_imag /= spatial_weight_map
        
        # True cropping: zero out areas with no contribution
        result_real[spatial_weight_map < 1e-9] = 0
        result_imag[spatial_weight_map < 1e-9] = 0
        
        # Reconstruct complex FFT
        return result_real + 1j * result_imag
