import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid

class ScenarioType(Enum):
    FIVE_G = "5g"
    ULTRASOUND = "ultrasound"
    TUMOR_ABLATION = "tumor_ablation"
    RADAR = "radar"
    SONAR = "sonar"
    CUSTOM = "custom"

@dataclass
class Source:
    """Source in a beamforming scenario"""
    source_id: str
    type: str  # 'transmitter', 'receiver', 'target', 'interference'
    position: List[float]  # [x, y]
    frequency: float  # Hz
    amplitude: float = 1.0
    phase: float = 0.0
    orientation: float = 0.0  # degrees
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'source_id': self.source_id,
            'type': self.type,
            'position': self.position,
            'frequency': self.frequency,
            'amplitude': self.amplitude,
            'phase': self.phase,
            'orientation': self.orientation,
            'parameters': self.parameters
        }

@dataclass
class ScenarioParameters:
    """Parameters for a beamforming scenario"""
    # General parameters
    frequency: float = 2.4e9
    bandwidth: float = 100e6
    sampling_rate: float = 10e9
    
    # Array parameters
    array_type: str = "linear"
    num_elements: int = 8
    element_spacing: float = 0.5  # in wavelengths
    
    # Beamforming parameters
    steering_angle: float = 0.0  # degrees
    beam_width: float = 10.0  # degrees
    
    # Environment parameters
    propagation_speed: float = 3e8  # m/s (speed of light)
    noise_level: float = 0.1
    multipath_enabled: bool = False
    
    # Visualization parameters
    grid_size: int = 200
    grid_range: float = 10.0  # meters
    
    # Custom parameters
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'frequency': self.frequency,
            'bandwidth': self.bandwidth,
            'sampling_rate': self.sampling_rate,
            'array_type': self.array_type,
            'num_elements': self.num_elements,
            'element_spacing': self.element_spacing,
            'steering_angle': self.steering_angle,
            'beam_width': self.beam_width,
            'propagation_speed': self.propagation_speed,
            'noise_level': self.noise_level,
            'multipath_enabled': self.multipath_enabled,
            'grid_size': self.grid_size,
            'grid_range': self.grid_range,
            'custom_params': self.custom_params
        }

class Scenario:
    """Beamforming scenario model"""
    
    def __init__(self, scenario_id: str = None, name: str = "New Scenario", 
                 scenario_type: ScenarioType = ScenarioType.CUSTOM):
        self.scenario_id = scenario_id or str(uuid.uuid4())
        self.name = name
        self.scenario_type = scenario_type
        self.description: str = ""
        self.parameters = ScenarioParameters()
        self.sources: List[Source] = []
        self.arrays: List[Dict] = []  # Array configurations
        self.metadata: Dict[str, Any] = {
            'created_at': None,
            'modified_at': None,
            'version': '1.0',
            'author': 'System'
        }
        
        # Initialize with default values based on type
        self._initialize_by_type()
    
    def _initialize_by_type(self):
        """Initialize scenario based on type"""
        if self.scenario_type == ScenarioType.FIVE_G:
            self._init_5g_scenario()
        elif self.scenario_type == ScenarioType.ULTRASOUND:
            self._init_ultrasound_scenario()
        elif self.scenario_type == ScenarioType.TUMOR_ABLATION:
            self._init_tumor_ablation_scenario()
        elif self.scenario_type == ScenarioType.RADAR:
            self._init_radar_scenario()
        elif self.scenario_type == ScenarioType.SONAR:
            self._init_sonar_scenario()
    
    def _init_5g_scenario(self):
        """Initialize 5G scenario"""
        self.name = "5G Base Station Scenario"
        self.description = "5G base station with beamforming for mobile communication"
        
        # Set parameters
        self.parameters.frequency = 3.5e9  # 3.5 GHz
        self.parameters.bandwidth = 100e6  # 100 MHz
        self.parameters.num_elements = 32
        self.parameters.array_type = "linear"
        self.parameters.element_spacing = 0.5
        self.parameters.steering_angle = 30.0
        self.parameters.beam_width = 5.0
        
        # Add sources
        transmitter = Source(
            source_id="tx_1",
            type="transmitter",
            position=[10.0, 5.0],
            frequency=3.5e9,
            amplitude=1.0
        )
        
        receiver = Source(
            source_id="rx_1",
            type="receiver",
            position=[-5.0, 3.0],
            frequency=3.5e9,
            amplitude=0.8
        )
        
        interference = Source(
            source_id="int_1",
            type="interference",
            position=[8.0, -3.0],
            frequency=3.5e9,
            amplitude=0.3
        )
        
        self.sources = [transmitter, receiver, interference]
        
        # Add arrays
        self.arrays = [
            {
                'array_id': 'array_1',
                'type': 'linear',
                'num_elements': 32,
                'spacing': 0.5,
                'position': [0.0, 0.0],
                'orientation': 0.0
            }
        ]
        
        # Update metadata
        self.metadata['application'] = '5G Communications'
        self.metadata['frequency_band'] = 'Sub-6 GHz'
    
    def _init_ultrasound_scenario(self):
        """Initialize ultrasound scenario"""
        self.name = "Medical Ultrasound Imaging"
        self.description = "Curved array ultrasound for medical imaging"
        
        # Set parameters
        self.parameters.frequency = 5e6  # 5 MHz
        self.parameters.propagation_speed = 1540  # Speed of sound in tissue (m/s)
        self.parameters.num_elements = 64
        self.parameters.array_type = "curved"
        self.parameters.element_spacing = 0.5
        self.parameters.grid_range = 0.1  # 10 cm
        
        # Add sources
        target = Source(
            source_id="target_1",
            type="target",
            position=[0.02, 0.05],  # 2cm right, 5cm deep
            frequency=5e6,
            amplitude=0.7
        )
        
        self.sources = [target]
        
        # Add arrays
        self.arrays = [
            {
                'array_id': 'array_1',
                'type': 'curved',
                'num_elements': 64,
                'spacing': 0.5,
                'position': [0.0, 0.0],
                'orientation': 0.0,
                'curvature': 0.2
            }
        ]
        
        # Update metadata
        self.metadata['application'] = 'Medical Imaging'
        self.metadata['imaging_depth'] = '10 cm'
    
    def _init_tumor_ablation_scenario(self):
        """Initialize tumor ablation scenario"""
        self.name = "Focused Ultrasound Tumor Ablation"
        self.description = "High-intensity focused ultrasound for tumor ablation therapy"
        
        # Set parameters
        self.parameters.frequency = 1e6  # 1 MHz
        self.parameters.propagation_speed = 1540  # Speed of sound in tissue
        self.parameters.num_elements = 256
        self.parameters.array_type = "circular"
        self.parameters.element_spacing = 0.5
        self.parameters.grid_range = 0.15  # 15 cm
        
        # Add sources
        focus_point = Source(
            source_id="focus",
            type="target",
            position=[0.0, 0.08],  # 8 cm deep
            frequency=1e6,
            amplitude=0.0  # Target doesn't emit
        )
        
        self.sources = [focus_point]
        
        # Add arrays
        self.arrays = [
            {
                'array_id': 'array_1',
                'type': 'circular',
                'num_elements': 256,
                'spacing': 0.5,
                'position': [0.0, 0.0],
                'orientation': 0.0,
                'radius': 0.05  # 5 cm radius
            }
        ]
        
        # Update metadata
        self.metadata['application'] = 'Medical Therapy'
        self.metadata['therapy_type'] = 'Tumor Ablation'
        self.metadata['focus_depth'] = '8 cm'
    
    def _init_radar_scenario(self):
        """Initialize radar scenario"""
        self.name = "Phased Array Radar"
        self.description = "Phased array radar for target detection and tracking"
        
        # Set parameters
        self.parameters.frequency = 10e9  # 10 GHz (X-band)
        self.parameters.bandwidth = 1e9  # 1 GHz
        self.parameters.num_elements = 16
        self.parameters.array_type = "linear"
        self.parameters.element_spacing = 0.5
        self.parameters.steering_angle = 45.0
        
        # Add sources
        target = Source(
            source_id="target_1",
            type="target",
            position=[50.0, 30.0],  # 50m right, 30m up
            frequency=10e9,
            amplitude=0.5
        )
        
        self.sources = [target]
        
        # Add arrays
        self.arrays = [
            {
                'array_id': 'array_1',
                'type': 'linear',
                'num_elements': 16,
                'spacing': 0.5,
                'position': [0.0, 0.0],
                'orientation': 0.0
            }
        ]
        
        # Update metadata
        self.metadata['application'] = 'Radar'
        self.metadata['frequency_band'] = 'X-band'
        self.metadata['range'] = '100 m'
    
    def _init_sonar_scenario(self):
        """Initialize sonar scenario"""
        self.name = "Underwater Sonar Array"
        self.description = "Underwater sonar array for object detection and imaging"
        
        # Set parameters
        self.parameters.frequency = 50e3  # 50 kHz
        self.parameters.propagation_speed = 1500  # Speed of sound in water
        self.parameters.num_elements = 32
        self.parameters.array_type = "linear"
        self.parameters.element_spacing = 0.5
        self.parameters.grid_range = 50.0  # 50 meters
        
        # Add sources
        target = Source(
            source_id="target_1",
            type="target",
            position=[20.0, 10.0],  # 20m right, 10m deep
            frequency=50e3,
            amplitude=0.6
        )
        
        self.sources = [target]
        
        # Add arrays
        self.arrays = [
            {
                'array_id': 'array_1',
                'type': 'linear',
                'num_elements': 32,
                'spacing': 0.5,
                'position': [0.0, 0.0],
                'orientation': 0.0
            }
        ]
        
        # Update metadata
        self.metadata['application'] = 'Sonar'
        self.metadata['environment'] = 'Underwater'
        self.metadata['range'] = '50 m'
    
    def add_source(self, source: Source):
        """Add a source to the scenario"""
        self.sources.append(source)
    
    def remove_source(self, source_id: str) -> bool:
        """Remove a source by ID"""
        for i, source in enumerate(self.sources):
            if source.source_id == source_id:
                self.sources.pop(i)
                return True
        return False
    
    def add_array(self, array_config: Dict):
        """Add an array to the scenario"""
        self.arrays.append(array_config)
    
    def update_parameters(self, **kwargs):
        """Update scenario parameters"""
        for key, value in kwargs.items():
            if hasattr(self.parameters, key):
                setattr(self.parameters, key, value)
            else:
                self.parameters.custom_params[key] = value
    
    def to_dict(self) -> Dict:
        """Convert scenario to dictionary"""
        return {
            'scenario_id': self.scenario_id,
            'name': self.name,
            'scenario_type': self.scenario_type.value,
            'description': self.description,
            'parameters': self.parameters.to_dict(),
            'sources': [source.to_dict() for source in self.sources],
            'arrays': self.arrays,
            'metadata': self.metadata
        }
    
    def save_to_file(self, filepath: str):
        """Save scenario to JSON file"""
        scenario_dict = self.to_dict()
        
        with open(filepath, 'w') as f:
            json.dump(scenario_dict, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'Scenario':
        """Load scenario from JSON file"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Scenario file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            scenario_dict = json.load(f)
        
        return cls.from_dict(scenario_dict)
    
    @classmethod
    def from_dict(cls, scenario_dict: Dict) -> 'Scenario':
        """Create scenario from dictionary"""
        scenario = cls(
            scenario_id=scenario_dict.get('scenario_id'),
            name=scenario_dict.get('name', 'Unnamed Scenario'),
            scenario_type=ScenarioType(scenario_dict.get('scenario_type', 'custom'))
        )
        
        scenario.description = scenario_dict.get('description', '')
        
        # Load parameters
        params_dict = scenario_dict.get('parameters', {})
        for key, value in params_dict.items():
            if hasattr(scenario.parameters, key):
                setattr(scenario.parameters, key, value)
            elif key == 'custom_params' and isinstance(value, dict):
                scenario.parameters.custom_params.update(value)
        
        # Load sources
        sources_list = scenario_dict.get('sources', [])
        for source_dict in sources_list:
            source = Source(
                source_id=source_dict.get('source_id', str(uuid.uuid4())),
                type=source_dict.get('type', 'target'),
                position=source_dict.get('position', [0.0, 0.0]),
                frequency=source_dict.get('frequency', 1e6),
                amplitude=source_dict.get('amplitude', 1.0),
                phase=source_dict.get('phase', 0.0),
                orientation=source_dict.get('orientation', 0.0),
                parameters=source_dict.get('parameters', {})
            )
            scenario.sources.append(source)
        
        # Load arrays
        scenario.arrays = scenario_dict.get('arrays', [])
        
        # Load metadata
        scenario.metadata = scenario_dict.get('metadata', {})
        
        return scenario
    
    def get_source_by_id(self, source_id: str) -> Optional[Source]:
        """Get source by ID"""
        for source in self.sources:
            if source.source_id == source_id:
                return source
        return None
    
    def get_array_by_id(self, array_id: str) -> Optional[Dict]:
        """Get array by ID"""
        for array in self.arrays:
            if array.get('array_id') == array_id:
                return array
        return None
    
    def clone(self, new_name: str = None) -> 'Scenario':
        """Create a clone of this scenario"""
        clone_dict = self.to_dict()
        clone_dict['scenario_id'] = str(uuid.uuid4())
        
        if new_name:
            clone_dict['name'] = new_name
        else:
            clone_dict['name'] = f"{self.name} (Copy)"
        
        return self.from_dict(clone_dict)