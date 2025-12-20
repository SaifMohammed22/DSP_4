import numpy as np
import logging
from typing import List, Dict, Any, Optional
from .phased_array import PhasedArray

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BeamformingSimulator:
    """
    Main beamforming simulator class implementing OOP principles.
    Handles all beamforming calculations and array management using PhasedArray objects.
    """
    
    # Physical constants
    SPEED_OF_LIGHT = 3e8  # m/s
    SPEED_OF_SOUND_AIR = 343  # m/s
    SPEED_OF_SOUND_TISSUE = 1500  # m/s
    
    def __init__(self, num_elements=16, frequency=2.4e9, element_spacing=None, 
                 beam_angle=0, array_type='linear', curvature_radius=None, mode='transmitter'):
        """
        Initialize beamforming simulator with a single default array
        """
        self.arrays: List[PhasedArray] = []
        self.frequency = frequency
        self.mode = mode.lower()
        
        # Determine propagation speed
        # For simplicity, using speed of light for high frequencies (RF) and sound for low
        if frequency > 1e6:
            self.propagation_speed = self.SPEED_OF_LIGHT
        else:
            self.propagation_speed = self.SPEED_OF_SOUND_AIR
            
        self.wavelength = self.propagation_speed / frequency
        
        # Add default array
        self.add_array(
            num_elements=num_elements,
            element_spacing=element_spacing if element_spacing else 0.5,
            geometry=array_type,
            curvature_radius=curvature_radius if curvature_radius else 10.0,
            position=(0.0, 0.0),
            orientation=0.0
        )
        
        # Set steering for the default array
        self.arrays[0].set_steering_angle(beam_angle, self.frequency, self.propagation_speed)
    
    def add_array(self, num_elements=16, element_spacing=0.5, geometry='linear', 
                  curvature_radius=10.0, position=(0.0, 0.0), orientation=0.0):
        """Add a new phased array to the system"""
        array = PhasedArray(
            num_elements=num_elements,
            element_spacing=element_spacing,
            geometry=geometry,
            curvature_radius=curvature_radius,
            position=position,
            orientation=orientation
        )
        self.arrays.append(array)
        return array

    def clear_arrays(self):
        """Remove all arrays"""
        self.arrays = []

    def get_element_positions(self):
        """
        Calculate positions of array elements for all arrays
        
        Returns:
            Tuple of (x_positions, y_positions) arrays containing all elements
        """
        all_x = []
        all_y = []
        
        for array in self.arrays:
            pos = array.element_positions
            all_x.extend(pos[:, 0])
            all_y.extend(pos[:, 1])
            
        return np.array(all_x), np.array(all_y)
    
    def compute_beam_profile(self, num_angles=1000):
        """
        Compute beam pattern/profile for the entire system
        """
        # Angle range
        theta = np.linspace(-np.pi, np.pi, num_angles)
        
        # Wave number
        k = 2 * np.pi / self.wavelength
        
        # Initialize array factor
        total_array_factor = np.zeros_like(theta, dtype=complex)
        
        for array in self.arrays:
            positions = array.element_positions
            phases = array.get_phases()
            amplitudes = array.get_amplitudes()
            
            # Compute contribution of this array
            # Array factor = Sum(w_n * exp(j * (k * (x*sin(theta) + y*cos(theta)) + phase)))
            # Note: PhasedArray puts center at its position.
            
            for idx, (pos, phase, amp) in enumerate(zip(positions, phases, amplitudes)):
                x_pos, y_pos = pos
                
                # Path difference relative to origin for angle theta
                # Assuming measurement in far field? Or simplified directional pattern
                # Using standard far-field approximation: phase = k * (x*sin(theta) + y*cos(theta))
                spatial_phase = k * (x_pos * np.sin(theta) + y_pos * np.cos(theta))
                
                total_array_factor += amp * np.exp(1j * (spatial_phase + phase))
        
        # Calculate magnitude
        magnitude = np.abs(total_array_factor)
        if np.max(magnitude) > 0:
            magnitude = magnitude / np.max(magnitude)
        
        # Convert to dB
        magnitude_db = 20 * np.log10(np.clip(magnitude, 1e-10, 1))
        magnitude_db = np.maximum(magnitude_db, -60)
        
        # Scale magnitude for visualization
        magnitude_scaled = 1 + (magnitude_db / 60)
        
        return {
            'angles': np.rad2deg(theta),
            'magnitude': magnitude_scaled,
            'magnitude_db': magnitude_db
        }
    
    def compute_interference_map(self, grid_size=400, grid_range=20):
        """
        Compute 2D interference/constructive-destructive map for all arrays
        """
        # Create spatial grid
        x = np.linspace(-grid_range, grid_range, grid_size)
        y = np.linspace(-grid_range, grid_range, grid_size)
        X, Y = np.meshgrid(x, y)
        
        # Wave number
        k = 2 * np.pi / self.wavelength
        
        # Initialize field
        field = np.zeros_like(X, dtype=complex)
        
        position_list = []
        
        for array in self.arrays:
            positions = array.element_positions
            phases = array.get_phases()
            amplitudes = array.get_amplitudes()
            
            position_list.extend(positions.tolist())
            
            for idx, (pos, phase, amp) in enumerate(zip(positions, phases, amplitudes)):
                x_pos, y_pos = pos
                
                # Distance from element to all grid points
                # Use numpy broadcasting
                distances = np.sqrt((X - x_pos)**2 + (Y - y_pos)**2)
                
                # Field contribution: (A/r) * exp(j(kr + phase))
                # Using simplified model A * exp... (ignoring 1/r decay for clearer interference pattern visualization if desired,
                # but physically 1/r is correct for 2D/3D. However, for map visualization, typically we want to see the pattern structure.
                # Let's use standard wave equation.
                
                # Avoid division by zero at element location
                # distances = np.maximum(distances, 0.1 * self.wavelength)
                # amplitude = amp / distances
                
                # Using constant amplitude for clearer interference pattern visualization as requested in many educational tools
                amplitude = amp 
                
                field += amplitude * np.exp(1j * (k * distances + phase))
        
        # Calculate intensity
        intensity = np.abs(field)**2
        if np.max(intensity) > 0:
            intensity = intensity / np.max(intensity)
        
        # Log scale for better visualization
        intensity = np.log10(intensity + 1)
        if np.max(intensity) > 0:
            intensity = intensity / np.max(intensity)
        
        return {
            'X': X,
            'Y': Y,
            'interference': intensity,
            'positions': np.array(position_list)
        }
    
    def update_parameters(self, **kwargs):
        """
        Update simulator parameters.
        Supports updating a specific array by index or updating global params.
        """
        if 'frequency' in kwargs:
            self.frequency = kwargs['frequency']
            self.wavelength = self.propagation_speed / self.frequency
            # Re-steer all arrays with new frequency
            for array in self.arrays:
                # We need to store desired steering angle somewhere if we want to preserve it across freq changes
                # For now, just re-apply current phases as best as possible, or assume 0 if not stored.
                pass 
        
        if 'mode' in kwargs:
            self.mode = kwargs['mode'].lower()
            
        # Support updating array list directly
        if 'arrays' in kwargs:
            self.arrays = []
            for arr_config in kwargs['arrays']:
                array = self.add_array(
                    num_elements=arr_config.get('num_elements', 16),
                    element_spacing=arr_config.get('element_spacing', 0.5),
                    geometry=arr_config.get('geometry', 'linear'),
                    curvature_radius=arr_config.get('curvature_radius', 10.0),
                    position=arr_config.get('position', (0.0, 0.0)),
                    orientation=arr_config.get('orientation', 0.0)
                )
                
                # Apply steering
                beam_angle = arr_config.get('beam_angle', 0)
                phase_shift = arr_config.get('phase_shift', 0) # Manual phase shift
                
                if arr_config.get('geometry') == 'linear': # steering logic
                     array.set_steering_angle(beam_angle, self.frequency, self.propagation_speed)
                elif arr_config.get('geometry') == 'curved':
                     # For curved, we can also use steering, or manual phase
                     array.set_steering_angle(beam_angle, self.frequency, self.propagation_speed)
                
                # If manual phases are provided overrides
                if 'phases' in arr_config:
                    array.set_custom_phases(arr_config['phases'])
