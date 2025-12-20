"""
Beamformer Class
Handles beam pattern computation and interference field calculation.
"""
import numpy as np
from typing import List, Tuple, Optional
from .phased_array import PhasedArray


class Beamformer:
    """
    Computes beam patterns and interference fields for phased arrays.
    Supports multiple arrays and multiple frequencies.
    """
    
    def __init__(
        self,
        frequencies: List[float] = None,
        speed: float = 343.0,  # Speed of sound in air (m/s)
        field_size: Tuple[float, float] = (20.0, 20.0),  # Field dimensions
        resolution: int = 200  # Grid resolution
    ):
        """
        Initialize the beamformer.
        
        Args:
            frequencies: List of operating frequencies in Hz
            speed: Wave propagation speed (m/s)
            field_size: (width, height) of computation field
            resolution: Number of grid points in each dimension
        """
        self.frequencies = frequencies or [1000.0]  # Default 1kHz
        self.speed = speed
        self.field_size = field_size
        self.resolution = resolution
        
        # Arrays in the system
        self.arrays: List[PhasedArray] = []
        
        # Computed fields
        self._field_grid_x = None
        self._field_grid_y = None
        self._interference_field = None
        self._beam_profile = None
        
        # Create computation grid
        self._create_grid()
    
    def _create_grid(self):
        """Create the computation grid."""
        w, h = self.field_size
        x = np.linspace(-w/2, w/2, self.resolution)
        y = np.linspace(0, h, self.resolution)  # y starts from 0 (array position)
        self._field_grid_x, self._field_grid_y = np.meshgrid(x, y)
    
    def add_array(self, array: PhasedArray):
        """Add a phased array to the system."""
        self.arrays.append(array)
    
    def remove_array(self, array_id: str):
        """Remove a phased array by ID."""
        self.arrays = [a for a in self.arrays if a.array_id != array_id]
    
    def clear_arrays(self):
        """Remove all arrays."""
        self.arrays = []
    
    def get_array(self, array_id: str) -> Optional[PhasedArray]:
        """Get an array by ID."""
        for array in self.arrays:
            if array.array_id == array_id:
                return array
        return None
    
    def set_frequencies(self, frequencies: List[float]):
        """Set operating frequencies."""
        self.frequencies = frequencies
    
    def set_speed(self, speed: float):
        """Set wave propagation speed."""
        self.speed = speed
    
    def update_field_parameters(
        self,
        field_size: Optional[Tuple[float, float]] = None,
        resolution: Optional[int] = None
    ):
        """Update field computation parameters."""
        if field_size is not None:
            self.field_size = field_size
        if resolution is not None:
            self.resolution = resolution
        self._create_grid()
    
    def compute_interference_field(self) -> np.ndarray:
        """
        Compute the interference field from all arrays.
        
        Returns:
            2D numpy array of complex field values
        """
        if not self.arrays:
            self._interference_field = np.zeros((self.resolution, self.resolution), dtype=complex)
            return self._interference_field
        
        # Initialize field
        total_field = np.zeros((self.resolution, self.resolution), dtype=complex)
        
        for freq in self.frequencies:
            wavelength = self.speed / freq
            k = 2 * np.pi / wavelength  # wave number
            
            for array in self.arrays:
                positions = array.element_positions
                phases = array.get_phases()
                amplitudes = array.get_amplitudes()
                
                for i in range(array.num_elements):
                    # Distance from this element to each grid point
                    dx = self._field_grid_x - positions[i, 0]
                    dy = self._field_grid_y - positions[i, 1]
                    r = np.sqrt(dx**2 + dy**2)
                    
                    # Avoid division by zero
                    r = np.maximum(r, wavelength / 100)
                    
                    # Spherical wave with phase shift
                    # Using 2D approximation (cylindrical waves)
                    element_field = amplitudes[i] * np.exp(1j * (k * r + phases[i])) / np.sqrt(r)
                    total_field += element_field
        
        # Normalize by number of frequencies
        total_field /= len(self.frequencies)
        
        self._interference_field = total_field
        return total_field
    
    def compute_beam_profile(self, distance: float = 10.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute the beam profile at a given distance.
        
        Args:
            distance: Distance from array center for profile computation
            
        Returns:
            Tuple of (angles, intensities) arrays
        """
        if not self.arrays:
            angles = np.linspace(-90, 90, 181)
            return angles, np.zeros_like(angles)
        
        # Compute beam profile angles
        angles = np.linspace(-90, 90, 361)
        intensities = np.zeros_like(angles)
        
        for freq in self.frequencies:
            wavelength = self.speed / freq
            k = 2 * np.pi / wavelength
            
            for angle_idx, angle in enumerate(angles):
                theta = np.radians(angle)
                
                # Point at given angle and distance
                x = distance * np.sin(theta)
                y = distance * np.cos(theta)
                
                field_at_point = 0j
                
                for array in self.arrays:
                    positions = array.element_positions
                    phases = array.get_phases()
                    amplitudes = array.get_amplitudes()
                    
                    for i in range(array.num_elements):
                        dx = x - positions[i, 0]
                        dy = y - positions[i, 1]
                        r = np.sqrt(dx**2 + dy**2)
                        r = max(r, wavelength / 100)
                        
                        field_at_point += amplitudes[i] * np.exp(1j * (k * r + phases[i])) / np.sqrt(r)
                
                intensities[angle_idx] += np.abs(field_at_point)**2
        
        # Normalize
        intensities /= len(self.frequencies)
        if intensities.max() > 0:
            intensities /= intensities.max()
        
        self._beam_profile = (angles, intensities)
        return angles, intensities
    
    def get_intensity_field(self) -> np.ndarray:
        """Get the intensity (magnitude squared) of the interference field."""
        if self._interference_field is None:
            self.compute_interference_field()
        return np.abs(self._interference_field)**2
    
    def get_phase_field(self) -> np.ndarray:
        """Get the phase of the interference field."""
        if self._interference_field is None:
            self.compute_interference_field()
        return np.angle(self._interference_field)
    
    def get_field_coordinates(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get the x, y coordinates of the field grid."""
        return self._field_grid_x, self._field_grid_y
    
    def steer_all_arrays(self, angle_degrees: float):
        """Steer all arrays to the same angle."""
        for array in self.arrays:
            array.set_steering_angle(angle_degrees, self.frequencies[0], self.speed)
    
    def focus_all_arrays(self, focus_x: float, focus_y: float):
        """Focus all arrays to the same point."""
        for array in self.arrays:
            array.set_focus_point(focus_x, focus_y, self.frequencies[0], self.speed)
    
    def get_field_data_for_visualization(self) -> dict:
        """
        Get all field data needed for visualization.
        
        Returns:
            Dictionary containing intensity field, phase field, beam profile, etc.
        """
        # Compute fields
        self.compute_interference_field()
        angles, profile = self.compute_beam_profile()
        
        intensity = self.get_intensity_field()
        phase = self.get_phase_field()
        
        # Normalize intensity for display
        intensity_normalized = intensity / (intensity.max() + 1e-10)
        
        # Convert to dB scale for better visualization
        intensity_db = 10 * np.log10(intensity_normalized + 1e-10)
        intensity_db = np.clip(intensity_db, -40, 0)  # Clip to -40dB
        
        # Collect element positions from all arrays
        element_positions = []
        for array in self.arrays:
            element_positions.extend(array.element_positions.tolist())
        
        return {
            'intensity': intensity_normalized.tolist(),
            'intensity_db': intensity_db.tolist(),
            'phase': phase.tolist(),
            'beam_profile': {
                'angles': angles.tolist(),
                'intensities': profile.tolist()
            },
            'field_extent': {
                'x_min': -self.field_size[0] / 2,
                'x_max': self.field_size[0] / 2,
                'y_min': 0,
                'y_max': self.field_size[1]
            },
            'element_positions': element_positions,
            'arrays': [array.to_dict() for array in self.arrays]
        }
    
    def to_dict(self) -> dict:
        """Serialize beamformer state to dictionary."""
        return {
            'frequencies': self.frequencies,
            'speed': self.speed,
            'field_size': self.field_size,
            'resolution': self.resolution,
            'arrays': [array.to_dict() for array in self.arrays]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Beamformer':
        """Create beamformer from dictionary."""
        beamformer = cls(
            frequencies=data.get('frequencies', [1000.0]),
            speed=data.get('speed', 343.0),
            field_size=tuple(data.get('field_size', (20.0, 20.0))),
            resolution=data.get('resolution', 200)
        )
        
        for array_data in data.get('arrays', []):
            array = PhasedArray.from_dict(array_data)
            beamformer.add_array(array)
        
        return beamformer
