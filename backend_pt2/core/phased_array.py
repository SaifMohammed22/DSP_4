import numpy as np
import logging

logging.basicConfig(
    filename='beamforming.log',
    level=logging.DEBUG,  # Changed to DEBUG level to see debug messages
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PhasedArray:
    """
    Phased Array class implementing OOP principles.
    Encapsulates array geometry, element management, and phase calculations.
    """
    
    def __init__(self, num_elements, frequency, geometry='linear', 
                 element_spacing=None, curvature_radius=None):
        """
        Initialize phased array
        
        Args:
            num_elements: Number of array elements
            frequency: Operating frequency in Hz
            geometry: 'linear' or 'curved'
            element_spacing: Distance between elements in wavelengths
            curvature_radius: Radius for curved arrays
        """
        logging.debug(f"PhasedArray.__init__ called with parameters:")
        logging.debug(f"  num_elements: {num_elements}")
        logging.debug(f"  frequency: {frequency}")
        logging.debug(f"  geometry: {geometry}")
        logging.debug(f"  element_spacing: {element_spacing}")
        logging.debug(f"  curvature_radius: {curvature_radius}")
        
        self.num_elements = num_elements
        self.frequency = frequency
        self.geometry = geometry.lower()
        self.propagation_speed = 3e8  # Default to speed of light
        
        # Calculate wavelength
        self.wavelength = self.propagation_speed / frequency
        logging.debug(f"  Calculated wavelength: {self.wavelength}")
        
        # Set element spacing
        if element_spacing is None:
            self.element_spacing = self.wavelength / 2
            logging.debug(f"  Using default element spacing: λ/2 = {self.element_spacing}")
        else:
            self.element_spacing = element_spacing * self.wavelength
            logging.debug(f"  Using custom element spacing: {element_spacing}λ = {self.element_spacing}")
        
        # Set curvature radius
        if curvature_radius is None and self.geometry == 'curved':
            self.curvature_radius = (num_elements - 1) * self.element_spacing / np.pi
            logging.debug(f"  Calculated curvature_radius: {self.curvature_radius}")
        else:
            self.curvature_radius = curvature_radius if curvature_radius else 1.0
            logging.debug(f"  Using curvature_radius: {self.curvature_radius}")
        
        # Calculate element positions
        self.positions = self._calculate_positions()
        logging.debug(f"  Calculated positions array shape: {self.positions.shape}")
        
        logging.info(f"PhasedArray created: {num_elements} elements, {geometry} geometry")
        logging.debug(f"PhasedArray.__init__ completed - instance ID: {id(self)}")
    
    def _calculate_positions(self):
        """Calculate 2D positions of array elements"""
        logging.debug(f"PhasedArray._calculate_positions called")
        logging.debug(f"  geometry: {self.geometry}")
        logging.debug(f"  num_elements: {self.num_elements}")
        logging.debug(f"  element_spacing: {self.element_spacing}")
        logging.debug(f"  curvature_radius: {self.curvature_radius}")
        
        if self.geometry == 'linear':
            logging.debug(f"  Calculating linear array positions")
            x = np.arange(-(self.num_elements - 1) / 2, 
                         (self.num_elements) / 2) * self.element_spacing
            y = np.zeros_like(x)
            logging.debug(f"  Linear x range: {x[0]:.3f} to {x[-1]:.3f}")
        else:  # curved
            logging.debug(f"  Calculating curved array positions")
            arc_angle = np.pi
            theta = np.linspace(-arc_angle, 0, self.num_elements)
            logging.debug(f"  theta range: {theta[0]:.3f} to {theta[-1]:.3f} radians")
            x = self.curvature_radius * np.cos(theta)
            y = self.curvature_radius * np.sin(theta)
            logging.debug(f"  Curved x range: {x[0]:.3f} to {x[-1]:.3f}")
            logging.debug(f"  Curved y range: {y[0]:.3f} to {y[-1]:.3f}")
        
        positions = np.column_stack([x, y])
        logging.debug(f"  Positions array shape: {positions.shape}")
        return positions
    
    def get_positions(self):
        """Return array element positions"""
        logging.debug(f"PhasedArray.get_positions called")
        x_pos = self.positions[:, 0]
        y_pos = self.positions[:, 1]
        logging.debug(f"  Returning x_pos shape: {x_pos.shape}, y_pos shape: {y_pos.shape}")
        return x_pos, y_pos
    
    def calculate_phase_shifts(self, steering_angle_deg):
        """
        Calculate phase shifts for beam steering
        
        Args:
            steering_angle_deg: Desired beam direction in degrees
            
        Returns:
            Array of phase shifts for each element
        """
        logging.debug(f"PhasedArray.calculate_phase_shifts called: steering_angle_deg={steering_angle_deg}")
        logging.debug(f"  geometry: {self.geometry}")
        logging.debug(f"  wavelength: {self.wavelength}")
        
        steering_angle_rad = np.deg2rad(steering_angle_deg)
        k = 2 * np.pi / self.wavelength
        logging.debug(f"  steering_angle_rad: {steering_angle_rad:.3f}")
        logging.debug(f"  wave number k: {k:.3f}")
        
        if self.geometry == 'linear':
            logging.debug(f"  Calculating linear array phase shifts")
            # Linear array: phase = k * d * sin(theta) * n
            phase_shifts = k * self.element_spacing * np.sin(steering_angle_rad) * \
                          np.arange(self.num_elements)
            logging.debug(f"  Linear phase_shifts shape: {phase_shifts.shape}")
            logging.debug(f"  Linear phase_shifts range: {phase_shifts[0]:.3f} to {phase_shifts[-1]:.3f}")
        else:
            logging.debug(f"  Calculating curved array phase shifts")
            # Curved array: more complex phase calculation
            x_center, y_center = 0, 0
            phase_shifts = np.zeros(self.num_elements)
            
            for i, (x, y) in enumerate(self.positions):
                element_angle = np.arctan2(y - y_center, x - x_center)
                phase_shifts[i] = k * self.curvature_radius * \
                                 np.cos(element_angle - steering_angle_rad)
                
                if i == 0:  # Log first element for debugging
                    logging.debug(f"  Element 0: position=({x:.3f}, {y:.3f}), element_angle={element_angle:.3f}")
                    logging.debug(f"  Element 0 phase_shift: {phase_shifts[0]:.3f}")
            
            logging.debug(f"  Curved phase_shifts shape: {phase_shifts.shape}")
            logging.debug(f"  Curved phase_shifts range: {phase_shifts.min():.3f} to {phase_shifts.max():.3f}")
        
        logging.debug(f"  Returning phase_shifts array")
        return phase_shifts
    
    def compute_array_factor(self, observation_angles, steering_angle_deg):
        """
        Compute array factor for given observation angles
        
        Args:
            observation_angles: Array of angles in degrees
            steering_angle_deg: Steering angle in degrees
            
        Returns:
            Complex array factor
        """
        logging.debug(f"PhasedArray.compute_array_factor called")
        logging.debug(f"  observation_angles shape: {observation_angles.shape}")
        logging.debug(f"  steering_angle_deg: {steering_angle_deg}")
        logging.debug(f"  geometry: {self.geometry}")
        
        theta = np.deg2rad(observation_angles)
        steering_rad = np.deg2rad(steering_angle_deg)
        k = 2 * np.pi / self.wavelength
        logging.debug(f"  theta (rad) range: {theta[0]:.3f} to {theta[-1]:.3f}")
        logging.debug(f"  steering_rad: {steering_rad:.3f}")
        logging.debug(f"  wave number k: {k:.3f}")
        
        array_factor = np.zeros_like(theta, dtype=complex)
        logging.debug(f"  array_factor initialized - shape: {array_factor.shape}, dtype: {array_factor.dtype}")
        
        x_pos, y_pos = self.get_positions()
        logging.debug(f"  Number of elements: {len(x_pos)}")
        
        for idx, (x, y) in enumerate(zip(x_pos, y_pos)):
            if self.geometry == 'linear':
                path_diff = x * (np.sin(theta) - np.sin(steering_rad))
            else:
                dx = x
                dy = y - self.curvature_radius
                path_diff = (dx * np.sin(theta) + dy * np.cos(theta) - 
                           (dx * np.sin(steering_rad) + dy * np.cos(steering_rad)))
            
            phase = k * path_diff
            array_factor += np.exp(1j * phase)
            
            if idx == 0:  # Log first element for debugging
                logging.debug(f"  Element 0: position=({x:.3f}, {y:.3f})")
                logging.debug(f"  Element 0 path_diff range: {path_diff.min():.3f} to {path_diff.max():.3f}")
        
        logging.debug(f"  array_factor magnitude range: {np.abs(array_factor).min():.3f} to {np.abs(array_factor).max():.3f}")
        logging.debug(f"  Returning array_factor")
        return array_factor
    
    def set_propagation_speed(self, speed):
        """Update propagation speed and recalculate wavelength"""
        logging.debug(f"PhasedArray.set_propagation_speed called: speed={speed}")
        logging.debug(f"  Previous propagation_speed: {self.propagation_speed}")
        logging.debug(f"  Previous wavelength: {self.wavelength}")
        
        self.propagation_speed = speed
        self.wavelength = speed / self.frequency
        self.element_spacing = self.wavelength / 2
        self.positions = self._calculate_positions()
        
        logging.debug(f"  New propagation_speed: {self.propagation_speed}")
        logging.debug(f"  New wavelength: {self.wavelength}")
        logging.debug(f"  New element_spacing: {self.element_spacing}")
        logging.info(f"Propagation speed updated to {speed} m/s")
        logging.debug(f"  Positions recalculated")
    
    def update_geometry(self, geometry, curvature_radius=None):
        """Update array geometry"""
        logging.debug(f"PhasedArray.update_geometry called: geometry={geometry}, curvature_radius={curvature_radius}")
        logging.debug(f"  Previous geometry: {self.geometry}")
        logging.debug(f"  Previous curvature_radius: {self.curvature_radius}")
        
        self.geometry = geometry.lower()
        if curvature_radius:
            self.curvature_radius = curvature_radius
        self.positions = self._calculate_positions()
        
        logging.debug(f"  New geometry: {self.geometry}")
        logging.debug(f"  New curvature_radius: {self.curvature_radius}")
        logging.info(f"Geometry updated to {geometry}")
        logging.debug(f"  Positions recalculated")
    
    def update_num_elements(self, num_elements):
        """Update number of elements"""
        logging.debug(f"PhasedArray.update_num_elements called: num_elements={num_elements}")
        logging.debug(f"  Previous num_elements: {self.num_elements}")
        
        self.num_elements = num_elements
        self.positions = self._calculate_positions()
        
        logging.debug(f"  New num_elements: {self.num_elements}")
        logging.info(f"Number of elements updated to {num_elements}")
        logging.debug(f"  Positions recalculated")


class MultiArraySystem:
    """
    Manages multiple phased arrays in a system.
    Allows for complex beamforming scenarios with multiple arrays.
    """
    
    def __init__(self):
        """Initialize multi-array system"""
        logging.debug(f"MultiArraySystem.__init__ called")
        self.arrays = []
        self.array_locations = []
        logging.info("MultiArraySystem initialized")
        logging.debug(f"MultiArraySystem.__init__ completed - instance ID: {id(self)}")
    
    def add_array(self, phased_array, location=(0, 0)):
        """
        Add a phased array to the system
        
        Args:
            phased_array: PhasedArray instance
            location: (x, y) location of array center
        """
        logging.debug(f"MultiArraySystem.add_array called")
        logging.debug(f"  phased_array type: {type(phased_array)}, instance ID: {id(phased_array)}")
        logging.debug(f"  location: {location}")
        logging.debug(f"  Current number of arrays: {len(self.arrays)}")
        
        self.arrays.append(phased_array)
        self.array_locations.append(location)
        
        logging.info(f"Array added at location {location}")
        logging.debug(f"  New number of arrays: {len(self.arrays)}")
        logging.debug(f"  Arrays list: {[id(arr) for arr in self.arrays]}")
        logging.debug(f"  Locations list: {self.array_locations}")
    
    def remove_array(self, index):
        """Remove array at given index"""
        logging.debug(f"MultiArraySystem.remove_array called: index={index}")
        logging.debug(f"  Current number of arrays: {len(self.arrays)}")
        
        if 0 <= index < len(self.arrays):
            removed_array_id = id(self.arrays[index])
            self.arrays.pop(index)
            self.array_locations.pop(index)
            
            logging.info(f"Array at index {index} removed")
            logging.debug(f"  Removed array ID: {removed_array_id}")
            logging.debug(f"  New number of arrays: {len(self.arrays)}")
        else:
            logging.warning(f"Attempted to remove array at invalid index: {index}")
    
    def get_all_positions(self):
        """Get positions of all elements in all arrays"""
        logging.debug(f"MultiArraySystem.get_all_positions called")
        logging.debug(f"  Number of arrays: {len(self.arrays)}")
        
        all_positions = []
        
        for idx, (array, (loc_x, loc_y)) in enumerate(zip(self.arrays, self.array_locations)):
            x_pos, y_pos = array.get_positions()
            # Offset by array location
            x_pos = x_pos + loc_x
            y_pos = y_pos + loc_y
            array_positions = np.column_stack([x_pos, y_pos])
            all_positions.append(array_positions)
            
            logging.debug(f"  Array {idx}: shape={array_positions.shape}, location=({loc_x}, {loc_y})")
            if idx == 0 and len(array_positions) > 0:
                logging.debug(f"    First position: {array_positions[0]}")
                logging.debug(f"    Last position: {array_positions[-1]}")
        
        if all_positions:
            result = np.vstack(all_positions)
            logging.debug(f"  Combined positions shape: {result.shape}")
            logging.debug(f"  Returning combined positions array")
            return result
        else:
            logging.debug(f"  No arrays in system, returning empty array")
            return np.array([])
    
    def compute_combined_pattern(self, observation_angles, steering_angles):
        """
        Compute combined radiation pattern from all arrays
        
        Args:
            observation_angles: Array of observation angles in degrees
            steering_angles: List of steering angles for each array
            
        Returns:
            Combined array factor
        """
        logging.debug(f"MultiArraySystem.compute_combined_pattern called")
        logging.debug(f"  observation_angles shape: {observation_angles.shape}")
        logging.debug(f"  steering_angles: {steering_angles}")
        logging.debug(f"  Number of arrays: {len(self.arrays)}")
        
        if len(self.arrays) != len(steering_angles):
            error_msg = f"Number of steering angles ({len(steering_angles)}) must match number of arrays ({len(self.arrays)})"
            logging.error(error_msg)
            raise ValueError(error_msg)
        
        combined_factor = np.zeros(len(observation_angles), dtype=complex)
        logging.debug(f"  combined_factor initialized - shape: {combined_factor.shape}, dtype: {combined_factor.dtype}")
        
        for idx, (array, steering_angle) in enumerate(zip(self.arrays, steering_angles)):
            logging.debug(f"  Processing array {idx} with steering_angle: {steering_angle}")
            array_factor = array.compute_array_factor(observation_angles, steering_angle)
            combined_factor += array_factor
            logging.debug(f"  Array {idx} factor magnitude range: {np.abs(array_factor).min():.3f} to {np.abs(array_factor).max():.3f}")
        
        logging.debug(f"  Combined factor magnitude range: {np.abs(combined_factor).min():.3f} to {np.abs(combined_factor).max():.3f}")
        logging.debug(f"  Returning combined_factor")
        return combined_factor