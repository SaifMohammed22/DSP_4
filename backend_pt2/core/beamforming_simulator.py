import numpy as np
import logging
from scipy.constants import speed_of_light

logging.basicConfig(
    filename='beamforming.log',
    level=logging.DEBUG,  # Changed to DEBUG level to see debug messages
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BeamformingSimulator:
    """
    Main beamforming simulator class implementing OOP principles.
    Handles all beamforming calculations and array management.
    """
    
    # Physical constants
    SPEED_OF_LIGHT = 3e8  # m/s
    SPEED_OF_SOUND_AIR = 343  # m/s
    SPEED_OF_SOUND_TISSUE = 1500  # m/s
    
    def __init__(self, num_elements=16, frequency=2.4e9, element_spacing=None, 
                 beam_angle=0, array_type='linear', curvature_radius=None, mode='transmitter'):
        """
        Initialize beamforming simulator
        
        Args:
            num_elements: Number of array elements
            frequency: Operating frequency in Hz
            element_spacing: Spacing between elements (wavelengths)
            beam_angle: Beam steering angle in degrees
            array_type: 'linear' or 'curved'
            curvature_radius: Radius for curved arrays
            mode: 'transmitter' or 'receiver'
        """
        logging.debug(f"Initializing BeamformingSimulator with parameters:")
        logging.debug(f"  num_elements: {num_elements}")
        logging.debug(f"  frequency: {frequency}")
        logging.debug(f"  element_spacing: {element_spacing}")
        logging.debug(f"  beam_angle: {beam_angle}")
        logging.debug(f"  array_type: {array_type}")
        logging.debug(f"  curvature_radius: {curvature_radius}")
        logging.debug(f"  mode: {mode}")
        
        self.num_elements = num_elements
        self.frequency = frequency
        self.beam_angle = beam_angle
        self.array_type = array_type.lower()
        self.mode = mode.lower()
        
        # Calculate wavelength based on propagation medium
        self.propagation_speed = self.SPEED_OF_LIGHT
        self.wavelength = self.propagation_speed / frequency
        logging.debug(f"  Calculated wavelength: {self.wavelength}")
        
        # Set element spacing (default to half wavelength)
        if element_spacing is None:
            self.element_spacing = self.wavelength / 2
            logging.debug(f"  Using default element spacing: λ/2 = {self.element_spacing}")
        else:
            self.element_spacing = element_spacing * self.wavelength
            logging.debug(f"  Using custom element spacing: {element_spacing}λ = {self.element_spacing}")
            
        # Set curvature radius for curved arrays
        if curvature_radius is None and self.array_type == 'curved':
            self.curvature_radius = (num_elements - 1) * self.element_spacing / np.pi
            logging.debug(f"  Calculated curvature_radius: {self.curvature_radius}")
        else:
            self.curvature_radius = curvature_radius if curvature_radius else 1.0
            logging.debug(f"  curvature_radius: {self.curvature_radius}")
            
        logging.info(f"Simulator initialized: {num_elements} elements, {frequency/1e9:.2f} GHz, {array_type} array")
        logging.debug(f"Initialization complete - instance ID: {id(self)}")
    
    def set_propagation_speed(self, speed):
        """Set propagation speed and update wavelength"""
        logging.debug(f"set_propagation_speed called: speed={speed}")
        logging.debug(f"  Previous propagation_speed: {self.propagation_speed}")
        logging.debug(f"  Previous wavelength: {self.wavelength}")
        
        self.propagation_speed = speed
        self.wavelength = speed / self.frequency
        self.element_spacing = self.wavelength / 2
        
        logging.debug(f"  New propagation_speed: {self.propagation_speed}")
        logging.debug(f"  New wavelength: {self.wavelength}")
        logging.debug(f"  New element_spacing: {self.element_spacing}")
        logging.info(f"Propagation speed set to {speed} m/s")
    
    def set_beam_angle(self, angle):
        """Set beam steering angle"""
        logging.debug(f"set_beam_angle called: angle={angle}")
        logging.debug(f"  Previous beam_angle: {self.beam_angle}")
        
        self.beam_angle = angle
        
        logging.debug(f"  New beam_angle: {self.beam_angle}")
        logging.debug(f"Beam angle set to {angle} degrees")
    
    def get_element_positions(self):
        """
        Calculate positions of array elements
        
        Returns:
            Tuple of (x_positions, y_positions) arrays
        """
        logging.debug(f"get_element_positions called")
        logging.debug(f"  array_type: {self.array_type}")
        logging.debug(f"  num_elements: {self.num_elements}")
        logging.debug(f"  element_spacing: {self.element_spacing}")
        logging.debug(f"  curvature_radius: {self.curvature_radius}")
        
        if self.array_type == 'linear':
            # Linear array centered at origin
            logging.debug(f"  Calculating linear array positions")
            x_positions = np.arange(-(self.num_elements - 1) / 2, 
                                   (self.num_elements) / 2) * self.element_spacing
            y_positions = np.zeros_like(x_positions)
        else:
            # Curved array (semicircular)
            logging.debug(f"  Calculating curved array positions")
            arc_angle = np.pi
            theta = np.linspace(-arc_angle, 0, self.num_elements)
            logging.debug(f"  theta range: {theta[0]:.3f} to {theta[-1]:.3f} radians")
            x_positions = self.curvature_radius * np.cos(theta)
            y_positions = self.curvature_radius * np.sin(theta)
        
        logging.debug(f"  x_positions shape: {x_positions.shape}")
        logging.debug(f"  y_positions shape: {y_positions.shape}")
        logging.debug(f"  x_positions range: {x_positions.min():.3f} to {x_positions.max():.3f}")
        logging.debug(f"  y_positions range: {y_positions.min():.3f} to {y_positions.max():.3f}")
        
        return x_positions, y_positions
    
    def compute_beam_profile(self, num_angles=1000):
        """
        Compute beam pattern/profile
        
        Args:
            num_angles: Number of angle samples
            
        Returns:
            Dictionary with angles, magnitude, and magnitude in dB
        """
        logging.debug(f"compute_beam_profile called: num_angles={num_angles}")
        logging.debug(f"  mode: {self.mode}")
        logging.debug(f"  beam_angle: {self.beam_angle}")
        logging.debug(f"  wavelength: {self.wavelength}")
        
        # Angle range
        theta = np.linspace(-np.pi, np.pi, num_angles)
        logging.debug(f"  theta range: {theta[0]:.3f} to {theta[-1]:.3f} radians")
        
        # Get element positions
        x_positions, y_positions = self.get_element_positions()
        
        # Steering angle in radians
        steering_angle = np.deg2rad(self.beam_angle)
        logging.debug(f"  steering_angle: {steering_angle:.3f} radians")
        
        # Wave number
        k = 2 * np.pi / self.wavelength
        logging.debug(f"  wave number k: {k:.3f}")
        
        # Initialize array factor
        array_factor = np.zeros_like(theta, dtype=complex)
        logging.debug(f"  array_factor initialized - shape: {array_factor.shape}, dtype: {array_factor.dtype}")
        
        if self.mode == 'receiver':
            logging.debug(f"  Using receiver mode with Blackman window")
            # Apply tapering window for receiver mode
            window = np.blackman(self.num_elements)
            window /= np.sum(window)
            logging.debug(f"  window shape: {window.shape}, sum: {window.sum():.3f}")
            
            for n, (x_pos, y_pos) in enumerate(zip(x_positions, y_positions)):
                phase_shift = k * x_pos * np.sin(steering_angle)
                phase_shift *= window[n]
                gain = window[n]
                
                if n == 0:  # Log first element for debugging
                    logging.debug(f"  Element 0: x_pos={x_pos:.3f}, window={window[0]:.3f}, phase_shift={phase_shift:.3f}")
                
                for i, angle in enumerate(theta):
                    phase_shift_angle = k * x_pos * (np.sin(angle) - np.sin(steering_angle))
                    array_factor[i] += gain * np.exp(1j * (phase_shift + phase_shift_angle))
        else:
            logging.debug(f"  Using transmitter mode")
            for idx, (x_pos, y_pos) in enumerate(zip(x_positions, y_positions)):
                if self.array_type == 'linear':
                    path_diff = x_pos * (np.sin(theta) - np.sin(steering_angle))
                else:
                    # Curved array path difference
                    dx = x_pos
                    dy = y_pos - self.curvature_radius
                    path_diff = (dx * np.sin(theta) + dy * np.cos(theta) - 
                               (dx * np.sin(steering_angle) + dy * np.cos(steering_angle)))
                
                phase = k * path_diff
                array_factor += np.exp(1j * phase)
                
                if idx == 0:  # Log first element for debugging
                    logging.debug(f"  Element 0: x_pos={x_pos:.3f}, y_pos={y_pos:.3f}")
                    logging.debug(f"  Element 0 path_diff range: {path_diff.min():.3f} to {path_diff.max():.3f}")
        
        # Calculate magnitude
        magnitude = np.abs(array_factor)
        magnitude = magnitude / np.max(magnitude)
        logging.debug(f"  magnitude range after normalization: {magnitude.min():.3f} to {magnitude.max():.3f}")
        
        # Convert to dB
        magnitude_db = 20 * np.log10(np.clip(magnitude, 1e-10, 1))
        magnitude_db = np.maximum(magnitude_db, -60)
        logging.debug(f"  magnitude_db range: {magnitude_db.min():.3f} to {magnitude_db.max():.3f} dB")
        
        # Scale magnitude for visualization
        magnitude_scaled = 1 + (magnitude_db / 60)
        logging.debug(f"  magnitude_scaled range: {magnitude_scaled.min():.3f} to {magnitude_scaled.max():.3f}")
        
        logging.debug(f"Beam profile computed - returning dict with keys: angles, magnitude, magnitude_db")
        
        return {
            'angles': np.rad2deg(theta),
            'magnitude': magnitude_scaled,
            'magnitude_db': magnitude_db
        }
    
    def compute_interference_map(self, grid_size=400, grid_range=20):
        """
        Compute 2D interference/constructive-destructive map
        
        Args:
            grid_size: Number of grid points per dimension
            grid_range: Spatial range in wavelengths
            
        Returns:
            Dictionary with X, Y grids, interference pattern, and element positions
        """
        logging.debug(f"compute_interference_map called: grid_size={grid_size}, grid_range={grid_range}")
        logging.debug(f"  array_type: {self.array_type}")
        logging.debug(f"  wavelength: {self.wavelength}")
        
        # Create spatial grid
        x = np.linspace(-grid_range, grid_range, grid_size)
        y = np.linspace(-grid_range if self.array_type == 'curved' else 0, 
                       grid_range, grid_size)
        X, Y = np.meshgrid(x, y)
        logging.debug(f"  X grid shape: {X.shape}")
        logging.debug(f"  X range: {X.min():.1f} to {X.max():.1f}")
        logging.debug(f"  Y range: {Y.min():.1f} to {Y.max():.1f}")
        
        # Wave number
        k = 2 * np.pi / self.wavelength
        logging.debug(f"  wave number k: {k:.3f}")
        
        # Get element positions
        x_positions, y_positions = self.get_element_positions()
        
        # Steering angle
        steering_angle_rad = np.deg2rad(self.beam_angle)
        logging.debug(f"  steering_angle_rad: {steering_angle_rad:.3f}")
        
        # Initialize field
        field = np.zeros_like(X, dtype=complex)
        logging.debug(f"  field initialized - shape: {field.shape}, dtype: {field.dtype}")
        
        # Calculate center for reference
        x_center = 0
        y_center = 0
        
        # Compute field from each element
        for idx, (x_pos, y_pos) in enumerate(zip(x_positions, y_positions)):
            # Distance from element to all grid points
            distances = np.sqrt((X - x_pos)**2 + (Y - y_pos)**2)
            
            if self.array_type == 'linear':
                # Linear array phase shift
                phase_shift = k * y_pos * np.sin(steering_angle_rad)
            else:
                # Curved array phase shift
                element_angle = np.arctan2(y_pos - y_center, x_pos - x_center)
                phase_shift = k * self.curvature_radius * np.cos(element_angle - steering_angle_rad)
            
            # Add contribution from this element
            field += np.exp(1j * (k * distances + phase_shift))
            
            if idx == 0:  # Log first element for debugging
                logging.debug(f"  Element 0: position=({x_pos:.3f}, {y_pos:.3f}), phase_shift={phase_shift:.3f}")
                logging.debug(f"  Element 0 distances range: {distances.min():.3f} to {distances.max():.3f}")
        
        # Calculate intensity
        intensity = np.abs(field)**2
        intensity = intensity / np.max(intensity)
        logging.debug(f"  intensity range after normalization: {intensity.min():.3e} to {intensity.max():.3f}")
        
        # Log scale for better visualization
        intensity = np.log10(intensity + 1)
        intensity = intensity / np.max(intensity)
        logging.debug(f"  intensity range after log scaling: {intensity.min():.3f} to {intensity.max():.3f}")
        
        logging.debug(f"Interference map computed - returning dict with keys: X, Y, interference, positions")
        
        return {
            'X': X,
            'Y': Y,
            'interference': intensity,
            'positions': np.column_stack([x_positions, y_positions])
        }
    
    def update_parameters(self, **kwargs):
        """Update simulator parameters"""
        logging.debug(f"update_parameters called with kwargs: {kwargs}")
        
        for key, value in kwargs.items():
            logging.debug(f"  Attempting to update {key} = {value}")
        
        if 'num_elements' in kwargs:
            old_val = self.num_elements
            self.num_elements = kwargs['num_elements']
            logging.debug(f"    Updated num_elements: {old_val} -> {self.num_elements}")
            
        if 'frequency' in kwargs:
            old_val = self.frequency
            self.frequency = kwargs['frequency']
            self.wavelength = self.propagation_speed / self.frequency
            logging.debug(f"    Updated frequency: {old_val} -> {self.frequency}")
            logging.debug(f"    New wavelength: {self.wavelength}")
            
        if 'beam_angle' in kwargs:
            old_val = self.beam_angle
            self.beam_angle = kwargs['beam_angle']
            logging.debug(f"    Updated beam_angle: {old_val} -> {self.beam_angle}")
            
        if 'array_type' in kwargs:
            old_val = self.array_type
            self.array_type = kwargs['array_type'].lower()
            logging.debug(f"    Updated array_type: {old_val} -> {self.array_type}")
            
        if 'element_spacing' in kwargs:
            old_val = self.element_spacing
            self.element_spacing = kwargs['element_spacing'] * self.wavelength
            logging.debug(f"    Updated element_spacing: {old_val} -> {self.element_spacing}")
            
        if 'mode' in kwargs:
            old_val = self.mode
            self.mode = kwargs['mode'].lower()
            logging.debug(f"    Updated mode: {old_val} -> {self.mode}")
            
        logging.info(f"Parameters updated: {kwargs}")
        logging.debug(f"update_parameters completed")