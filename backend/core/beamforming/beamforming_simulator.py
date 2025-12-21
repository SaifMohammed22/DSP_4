"""
Beamforming Simulator - Core computation engine
Implements real-time beamforming visualization with support for:
- Multiple phased array units
- Linear and curved array geometries
- Transmitter and receiver modes
- Phase shift based beam steering
"""
import numpy as np
import logging
from typing import List, Tuple, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class BeamformingSimulator:
    """
    Main beamforming simulator class.
    Handles all beamforming calculations for interference maps and beam profiles.
    """
    
    def __init__(self, frequency=1.0, mode='transmitter'):
        """
        Initialize beamforming simulator.
        
        Args:
            frequency: Operating frequency (normalized, 1-20 range like reference)
            mode: 'transmitter' or 'receiver'
        """
        self.frequency = frequency
        self.mode = mode.lower()
        self.arrays = []
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def add_array(self, num_elements=8, element_spacing=0.5, geometry='linear',
                  curvature_radius=5.0, position=(0.0, 0.0), orientation=0.0,
                  phase_shift=0.0, beam_angle=0.0):
        """
        Add a phased array to the system.
        
        Args:
            num_elements: Number of antenna/transducer elements
            element_spacing: Spacing between elements (in wavelengths, λ)
            geometry: 'linear' or 'curved'
            curvature_radius: Radius for curved arrays (in wavelengths)
            position: (x, y) position of array center
            orientation: Rotation angle in degrees
            phase_shift: Progressive phase shift between elements (radians)
            beam_angle: Beam steering angle (degrees) - alternative to phase_shift
        """
        array = {
            'num_elements': num_elements,
            'element_spacing': element_spacing,
            'geometry': geometry.lower(),
            'curvature_radius': curvature_radius,
            'position': position,
            'orientation': orientation,
            'phase_shift': phase_shift,
            'beam_angle': beam_angle
        }
        self.arrays.append(array)
        self.logger.info(f"Added array with {num_elements} elements, geometry={geometry}")
        return array
    
    def clear_arrays(self):
        """Remove all arrays from the system."""
        self.arrays = []
        
    def _get_element_positions(self, array: dict) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate element positions for a single array.
        
        Returns:
            Tuple of (x_positions, y_positions) in wavelength units
        """
        n = array['num_elements']
        spacing = array['element_spacing']
        geometry = array['geometry']
        radius = array['curvature_radius']
        pos_x, pos_y = array['position']
        orientation = np.deg2rad(array['orientation'])
        
        if geometry == 'linear':
            # Linear array centered at origin
            indices = np.arange(n) - (n - 1) / 2
            local_x = indices * spacing
            local_y = np.zeros(n)
        else:
            # Curved array along an arc
            if n > 1:
                arc_length = (n - 1) * spacing
                total_angle = arc_length / radius if radius > 0 else np.pi / 2
                angles = np.linspace(-total_angle / 2, total_angle / 2, n)
            else:
                angles = np.array([0])
            
            local_x = radius * np.sin(angles)
            local_y = radius * (1 - np.cos(angles))
        
        # Apply rotation
        cos_o, sin_o = np.cos(orientation), np.sin(orientation)
        rotated_x = local_x * cos_o - local_y * sin_o
        rotated_y = local_x * sin_o + local_y * cos_o
        
        # Translate to array position
        x_positions = rotated_x + pos_x
        y_positions = rotated_y + pos_y
        
        return x_positions, y_positions
    
    def get_element_positions(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get all element positions from all arrays.
        
        Returns:
            Tuple of (all_x, all_y) positions
        """
        all_x = []
        all_y = []
        
        for array in self.arrays:
            x, y = self._get_element_positions(array)
            all_x.extend(x)
            all_y.extend(y)
            
        return np.array(all_x), np.array(all_y)
    
    def compute_interference_map(self, grid_size=400, grid_range=20) -> dict:
        """
        Compute 2D interference pattern (constructive/destructive map).
        
        Uses sine wave superposition like the reference application:
        amplitude = sum(sin(2*pi*f + i*phase_shift + 2*pi*f*distance))
        
        Args:
            grid_size: Number of grid points per dimension
            grid_range: Spatial range in wavelengths
            
        Returns:
            Dictionary with X, Y grids, interference pattern, and element positions
        """
        # Create spatial grid
        x = np.linspace(-grid_range, grid_range, grid_size)
        y = np.linspace(0, grid_range * 2, grid_size)  # Start from 0 like reference
        X, Y = np.meshgrid(x, y)
        
        # Initialize amplitude field
        amplitude = np.zeros_like(X)
        
        all_positions = []
        
        for array in self.arrays:
            x_pos, y_pos = self._get_element_positions(array)
            phase_shift = array.get('phase_shift', 0)
            
            # If beam_angle is specified, calculate phase shift from it
            beam_angle = array.get('beam_angle', 0)
            if beam_angle != 0 and phase_shift == 0:
                # Progressive phase shift for beam steering
                # phase_shift = 2*pi*d*sin(theta)/lambda where d is in wavelengths
                phase_shift = 2 * np.pi * array['element_spacing'] * np.sin(np.deg2rad(beam_angle))
            
            for i, (ex, ey) in enumerate(zip(x_pos, y_pos)):
                all_positions.append([ex, ey])
                
                # Distance from element to all grid points
                distance = np.sqrt((X - ex)**2 + (Y - ey)**2)
                
                # Sine wave interference pattern (matching reference app formula)
                # amplitude += sin(2*pi*f + i*phase_shift + 2*pi*f*distance)
                amplitude += np.sin(
                    2 * np.pi * self.frequency + 
                    i * phase_shift + 
                    2 * np.pi * self.frequency * distance
                )
        
        # Normalize to [0, 1]
        if np.max(amplitude) != np.min(amplitude):
            amplitude_normalized = (amplitude - np.min(amplitude)) / (np.max(amplitude) - np.min(amplitude))
        else:
            amplitude_normalized = np.zeros_like(amplitude)
        
        return {
            'X': X,
            'Y': Y,
            'interference': amplitude_normalized,
            'positions': np.array(all_positions)
        }
    
    def compute_beam_profile(self, num_angles=360) -> dict:
        """
        Compute the beam radiation pattern (polar plot data).
        
        Args:
            num_angles: Number of angle samples
            
        Returns:
            Dictionary with angles and magnitude data
        """
        # Angle range: -180 to 180 degrees
        angles_deg = np.linspace(-180, 180, num_angles)
        theta = np.deg2rad(angles_deg)
        
        # Array factor computation
        array_factor = np.zeros(num_angles, dtype=complex)
        
        for array in self.arrays:
            n = array['num_elements']
            spacing = array['element_spacing']
            phase_shift = array.get('phase_shift', 0)
            beam_angle = array.get('beam_angle', 0)
            
            # If beam_angle specified, use it
            if beam_angle != 0 and phase_shift == 0:
                phase_shift = 2 * np.pi * spacing * np.sin(np.deg2rad(beam_angle))
            
            # Wave number (normalized since spacing is in wavelengths)
            k = 2 * np.pi
            
            # Array factor: sum of exp(j * (k*d*n*sin(theta) + n*phase_shift))
            for idx in range(n):
                element_phase = k * spacing * idx * np.sin(theta) + idx * phase_shift
                array_factor += np.exp(1j * element_phase)
        
        # Compute magnitude
        magnitude = np.abs(array_factor)
        if np.max(magnitude) > 0:
            magnitude = magnitude / np.max(magnitude)
        
        # Convert to dB
        magnitude_db = 20 * np.log10(np.clip(magnitude, 1e-10, 1))
        magnitude_db = np.maximum(magnitude_db, -60)
        
        # Scale for visualization (0 to 1 range)
        magnitude_scaled = (magnitude_db + 60) / 60
        
        return {
            'angles': angles_deg.tolist(),
            'magnitude': magnitude_scaled.tolist(),
            'magnitude_db': magnitude_db.tolist()
        }
    
    def update_parameters(self, **kwargs):
        """
        Update simulator parameters.
        
        Supports:
        - frequency: Update operating frequency
        - mode: Update transmitter/receiver mode
        - arrays: Replace all arrays with new configuration list
        """
        if 'frequency' in kwargs:
            self.frequency = kwargs['frequency']
            
        if 'mode' in kwargs:
            self.mode = kwargs['mode'].lower()
        
        # Handle array configuration updates
        if 'arrays' in kwargs:
            self.arrays = []
            for arr_config in kwargs['arrays']:
                self.add_array(
                    num_elements=arr_config.get('num_elements', 8),
                    element_spacing=arr_config.get('element_spacing', 0.5),
                    geometry=arr_config.get('geometry', 'linear'),
                    curvature_radius=arr_config.get('curvature_radius', 5.0),
                    position=tuple(arr_config.get('position', [0.0, 0.0])),
                    orientation=arr_config.get('orientation', 0.0),
                    phase_shift=arr_config.get('phase_shift', 0.0),
                    beam_angle=arr_config.get('beam_angle', 0.0)
                )
        
        # Handle legacy single-array parameters
        if 'num_elements' in kwargs and 'arrays' not in kwargs:
            if len(self.arrays) == 0:
                self.add_array()
            
            self.arrays[0]['num_elements'] = kwargs.get('num_elements', 8)
            self.arrays[0]['element_spacing'] = kwargs.get('element_spacing', 0.5)
            self.arrays[0]['geometry'] = kwargs.get('array_type', kwargs.get('geometry', 'linear'))
            self.arrays[0]['beam_angle'] = kwargs.get('beam_angle', 0)
            self.arrays[0]['phase_shift'] = kwargs.get('phase_shift', 0)
