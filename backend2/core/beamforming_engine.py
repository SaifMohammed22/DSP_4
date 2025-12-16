import numpy as np
from typing import List, Dict, Tuple, Optional
import json
import os
from enum import Enum

class ArrayType(Enum):
    LINEAR = "linear"
    CURVED = "curved"
    CIRCULAR = "circular"
    RECTANGULAR = "rectangular"

class BeamformingEngine:
    """
    Main engine for beamforming simulations.
    Handles array configurations, beam pattern calculations,
    and interference analysis.
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.arrays: List[Dict] = []
        self.sources: List[Dict] = []
        self.frequencies: List[float] = []
        self.beam_pattern = None
        self.interference_map = None
        self.results_cache = {}
        
        # Default parameters
        self.grid_size = 200
        self.grid_range = 10.0  # meters
        self.propagation_speed = 3e8  # Speed of light (m/s)
    
    def add_array(self, array_config: Dict) -> int:
        """
        Add a phased array to the simulation.
        
        Args:
            array_config: Dictionary containing array parameters
        
        Returns:
            Array ID
        """
        # Generate array ID if not provided
        if 'array_id' not in array_config:
            array_config['array_id'] = f"array_{len(self.arrays)}"
        
        # Set defaults
        defaults = {
            'type': 'linear',
            'num_elements': 8,
            'spacing': 0.5,  # in wavelengths
            'position': [0.0, 0.0],
            'orientation': 0.0,
            'curvature': 0.0,
            'delays': [],
            'amplitudes': [],
            'enabled': True
        }
        
        # Merge with defaults
        array = {**defaults, **array_config}
        
        # Calculate element positions
        array['element_positions'] = self._calculate_element_positions(array)
        
        # Store array
        self.arrays.append(array)
        return len(self.arrays) - 1
    
    def _calculate_element_positions(self, array: Dict) -> np.ndarray:
        """Calculate element positions based on array geometry"""
        array_type = array['type']
        num_elements = array['num_elements']
        spacing = array['spacing']
        position = np.array(array['position'])
        orientation = np.radians(array['orientation'])
        
        if array_type == 'linear':
            positions = self._create_linear_array(num_elements, spacing)
        elif array_type == 'curved':
            curvature = array['curvature']
            positions = self._create_curved_array(num_elements, spacing, curvature)
        elif array_type == 'circular':
            positions = self._create_circular_array(num_elements, spacing)
        elif array_type == 'rectangular':
            positions = self._create_rectangular_array(num_elements, spacing)
        else:
            positions = self._create_linear_array(num_elements, spacing)
        
        # Apply rotation
        if orientation != 0:
            rotation_matrix = np.array([
                [np.cos(orientation), -np.sin(orientation)],
                [np.sin(orientation), np.cos(orientation)]
            ])
            positions = positions @ rotation_matrix.T
        
        # Apply translation
        positions += position
        
        return positions
    
    def _create_linear_array(self, num_elements: int, spacing: float) -> np.ndarray:
        """Create linear array element positions"""
        positions = np.zeros((num_elements, 2))
        for i in range(num_elements):
            positions[i, 0] = (i - (num_elements - 1) / 2) * spacing
        return positions
    
    def _create_curved_array(self, num_elements: int, spacing: float, curvature: float) -> np.ndarray:
        """Create curved array element positions"""
        if curvature == 0:
            return self._create_linear_array(num_elements, spacing)
        
        radius = 1.0 / curvature
        arc_length = (num_elements - 1) * spacing
        angle = arc_length / radius
        
        angles = np.linspace(-angle/2, angle/2, num_elements)
        positions = np.zeros((num_elements, 2))
        
        for i, theta in enumerate(angles):
            positions[i, 0] = radius * np.sin(theta)
            positions[i, 1] = radius * (1 - np.cos(theta))
        
        return positions
    
    def _create_circular_array(self, num_elements: int, spacing: float) -> np.ndarray:
        """Create circular array element positions"""
        radius = spacing * num_elements / (2 * np.pi)
        angles = np.linspace(0, 2 * np.pi, num_elements, endpoint=False)
        
        positions = np.zeros((num_elements, 2))
        positions[:, 0] = radius * np.cos(angles)
        positions[:, 1] = radius * np.sin(angles)
        
        return positions
    
    def _create_rectangular_array(self, num_elements: int, spacing: float) -> np.ndarray:
        """Create rectangular array element positions"""
        # Determine grid dimensions
        rows = int(np.sqrt(num_elements))
        cols = int(np.ceil(num_elements / rows))
        
        positions = np.zeros((num_elements, 2))
        idx = 0
        
        for i in range(rows):
            for j in range(cols):
                if idx >= num_elements:
                    break
                positions[idx, 0] = (j - (cols - 1) / 2) * spacing
                positions[idx, 1] = (i - (rows - 1) / 2) * spacing
                idx += 1
        
        return positions[:num_elements]
    
    def add_source(self, source_config: Dict) -> int:
        """
        Add a signal source to the simulation.
        
        Args:
            source_config: Dictionary containing source parameters
        
        Returns:
            Source ID
        """
        # Generate source ID if not provided
        if 'source_id' not in source_config:
            source_config['source_id'] = f"source_{len(self.sources)}"
        
        # Set defaults
        defaults = {
            'type': 'transmitter',
            'position': [0.0, 0.0],
            'frequency': 2.4e9,
            'amplitude': 1.0,
            'phase': 0.0,
            'orientation': 0.0,
            'enabled': True
        }
        
        # Merge with defaults
        source = {**defaults, **source_config}
        self.sources.append(source)
        return len(self.sources) - 1
    
    def compute_beam_pattern(self, frequencies: List[float], 
                           steering_angle: float = 0.0,
                           grid_size: int = None,
                           grid_range: float = None) -> Dict:
        """
        Compute beam pattern for current arrays and sources.
        
        Args:
            frequencies: List of operating frequencies
            steering_angle: Beam steering angle in degrees
            grid_size: Resolution of computation grid
            grid_range: Physical range of grid in meters
        
        Returns:
            Dictionary containing beam pattern data
        """
        if grid_size is None:
            grid_size = self.grid_size
        if grid_range is None:
            grid_range = self.grid_range
        
        # Create computation grid
        x = np.linspace(-grid_range, grid_range, grid_size)
        y = np.linspace(-grid_range, grid_range, grid_size)
        X, Y = np.meshgrid(x, y)
        
        # Initialize field
        total_field = np.zeros_like(X, dtype=complex)
        
        # Process each array
        for array in self.arrays:
            if not array.get('enabled', True):
                continue
            
            array_field = self._compute_array_field(
                array, X, Y, frequencies, steering_angle
            )
            total_field += array_field
        
        # Compute magnitude and phase
        magnitude = np.abs(total_field)
        phase = np.angle(total_field)
        
        # Normalize magnitude
        if magnitude.max() > 0:
            magnitude = magnitude / magnitude.max()
        
        # Store results
        self.beam_pattern = {
            'magnitude': magnitude.tolist(),
            'phase': phase.tolist(),
            'X': X.tolist(),
            'Y': Y.tolist(),
            'steering_angle': steering_angle,
            'frequencies': frequencies,
            'grid_size': grid_size,
            'grid_range': grid_range
        }
        
        return self.beam_pattern
    
    def _compute_array_field(self, array: Dict, X: np.ndarray, Y: np.ndarray,
                           frequencies: List[float], steering_angle: float) -> np.ndarray:
        """Compute radiation field for a single array"""
        positions = array['element_positions']
        num_elements = array['num_elements']
        
        # Get element delays and amplitudes
        delays = array.get('delays', [])
        amplitudes = array.get('amplitudes', [])
        
        # Initialize field
        array_field = np.zeros_like(X, dtype=complex)
        
        # Process each frequency
        for freq in frequencies:
            wavelength = self.propagation_speed / freq
            
            # Calculate steering delays
            if len(delays) == 0:
                steering_delays = self._calculate_steering_delays(
                    array, steering_angle, wavelength
                )
            else:
                steering_delays = delays
            
            # Process each element
            for i in range(num_elements):
                if i >= len(positions):
                    continue
                
                # Element position
                elem_x, elem_y = positions[i]
                
                # Distance from element to grid points
                distances = np.sqrt((X - elem_x)**2 + (Y - elem_y)**2)
                
                # Phase contribution
                phase_contribution = 2 * np.pi * distances / wavelength
                
                # Apply delay
                delay = steering_delays[i] if i < len(steering_delays) else 0
                phase_delay = 2 * np.pi * freq * delay
                
                # Apply amplitude
                amplitude = amplitudes[i] if i < len(amplitudes) else 1.0
                
                # Add element contribution
                array_field += amplitude * np.exp(1j * (phase_contribution + phase_delay))
        
        return array_field
    
    def _calculate_steering_delays(self, array: Dict, 
                                 steering_angle: float, 
                                 wavelength: float) -> List[float]:
        """Calculate delays for beam steering"""
        positions = array['element_positions']
        steering_rad = np.radians(steering_angle)
        
        delays = []
        for pos in positions:
            # For linear steering along x-axis
            phase_shift = pos[0] * np.sin(steering_rad) / wavelength
            delays.append(phase_shift)
        
        # Normalize to remove negative delays
        min_delay = min(delays) if delays else 0
        delays = [d - min_delay for d in delays]
        
        return delays
    
    def compute_interference_map(self, sources: List[Dict] = None,
                               grid_size: int = None,
                               grid_range: float = None) -> Dict:
        """
        Compute interference map from sources.
        
        Args:
            sources: List of sources (uses self.sources if None)
            grid_size: Resolution of computation grid
            grid_range: Physical range of grid in meters
        
        Returns:
            Dictionary containing interference map data
        """
        if sources is None:
            sources = self.sources
        
        if grid_size is None:
            grid_size = self.grid_size
        if grid_range is None:
            grid_range = self.grid_range
        
        # Create computation grid
        x = np.linspace(-grid_range, grid_range, grid_size)
        y = np.linspace(-grid_range, grid_range, grid_size)
        X, Y = np.meshgrid(x, y)
        
        # Initialize total field
        total_field = np.zeros_like(X, dtype=complex)
        
        # Add contribution from each source
        for source in sources:
            if not source.get('enabled', True):
                continue
            
            source_field = self._compute_source_field(source, X, Y)
            total_field += source_field
        
        # Compute interference power
        interference_power = np.abs(total_field)**2
        
        # Store results
        self.interference_map = {
            'interference': interference_power.tolist(),
            'X': X.tolist(),
            'Y': Y.tolist(),
            'sources': sources,
            'grid_size': grid_size,
            'grid_range': grid_range
        }
        
        return self.interference_map
    
    def _compute_source_field(self, source: Dict, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        """Compute field from a single source"""
        pos_x, pos_y = source['position']
        freq = source['frequency']
        amplitude = source['amplitude']
        phase = source['phase']
        
        wavelength = self.propagation_speed / freq
        
        # Distance from source to grid points
        distances = np.sqrt((X - pos_x)**2 + (Y - pos_y)**2)
        
        # Spherical wave propagation
        field = amplitude * np.exp(1j * (2 * np.pi * distances / wavelength + phase))
        
        # Attenuation (inverse square law)
        field = field / (distances + 1e-10)  # Add small value to avoid division by zero
        
        return field
    
    def steer_beam(self, steering_angle: float) -> Dict:
        """
        Steer beam to new angle and recompute pattern.
        
        Args:
            steering_angle: New steering angle in degrees
        
        Returns:
            Updated beam pattern
        """
        if not self.frequencies:
            self.frequencies = [self.config.get('DEFAULT_FREQUENCY', 2.4e9)]
        
        return self.compute_beam_pattern(self.frequencies, steering_angle)
    
    def update_array_parameter(self, array_id: int, parameter: str, value) -> bool:
        """
        Update parameter of a specific array.
        
        Args:
            array_id: ID of array to update
            parameter: Parameter name to update
            value: New value
        
        Returns:
            Success status
        """
        if array_id >= len(self.arrays):
            return False
        
        if parameter in ['position', 'orientation', 'curvature', 'spacing', 'num_elements']:
            # These parameters require recalculating element positions
            self.arrays[array_id][parameter] = value
            self.arrays[array_id]['element_positions'] = self._calculate_element_positions(
                self.arrays[array_id]
            )
        elif parameter in ['delays', 'amplitudes', 'enabled']:
            # Simple parameter updates
            self.arrays[array_id][parameter] = value
        else:
            return False
        
        return True
    
    def load_scenario(self, scenario_name: str) -> Dict:
        """
        Load a predefined scenario.
        
        Args:
            scenario_name: Name of scenario to load
        
        Returns:
            Loaded scenario data
        """
        scenario_path = os.path.join('config/scenarios', f"{scenario_name}.json")
        
        if not os.path.exists(scenario_path):
            raise FileNotFoundError(f"Scenario '{scenario_name}' not found")
        
        with open(scenario_path, 'r') as f:
            scenario_data = json.load(f)
        
        # Clear current configuration
        self.arrays = []
        self.sources = []
        
        # Load arrays
        for array_config in scenario_data.get('arrays', []):
            self.add_array(array_config)
        
        # Load sources
        for source_config in scenario_data.get('sources', []):
            self.add_source(source_config)
        
        # Load frequencies
        self.frequencies = scenario_data.get('frequencies', [2.4e9])
        
        # Load other parameters
        self.grid_size = scenario_data.get('grid_size', self.grid_size)
        self.grid_range = scenario_data.get('grid_range', self.grid_range)
        
        return scenario_data
    
    def get_available_scenarios(self) -> List[str]:
        """Get list of available scenarios"""
        scenario_dir = 'config/scenarios'
        if not os.path.exists(scenario_dir):
            return []
        
        scenarios = []
        for file in os.listdir(scenario_dir):
            if file.endswith('.json'):
                scenarios.append(file.replace('.json', ''))
        
        return scenarios
    
    def save_scenario(self, name: str, description: str = "") -> str:
        """
        Save current configuration as a scenario.
        
        Args:
            name: Name for the scenario
            description: Optional description
        
        Returns:
            Path to saved scenario file
        """
        scenario_data = {
            'name': name,
            'description': description,
            'arrays': self.arrays,
            'sources': self.sources,
            'frequencies': self.frequencies,
            'grid_size': self.grid_size,
            'grid_range': self.grid_range,
            'timestamp': np.datetime64('now').astype(str)
        }
        
        # Ensure scenario directory exists
        os.makedirs('config/scenarios', exist_ok=True)
        
        # Save to file
        filename = name.lower().replace(' ', '_') + '.json'
        filepath = os.path.join('config/scenarios', filename)
        
        with open(filepath, 'w') as f:
            json.dump(scenario_data, f, indent=2)
        
        return filepath
    
    def get_simulation_summary(self) -> Dict:
        """Get summary of current simulation setup"""
        return {
            'num_arrays': len(self.arrays),
            'num_sources': len(self.sources),
            'frequencies': self.frequencies,
            'grid_size': self.grid_size,
            'grid_range': self.grid_range,
            'has_beam_pattern': self.beam_pattern is not None,
            'has_interference_map': self.interference_map is not None
        }
    
    def clear_simulation(self):
        """Clear all simulation data"""
        self.arrays = []
        self.sources = []
        self.frequencies = []
        self.beam_pattern = None
        self.interference_map = None
        self.results_cache = {}