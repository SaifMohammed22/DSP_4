import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

class ArrayType(Enum):
    LINEAR = "linear"
    CURVED = "curved"
    CIRCULAR = "circular"
    RECTANGULAR = "rectangular"

class ElementType(Enum):
    ISOTROPIC = "isotropic"
    DIPOLE = "dipole"
    PATCH = "patch"
    CUSTOM = "custom"

@dataclass
class ArrayElement:
    """Represents a single element in an array"""
    position: Tuple[float, float]  # (x, y) position
    amplitude: float = 1.0
    phase: float = 0.0
    delay: float = 0.0
    element_type: ElementType = ElementType.ISOTROPIC
    orientation: float = 0.0  # Degrees
    
    def to_dict(self) -> Dict:
        return {
            'position': list(self.position),
            'amplitude': self.amplitude,
            'phase': self.phase,
            'delay': self.delay,
            'element_type': self.element_type.value,
            'orientation': self.orientation
        }

class PhasedArray:
    """Model representing a phased array"""
    
    def __init__(self, 
                 array_id: str,
                 array_type: ArrayType = ArrayType.LINEAR,
                 num_elements: int = 8,
                 spacing: float = 0.5,  # in wavelengths
                 position: Tuple[float, float] = (0.0, 0.0),
                 orientation: float = 0.0,
                 curvature: float = 0.0):
        
        self.array_id = array_id
        self.array_type = array_type
        self.num_elements = num_elements
        self.spacing = spacing
        self.position = position
        self.orientation = orientation
        self.curvature = curvature
        
        # Initialize elements
        self.elements: List[ArrayElement] = []
        self._initialize_elements()
        
        # Array parameters
        self.frequency: float = 2.4e9  # Default frequency
        self.wavelength: float = self._calculate_wavelength()
    
    def _calculate_wavelength(self) -> float:
        """Calculate wavelength from frequency"""
        speed_of_light = 3e8  # m/s
        return speed_of_light / self.frequency if self.frequency > 0 else 0.125
    
    def _initialize_elements(self):
        """Initialize array elements based on geometry"""
        self.elements = []
        
        if self.array_type == ArrayType.LINEAR:
            self._create_linear_array()
        elif self.array_type == ArrayType.CURVED:
            self._create_curved_array()
        elif self.array_type == ArrayType.CIRCULAR:
            self._create_circular_array()
        elif self.array_type == ArrayType.RECTANGULAR:
            self._create_rectangular_array()
    
    def _create_linear_array(self):
        """Create linear array elements"""
        start_x = - (self.num_elements - 1) * self.spacing * self.wavelength / 2
        start_y = 0
        
        for i in range(self.num_elements):
            x = self.position[0] + start_x + i * self.spacing * self.wavelength
            y = self.position[1] + start_y
            
            # Rotate if needed
            if self.orientation != 0:
                angle_rad = np.radians(self.orientation)
                x_rot = x * np.cos(angle_rad) - y * np.sin(angle_rad)
                y_rot = x * np.sin(angle_rad) + y * np.cos(angle_rad)
                x, y = x_rot, y_rot
            
            element = ArrayElement(position=(float(x), float(y)))
            self.elements.append(element)
    
    def _create_curved_array(self):
        """Create curved array elements"""
        if self.curvature == 0:
            self._create_linear_array()
            return
        
        radius = 1.0 / self.curvature
        angle_range = np.arcsin((self.num_elements - 1) * self.spacing / (2 * radius))
        angles = np.linspace(-angle_range, angle_range, self.num_elements)
        
        for i, angle in enumerate(angles):
            x = self.position[0] + radius * np.sin(angle)
            y = self.position[1] + radius * (1 - np.cos(angle))
            
            element = ArrayElement(position=(float(x), float(y)))
            self.elements.append(element)
    
    def _create_circular_array(self):
        """Create circular array elements"""
        radius = self.spacing * self.num_elements / (2 * np.pi)
        angles = np.linspace(0, 2 * np.pi, self.num_elements, endpoint=False)
        
        for i, angle in enumerate(angles):
            x = self.position[0] + radius * np.cos(angle)
            y = self.position[1] + radius * np.sin(angle)
            
            element = ArrayElement(position=(float(x), float(y)))
            self.elements.append(element)
    
    def _create_rectangular_array(self):
        """Create rectangular array elements"""
        # For simplicity, create square array
        side_elements = int(np.ceil(np.sqrt(self.num_elements)))
        spacing_x = self.spacing * self.wavelength
        spacing_y = self.spacing * self.wavelength
        
        start_x = - (side_elements - 1) * spacing_x / 2
        start_y = - (side_elements - 1) * spacing_y / 2
        
        element_count = 0
        for i in range(side_elements):
            for j in range(side_elements):
                if element_count >= self.num_elements:
                    break
                
                x = self.position[0] + start_x + j * spacing_x
                y = self.position[1] + start_y + i * spacing_y
                
                element = ArrayElement(position=(float(x), float(y)))
                self.elements.append(element)
                element_count += 1
    
    def set_frequency(self, frequency: float):
        """Set operating frequency"""
        self.frequency = frequency
        self.wavelength = self._calculate_wavelength()
        self._initialize_elements()  # Recreate elements with new wavelength
    
    def apply_steering(self, steering_angle: float):
        """Apply phase shifts for beam steering"""
        steering_rad = np.radians(steering_angle)
        
        for element in self.elements:
            # Calculate phase shift for steering
            # For linear array along x-axis
            phase_shift = 2 * np.pi * element.position[0] * np.sin(steering_rad) / self.wavelength
            element.phase = phase_shift
    
    def apply_delays(self, delays: List[float]):
        """Apply custom delays to elements"""
        for i, element in enumerate(self.elements):
            if i < len(delays):
                element.delay = delays[i]
                # Convert delay to phase shift
                element.phase = 2 * np.pi * self.frequency * delays[i]
    
    def get_element_positions(self) -> np.ndarray:
        """Get all element positions as numpy array"""
        positions = np.zeros((len(self.elements), 2))
        for i, element in enumerate(self.elements):
            positions[i, 0] = element.position[0]
            positions[i, 1] = element.position[1]
        return positions
    
    def get_phases(self) -> np.ndarray:
        """Get all element phases as numpy array"""
        return np.array([element.phase for element in self.elements])
    
    def get_amplitudes(self) -> np.ndarray:
        """Get all element amplitudes as numpy array"""
        return np.array([element.amplitude for element in self.elements])
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return {
            'array_id': self.array_id,
            'array_type': self.array_type.value,
            'num_elements': self.num_elements,
            'spacing': self.spacing,
            'position': list(self.position),
            'orientation': self.orientation,
            'curvature': self.curvature,
            'frequency': self.frequency,
            'wavelength': self.wavelength,
            'elements': [element.to_dict() for element in self.elements]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PhasedArray':
        """Create PhasedArray from dictionary"""
        array = cls(
            array_id=data['array_id'],
            array_type=ArrayType(data['array_type']),
            num_elements=data['num_elements'],
            spacing=data['spacing'],
            position=tuple(data['position']),
            orientation=data['orientation'],
            curvature=data['curvature']
        )
        
        # Set frequency
        array.set_frequency(data.get('frequency', 2.4e9))
        
        # Update elements if provided
        if 'elements' in data:
            array.elements = []
            for elem_data in data['elements']:
                element = ArrayElement(
                    position=tuple(elem_data['position']),
                    amplitude=elem_data.get('amplitude', 1.0),
                    phase=elem_data.get('phase', 0.0),
                    delay=elem_data.get('delay', 0.0),
                    element_type=ElementType(elem_data.get('element_type', 'isotropic')),
                    orientation=elem_data.get('orientation', 0.0)
                )
                array.elements.append(element)
        
        return array