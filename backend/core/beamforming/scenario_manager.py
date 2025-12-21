import json
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ScenarioManager:
    """
    Manages predefined and custom beamforming scenarios.
    Handles loading, saving, and validation of scenario configurations.
    """
    
    def __init__(self, scenarios_dir='scenarios'):
        """
        Initialize scenario manager
        
        Args:
            scenarios_dir: Directory to store scenario JSON files
        """
        self.scenarios_dir = scenarios_dir
        os.makedirs(scenarios_dir, exist_ok=True)
        
        self._create_default_scenarios()
    
    def _create_default_scenarios(self):
        """Create default scenarios if they don't exist"""
        default_scenarios = {
            '5G Beamforming': {
                'name': '5G Beamforming',
                'description': '5G millimeter wave beamforming for wireless communications',
                'num_elements': 64,
                'frequency': 28e9,  # 28 GHz
                'array_type': 'Linear',
                'beam_angle': 0,
                'element_spacing': 0.5,
                'propagation_speed': 3e8,
                'mode': 'transmitter',
                'grid_range': 3,
                'application': '5G wireless communications, high-frequency directional transmission'
            },
            'Ultrasound Imaging': {
                'name': 'Ultrasound Imaging',
                'description': 'Medical ultrasound imaging with curved transducer array',
                'num_elements': 128,
                'frequency': 5e6,  # 5 MHz
                'array_type': 'Curved',
                'beam_angle': 0,
                'element_spacing': 0.5,
                'propagation_speed': 1500,  # Speed of sound in tissue
                'mode': 'transmitter',
                'grid_range': 1.5,
                'application': 'Medical imaging, non-invasive tissue visualization'
            },
            'Tumor Ablation': {
                'name': 'Tumor Ablation',
                'description': 'Focused ultrasound for tumor ablation therapy',
                'num_elements': 32,
                'frequency': 1e6,  # 1 MHz
                'array_type': 'Curved',
                'beam_angle': 0,
                'element_spacing': 0.5,
                'propagation_speed': 1500,  # Speed of sound in tissue
                'mode': 'transmitter',
                'curvature_radius': 4.0,
                'grid_range': 5,
                'application': 'Therapeutic ultrasound, non-invasive tumor treatment'
            },
            'Receiver Mode 5G': {
                'name': 'Receiver Mode 5G',
                'description': '5G receiver array for direction of arrival estimation',
                'num_elements': 16,
                'frequency': 10e9,  # 10 GHz
                'array_type': 'Linear',
                'beam_angle': 0,
                'element_spacing': 0.5,
                'propagation_speed': 3e8,
                'mode': 'receiver',
                'grid_range': 7,
                'application': '5G signal reception, direction of arrival estimation'
            }
        }
        
        for scenario_name, scenario_data in default_scenarios.items():
            filepath = os.path.join(self.scenarios_dir, 
                                   f"{scenario_name.lower().replace(' ', '_')}.json")
            
            if not os.path.exists(filepath):
                try:
                    with open(filepath, 'w') as f:
                        json.dump(scenario_data, f, indent=4)
                except Exception as e:
                    logging.error(f"Failed to create scenario file: {str(e)}")
    
    def load_scenario(self, scenario_name):
        """
        Load scenario configuration from file
        
        Args:
            scenario_name: Name of scenario to load
            
        Returns:
            Dictionary with scenario configuration or None if not found
        """
        filename = f"{scenario_name.lower().replace(' ', '_')}.json"
        filepath = os.path.join(self.scenarios_dir, filename)
        
        try:
            with open(filepath, 'r') as f:
                scenario = json.load(f)
            return scenario
            
        except FileNotFoundError:
            logging.warning(f"Scenario not found: {scenario_name}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding scenario JSON: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error loading scenario: {str(e)}")
            return None
    
    def save_scenario(self, scenario_data):
        """
        Save scenario configuration to file
        
        Args:
            scenario_data: Dictionary with scenario configuration
        """
        if 'name' not in scenario_data:
            raise ValueError("Scenario must have a 'name' field")
        
        scenario_name = scenario_data['name']
        filename = scenario_name.lower().replace(' ', '_') + '.json'
        filepath = os.path.join(self.scenarios_dir, filename)
        
        # Validate before saving
        is_valid, error_message = self.validate_scenario(scenario_data)
        if not is_valid:
            raise ValueError(f"Invalid scenario: {error_message}")
        
        try:
            with open(filepath, 'w') as f:
                json.dump(scenario_data, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save scenario: {str(e)}")
            raise
    
    def get_all_scenarios(self):
        """
        Get list of all available scenarios
        
        Returns:
            List of scenario dictionaries with id, name, description
        """
        scenarios = []
        
        try:
            files = os.listdir(self.scenarios_dir)
            
            for filename in files:
                if filename.endswith('.json'):
                    filepath = os.path.join(self.scenarios_dir, filename)
                    
                    try:
                        with open(filepath, 'r') as f:
                            scenario = json.load(f)
                        
                        # Get ID from scenario or derive from filename
                        scenario_id = scenario.get('id', filename[:-5])
                        
                        scenario_info = {
                            'id': scenario_id,
                            'name': scenario.get('name', filename[:-5]),
                            'description': scenario.get('description', scenario.get('application', '')),
                        }
                        scenarios.append(scenario_info)
                        
                    except json.JSONDecodeError as e:
                        logging.warning(f"Failed to decode JSON in file {filename}: {str(e)}")
                    except Exception as e:
                        logging.warning(f"Error loading scenario from {filename}: {str(e)}")
            
        except Exception as e:
            logging.error(f"Error loading scenarios: {str(e)}")
        
        return scenarios
    
    def delete_scenario(self, scenario_name):
        """
        Delete a scenario file
        
        Args:
            scenario_name: Name of scenario to delete
        """
        filename = f"{scenario_name.lower().replace(' ', '_')}.json"
        filepath = os.path.join(self.scenarios_dir, filename)
        
        try:
            if not os.path.exists(filepath):
                return False
            
            os.remove(filepath)
            return True
            
        except FileNotFoundError:
            return False
        except PermissionError as e:
            logging.error(f"Permission denied deleting scenario: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Error deleting scenario: {str(e)}")
            return False
    
    def validate_scenario(self, scenario_data):
        """
        Validate scenario configuration
        
        Args:
            scenario_data: Dictionary with scenario configuration
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ['name', 'num_elements', 'frequency', 'array_type']
        
        for field in required_fields:
            if field not in scenario_data:
                return False, f"Missing required field: {field}"
        
        # Validate numeric ranges
        num_elements = scenario_data['num_elements']
        if num_elements < 2 or num_elements > 256:
            return False, "num_elements must be between 2 and 256"
        
        frequency = scenario_data['frequency']
        if frequency <= 0:
            return False, "frequency must be positive"
        
        array_type = scenario_data['array_type']
        valid_array_types = ['Linear', 'Curved', 'linear', 'curved']
        if array_type not in valid_array_types:
            return False, "array_type must be 'Linear' or 'Curved'"
        
        # Additional validation for curved arrays
        if array_type.lower() == 'curved':
            if 'curvature_radius' in scenario_data:
                curvature_radius = scenario_data['curvature_radius']
                if curvature_radius <= 0:
                    return False, "curvature_radius must be positive for curved arrays"
        
        return True, ""
