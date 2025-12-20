"""
Phased Array Class
Handles the geometry and properties of a phased array antenna/transducer.
"""
import numpy as np
from typing import Literal, Tuple, List, Optional


class PhasedArray:
    """
    Represents a phased array with configurable geometry and parameters.
    Supports linear and curved array geometries.
    """
    
    def __init__(
        self,
        num_elements: int = 8,
        element_spacing: float = 0.5,  # in wavelengths
        geometry: Literal['linear', 'curved'] = 'linear',
        curvature_radius: float = 10.0,  # for curved arrays
        position: Tuple[float, float] = (0.0, 0.0),
        orientation: float = 0.0,  # rotation angle in degrees
        array_id: Optional[str] = None
    ):
        """
        Initialize a phased array.
        
        Args:
            num_elements: Number of antenna/transducer elements
            element_spacing: Spacing between elements (in wavelengths)
            geometry: 'linear' or 'curved'
            curvature_radius: Radius of curvature for curved arrays (in wavelengths)
            position: (x, y) position of array center
            orientation: Rotation angle in degrees
            array_id: Unique identifier for this array
        """
        self.num_elements = num_elements
        self.element_spacing = element_spacing
        self.geometry = geometry
        self.curvature_radius = curvature_radius
        self.position = np.array(position)
        self.orientation = orientation
        self.array_id = array_id or f"array_{id(self)}"
        
        # Element positions (computed)
        self._element_positions = None
        self._element_normals = None
        
        # Phase shifts and delays for each element
        self._phase_shifts = np.zeros(num_elements)
        self._delays = np.zeros(num_elements)
        self._amplitudes = np.ones(num_elements)
        
        # Compute element positions
        self._compute_element_positions()
    
    def _compute_element_positions(self):
        """Compute the positions of each element based on geometry."""
        n = self.num_elements
        
        if self.geometry == 'linear':
            # Linear array: elements along a straight line
            # Center the array at origin, then translate
            indices = np.arange(n) - (n - 1) / 2
            local_x = indices * self.element_spacing
            local_y = np.zeros(n)
            
            # All normals point in +y direction for linear array
            self._element_normals = np.column_stack([
                np.zeros(n),
                np.ones(n)
            ])
            
        else:  # curved
            # Curved array: elements along an arc
            # Arc length = (n-1) * element_spacing
            arc_length = (n - 1) * self.element_spacing
            
            # Angle subtended by the arc
            if self.curvature_radius > 0:
                total_angle = arc_length / self.curvature_radius
            else:
                total_angle = np.pi / 2  # Default 90 degrees
            
            # Distribute elements along the arc
            angles = np.linspace(-total_angle / 2, total_angle / 2, n)
            
            # Positions on the arc (centered at curvature center)
            local_x = self.curvature_radius * np.sin(angles)
            local_y = self.curvature_radius * (1 - np.cos(angles))
            
            # Normals point radially outward
            self._element_normals = np.column_stack([
                np.sin(angles),
                np.cos(angles)
            ])
        
        # Apply rotation
        theta = np.radians(self.orientation)
        cos_t, sin_t = np.cos(theta), np.sin(theta)
        rotation_matrix = np.array([
            [cos_t, -sin_t],
            [sin_t, cos_t]
        ])
        
        local_positions = np.column_stack([local_x, local_y])
        rotated_positions = local_positions @ rotation_matrix.T
        
        # Rotate normals too
        self._element_normals = self._element_normals @ rotation_matrix.T
        
        # Translate to array position
        self._element_positions = rotated_positions + self.position
    
    @property
    def element_positions(self) -> np.ndarray:
        """Get the (x, y) positions of all elements."""
        return self._element_positions.copy()
    
    @property
    def element_normals(self) -> np.ndarray:
        """Get the normal vectors for all elements."""
        return self._element_normals.copy()
    
    def set_steering_angle(self, angle_degrees: float, frequency: float, speed: float = 343.0):
        """
        Set phase shifts to steer the beam to a specific angle.
        
        Args:
            angle_degrees: Steering angle in degrees (0 = broadside)
            frequency: Operating frequency in Hz
            speed: Wave propagation speed (m/s), default is speed of sound in air
        """
        wavelength = speed / frequency
        k = 2 * np.pi / wavelength  # wave number
        
        # Convert angle to radians
        theta = np.radians(angle_degrees)
        
        # For linear array, phase shift = k * d * sin(theta) for each element
        # where d is the distance from reference element
        if self.geometry == 'linear':
            indices = np.arange(self.num_elements) - (self.num_elements - 1) / 2
            d = indices * self.element_spacing * wavelength
            self._phase_shifts = -k * d * np.sin(theta)
        else:
            # For curved array, compute based on element positions
            # Project positions onto steering direction
            steering_vector = np.array([np.sin(theta), np.cos(theta)])
            projections = self._element_positions @ steering_vector
            projections -= projections.mean()  # Center
            self._phase_shifts = -k * projections
    
    def set_focus_point(self, focus_x: float, focus_y: float, frequency: float, speed: float = 343.0):
        """
        Set delays to focus the beam at a specific point.
        
        Args:
            focus_x, focus_y: Focus point coordinates
            frequency: Operating frequency in Hz
            speed: Wave propagation speed (m/s)
        """
        wavelength = speed / frequency
        focus_point = np.array([focus_x, focus_y])
        
        # Compute distance from each element to focus point
        distances = np.linalg.norm(self._element_positions - focus_point, axis=1)
        
        # Delays to make all waves arrive at focus point simultaneously
        max_distance = distances.max()
        self._delays = (max_distance - distances) / speed
        
        # Convert delays to phase shifts
        self._phase_shifts = 2 * np.pi * frequency * self._delays
    
    def set_custom_phases(self, phases: np.ndarray):
        """Set custom phase shifts for each element."""
        if len(phases) != self.num_elements:
            raise ValueError(f"Expected {self.num_elements} phases, got {len(phases)}")
        self._phase_shifts = np.array(phases)
    
    def set_uniform_phase(self, phase: float):
        """Set uniform phase shift for all elements (progressive phase)."""
        # Apply progressive phase shift across elements
        indices = np.arange(self.num_elements)
        self._phase_shifts = indices * phase
    
    def set_custom_amplitudes(self, amplitudes: np.ndarray):
        """Set custom amplitudes for each element (for apodization/windowing)."""
        if len(amplitudes) != self.num_elements:
            raise ValueError(f"Expected {self.num_elements} amplitudes, got {len(amplitudes)}")
        self._amplitudes = np.array(amplitudes)
    
    def get_phases(self) -> np.ndarray:
        """Get current phase shifts."""
        return self._phase_shifts.copy()
    
    def get_amplitudes(self) -> np.ndarray:
        """Get current amplitudes."""
        return self._amplitudes.copy()
    
    def update_parameters(
        self,
        num_elements: Optional[int] = None,
        element_spacing: Optional[float] = None,
        geometry: Optional[str] = None,
        curvature_radius: Optional[float] = None,
        position: Optional[Tuple[float, float]] = None,
        orientation: Optional[float] = None
    ):
        """Update array parameters and recompute element positions."""
        if num_elements is not None:
            self.num_elements = num_elements
            self._phase_shifts = np.zeros(num_elements)
            self._delays = np.zeros(num_elements)
            self._amplitudes = np.ones(num_elements)
        
        if element_spacing is not None:
            self.element_spacing = element_spacing
        
        if geometry is not None:
            self.geometry = geometry
        
        if curvature_radius is not None:
            self.curvature_radius = curvature_radius
        
        if position is not None:
            self.position = np.array(position)
        
        if orientation is not None:
            self.orientation = orientation
        
        self._compute_element_positions()
    
    def to_dict(self) -> dict:
        """Serialize array to dictionary."""
        return {
            'array_id': self.array_id,
            'num_elements': self.num_elements,
            'element_spacing': self.element_spacing,
            'geometry': self.geometry,
            'curvature_radius': self.curvature_radius,
            'position': self.position.tolist(),
            'orientation': self.orientation,
            'element_positions': self._element_positions.tolist(),
            'phase_shifts': self._phase_shifts.tolist(),
            'amplitudes': self._amplitudes.tolist()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PhasedArray':
        """Create array from dictionary."""
        array = cls(
            num_elements=data['num_elements'],
            element_spacing=data['element_spacing'],
            geometry=data['geometry'],
            curvature_radius=data.get('curvature_radius', 10.0),
            position=tuple(data['position']),
            orientation=data.get('orientation', 0.0),
            array_id=data.get('array_id')
        )
        
        if 'phase_shifts' in data:
            array._phase_shifts = np.array(data['phase_shifts'])
        if 'amplitudes' in data:
            array._amplitudes = np.array(data['amplitudes'])
        
        return array


class MultiArraySystem:
    """
    Manages multiple phased arrays in a system.
    Allows for complex beamforming scenarios with multiple arrays.
    """
    
    def __init__(self):
        """Initialize multi-array system"""
        self.arrays = []
        self.array_locations = []
    
    def add_array(self, phased_array, location=(0, 0)):
        """
        Add a phased array to the system
        
        Args:
            phased_array: PhasedArray instance
            location: (x, y) location of array center
        """
        self.arrays.append(phased_array)
        self.array_locations.append(location)
    
    def remove_array(self, index):
        """Remove array at given index"""
        if 0 <= index < len(self.arrays):
            self.arrays.pop(index)
            self.array_locations.pop(index)
    
    def get_all_positions(self):
        """Get positions of all elements in all arrays"""
        all_positions = []
        
        for idx, (array, (loc_x, loc_y)) in enumerate(zip(self.arrays, self.array_locations)):
            positions = array.element_positions
            # Offset by array location
            positions = positions + np.array([loc_x, loc_y])
            all_positions.append(positions)
        
        if all_positions:
            return np.vstack(all_positions)
        else:
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
        if len(self.arrays) != len(steering_angles):
            raise ValueError(f"Number of steering angles ({len(steering_angles)}) must match number of arrays ({len(self.arrays)})")
        
        combined_factor = np.zeros(len(observation_angles), dtype=complex)
        
        for array, steering_angle in zip(self.arrays, steering_angles):
            # Use the array's steering angle method
            array.set_steering_angle(steering_angle, 1e9, 3e8)  # Default frequency/speed
            # Compute pattern contribution (simplified)
            positions = array.element_positions
            phases = array.get_phases()
            
            theta_rad = np.deg2rad(observation_angles)
            k = 2 * np.pi / (3e8 / 1e9)  # wave number
            
            for angle_idx, angle in enumerate(theta_rad):
                field_at_angle = 0j
                for i, (pos, phase) in enumerate(zip(positions, phases)):
                    # Simplified: assume far field
                    field_at_angle += np.exp(1j * (k * pos[0] * np.sin(angle) + phase))
                combined_factor[angle_idx] += field_at_angle
        
        return combined_factor
