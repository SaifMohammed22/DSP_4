"""
Scenario Manager
Provides preset scenarios for different beamforming applications.
"""
import json
import os
from typing import Dict, List, Optional
from .phased_array import PhasedArray
from .beamformer import Beamformer


# Preset scenarios
SCENARIOS = {
    '5g_mimo': {
        'name': '5G MIMO Base Station',
        'description': 'Massive MIMO antenna array for 5G wireless communication',
        'parameters': {
            'frequencies': [3500e6],  # 3.5 GHz (5G mid-band)
            'speed': 3e8,  # Speed of light
            'field_size': (2.0, 2.0),  # 2m x 2m field (scaled for display)
            'resolution': 200
        },
        'arrays': [
            {
                'array_id': '5g_main',
                'num_elements': 16,
                'element_spacing': 0.5,  # Half wavelength
                'geometry': 'linear',
                'position': (0.0, 0.0),
                'orientation': 0.0,
                'steering_angle': 0.0
            }
        ],
        'display_settings': {
            'scale_factor': 1000,  # Convert to mm for display
            'unit': 'mm',
            'title': '5G MIMO Beam Pattern'
        }
    },
    
    'ultrasound_imaging': {
        'name': 'Ultrasound Medical Imaging',
        'description': 'Curved array ultrasound transducer for medical imaging',
        'parameters': {
            'frequencies': [5e6],  # 5 MHz
            'speed': 1540.0,  # Speed of sound in tissue (m/s)
            'field_size': (0.1, 0.15),  # 10cm x 15cm field
            'resolution': 200
        },
        'arrays': [
            {
                'array_id': 'ultrasound_probe',
                'num_elements': 64,
                'element_spacing': 0.3,  # ~0.3 wavelength
                'geometry': 'curved',
                'curvature_radius': 40.0,  # 40 wavelengths
                'position': (0.0, 0.0),
                'orientation': 0.0,
                'focus_point': (0.0, 0.08)  # Focus at 8cm depth
            }
        ],
        'display_settings': {
            'scale_factor': 1000,  # Convert to mm
            'unit': 'mm',
            'title': 'Ultrasound Beam Pattern'
        }
    },
    
    'tumor_ablation': {
        'name': 'Tumor Ablation HIFU',
        'description': 'High-Intensity Focused Ultrasound for tumor ablation therapy',
        'parameters': {
            'frequencies': [1e6, 1.5e6],  # 1 MHz and 1.5 MHz
            'speed': 1540.0,  # Speed of sound in tissue
            'field_size': (0.08, 0.12),  # 8cm x 12cm field
            'resolution': 200
        },
        'arrays': [
            {
                'array_id': 'hifu_main',
                'num_elements': 128,
                'element_spacing': 0.4,
                'geometry': 'curved',
                'curvature_radius': 60.0,  # Larger curvature for focusing
                'position': (0.0, 0.0),
                'orientation': 0.0,
                'focus_point': (0.0, 0.06)  # Focus at 6cm depth
            },
            {
                'array_id': 'hifu_secondary',
                'num_elements': 64,
                'element_spacing': 0.4,
                'geometry': 'curved',
                'curvature_radius': 50.0,
                'position': (-0.02, 0.0),  # Offset to the left
                'orientation': 15.0,  # Angled inward
                'focus_point': (0.0, 0.06)
            }
        ],
        'display_settings': {
            'scale_factor': 1000,
            'unit': 'mm',
            'title': 'HIFU Ablation Pattern'
        }
    }
}


class ScenarioManager:
    """
    Manages beamforming scenarios - loading, saving, and applying presets.
    """
    
    def __init__(self, custom_scenarios_dir: Optional[str] = None):
        """
        Initialize the scenario manager.
        
        Args:
            custom_scenarios_dir: Directory for custom user scenarios
        """
        self.custom_scenarios_dir = custom_scenarios_dir
        self._custom_scenarios: Dict[str, dict] = {}
        
        if custom_scenarios_dir and os.path.exists(custom_scenarios_dir):
            self._load_custom_scenarios()
    
    def _load_custom_scenarios(self):
        """Load custom scenarios from disk."""
        if not self.custom_scenarios_dir:
            return
        
        for filename in os.listdir(self.custom_scenarios_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.custom_scenarios_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        scenario = json.load(f)
                        scenario_id = filename[:-5]  # Remove .json
                        self._custom_scenarios[scenario_id] = scenario
                except Exception as e:
                    print(f"Error loading scenario {filename}: {e}")
    
    def get_available_scenarios(self) -> List[dict]:
        """Get list of all available scenarios."""
        scenarios = []
        
        # Built-in scenarios
        for scenario_id, scenario in SCENARIOS.items():
            scenarios.append({
                'id': scenario_id,
                'name': scenario['name'],
                'description': scenario['description'],
                'type': 'builtin'
            })
        
        # Custom scenarios
        for scenario_id, scenario in self._custom_scenarios.items():
            scenarios.append({
                'id': scenario_id,
                'name': scenario.get('name', scenario_id),
                'description': scenario.get('description', ''),
                'type': 'custom'
            })
        
        return scenarios
    
    def get_scenario(self, scenario_id: str) -> Optional[dict]:
        """Get a scenario by ID."""
        if scenario_id in SCENARIOS:
            return SCENARIOS[scenario_id]
        return self._custom_scenarios.get(scenario_id)
    
    def apply_scenario(self, beamformer: Beamformer, scenario_id: str) -> bool:
        """
        Apply a scenario to a beamformer.
        
        Args:
            beamformer: Beamformer instance to configure
            scenario_id: ID of scenario to apply
            
        Returns:
            True if successful, False otherwise
        """
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return False
        
        params = scenario['parameters']
        
        # Configure beamformer
        beamformer.set_frequencies(params['frequencies'])
        beamformer.set_speed(params['speed'])
        beamformer.update_field_parameters(
            field_size=tuple(params['field_size']),
            resolution=params['resolution']
        )
        
        # Clear existing arrays and add new ones
        beamformer.clear_arrays()
        
        for array_config in scenario['arrays']:
            array = PhasedArray(
                num_elements=array_config['num_elements'],
                element_spacing=array_config['element_spacing'],
                geometry=array_config['geometry'],
                curvature_radius=array_config.get('curvature_radius', 10.0),
                position=tuple(array_config['position']),
                orientation=array_config.get('orientation', 0.0),
                array_id=array_config['array_id']
            )
            
            # Apply steering or focusing
            if 'steering_angle' in array_config:
                array.set_steering_angle(
                    array_config['steering_angle'],
                    params['frequencies'][0],
                    params['speed']
                )
            elif 'focus_point' in array_config:
                fx, fy = array_config['focus_point']
                array.set_focus_point(fx, fy, params['frequencies'][0], params['speed'])
            
            beamformer.add_array(array)
        
        return True
    
    def save_scenario(
        self,
        scenario_id: str,
        name: str,
        description: str,
        beamformer: Beamformer
    ) -> bool:
        """
        Save current beamformer state as a custom scenario.
        
        Args:
            scenario_id: ID for the scenario
            name: Display name
            description: Description text
            beamformer: Beamformer instance to save
            
        Returns:
            True if successful
        """
        if not self.custom_scenarios_dir:
            return False
        
        scenario = {
            'name': name,
            'description': description,
            'parameters': {
                'frequencies': beamformer.frequencies,
                'speed': beamformer.speed,
                'field_size': beamformer.field_size,
                'resolution': beamformer.resolution
            },
            'arrays': [array.to_dict() for array in beamformer.arrays],
            'display_settings': {
                'scale_factor': 1000,
                'unit': 'mm',
                'title': name
            }
        }
        
        # Save to file
        os.makedirs(self.custom_scenarios_dir, exist_ok=True)
        filepath = os.path.join(self.custom_scenarios_dir, f"{scenario_id}.json")
        
        try:
            with open(filepath, 'w') as f:
                json.dump(scenario, f, indent=2)
            self._custom_scenarios[scenario_id] = scenario
            return True
        except Exception as e:
            print(f"Error saving scenario: {e}")
            return False
    
    def delete_custom_scenario(self, scenario_id: str) -> bool:
        """Delete a custom scenario."""
        if scenario_id not in self._custom_scenarios:
            return False
        
        if self.custom_scenarios_dir:
            filepath = os.path.join(self.custom_scenarios_dir, f"{scenario_id}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
        
        del self._custom_scenarios[scenario_id]
        return True
    
    def get_scenario_display_settings(self, scenario_id: str) -> dict:
        """Get display settings for a scenario."""
        scenario = self.get_scenario(scenario_id)
        if scenario and 'display_settings' in scenario:
            return scenario['display_settings']
        return {
            'scale_factor': 1,
            'unit': 'm',
            'title': 'Beam Pattern'
        }
