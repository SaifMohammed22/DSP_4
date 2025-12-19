import json
import os
import logging

logging.basicConfig(
    filename='beamforming.log',
    level=logging.DEBUG,  # Changed to DEBUG level to see debug messages
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
        logging.debug(f"ScenarioManager.__init__ called: scenarios_dir='{scenarios_dir}'")
        
        self.scenarios_dir = scenarios_dir
        os.makedirs(scenarios_dir, exist_ok=True)
        logging.debug(f"  Created/verified directory: {scenarios_dir}")
        
        self._create_default_scenarios()
        
        logging.info("ScenarioManager initialized")
        logging.debug(f"ScenarioManager.__init__ completed - instance ID: {id(self)}")
    
    def _create_default_scenarios(self):
        """Create default scenarios if they don't exist"""
        logging.debug(f"ScenarioManager._create_default_scenarios called")
        
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
        
        logging.debug(f"  Number of default scenarios: {len(default_scenarios)}")
        logging.debug(f"  Default scenario names: {list(default_scenarios.keys())}")
        
        created_count = 0
        for scenario_name, scenario_data in default_scenarios.items():
            filepath = os.path.join(self.scenarios_dir, 
                                   f"{scenario_name.lower().replace(' ', '_')}.json")
            logging.debug(f"  Checking scenario: {scenario_name}")
            logging.debug(f"    Target filepath: {filepath}")
            
            if not os.path.exists(filepath):
                logging.debug(f"    File doesn't exist, creating...")
                try:
                    with open(filepath, 'w') as f:
                        json.dump(scenario_data, f, indent=4)
                    created_count += 1
                    logging.info(f"Created default scenario: {scenario_name}")
                    logging.debug(f"    Successfully created file")
                except Exception as e:
                    logging.error(f"    Failed to create scenario file: {str(e)}")
            else:
                logging.debug(f"    File already exists, skipping creation")
        
        logging.debug(f"  Total scenarios created: {created_count}")
    
    def load_scenario(self, scenario_name):
        """
        Load scenario configuration from file
        
        Args:
            scenario_name: Name of scenario to load
            
        Returns:
            Dictionary with scenario configuration or None if not found
        """
        logging.debug(f"ScenarioManager.load_scenario called: scenario_name='{scenario_name}'")
        
        filename = f"{scenario_name.lower().replace(' ', '_')}.json"
        filepath = os.path.join(self.scenarios_dir, filename)
        logging.debug(f"  Constructed filename: {filename}")
        logging.debug(f"  Full filepath: {filepath}")
        
        try:
            logging.debug(f"  Attempting to open file...")
            with open(filepath, 'r') as f:
                scenario = json.load(f)
            
            logging.info(f"Loaded scenario: {scenario_name}")
            logging.debug(f"  Scenario data keys: {list(scenario.keys())}")
            logging.debug(f"  Scenario data values:")
            for key, value in scenario.items():
                if key in ['name', 'description', 'array_type', 'mode', 'application']:
                    logging.debug(f"    {key}: {value}")
                elif key in ['num_elements', 'frequency', 'propagation_speed']:
                    logging.debug(f"    {key}: {value} ({type(value).__name__})")
            
            return scenario
            
        except FileNotFoundError:
            logging.warning(f"Scenario not found: {scenario_name}")
            logging.debug(f"  FileNotFoundError: {filepath} does not exist")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding scenario JSON: {str(e)}")
            logging.debug(f"  JSONDecodeError details: line {e.lineno}, column {e.colno}, msg: {e.msg}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error loading scenario: {str(e)}")
            logging.debug(f"  Exception type: {type(e).__name__}")
            return None
    
    def save_scenario(self, scenario_data):
        """
        Save scenario configuration to file
        
        Args:
            scenario_data: Dictionary with scenario configuration
        """
        logging.debug(f"ScenarioManager.save_scenario called")
        logging.debug(f"  scenario_data keys: {list(scenario_data.keys())}")
        
        if 'name' not in scenario_data:
            error_msg = "Scenario must have a 'name' field"
            logging.error(f"  {error_msg}")
            raise ValueError(error_msg)
        
        scenario_name = scenario_data['name']
        filename = scenario_name.lower().replace(' ', '_') + '.json'
        filepath = os.path.join(self.scenarios_dir, filename)
        
        logging.debug(f"  Scenario name: {scenario_name}")
        logging.debug(f"  Generated filename: {filename}")
        logging.debug(f"  Full filepath: {filepath}")
        
        # Validate before saving
        is_valid, error_message = self.validate_scenario(scenario_data)
        if not is_valid:
            logging.error(f"  Scenario validation failed: {error_message}")
            raise ValueError(f"Invalid scenario: {error_message}")
        
        logging.debug(f"  Scenario validation passed")
        
        try:
            with open(filepath, 'w') as f:
                json.dump(scenario_data, f, indent=4)
            
            logging.info(f"Saved scenario: {scenario_name}")
            logging.debug(f"  Successfully wrote {len(json.dumps(scenario_data))} characters to file")
            
        except Exception as e:
            logging.error(f"  Failed to save scenario: {str(e)}")
            logging.debug(f"  Exception type: {type(e).__name__}")
            raise
    
    def get_all_scenarios(self):
        """
        Get list of all available scenarios
        
        Returns:
            List of scenario names
        """
        logging.debug(f"ScenarioManager.get_all_scenarios called")
        logging.debug(f"  Scanning directory: {self.scenarios_dir}")
        
        scenarios = []
        
        try:
            files = os.listdir(self.scenarios_dir)
            logging.debug(f"  Found {len(files)} files in directory")
            
            for filename in files:
                logging.debug(f"  Processing file: {filename}")
                if filename.endswith('.json'):
                    filepath = os.path.join(self.scenarios_dir, filename)
                    logging.debug(f"    JSON file detected: {filename}")
                    
                    try:
                        with open(filepath, 'r') as f:
                            scenario = json.load(f)
                        
                        scenario_info = {
                            'name': scenario.get('name', filename[:-5]),
                            'description': scenario.get('description', ''),
                            'application': scenario.get('application', '')
                        }
                        scenarios.append(scenario_info)
                        
                        logging.debug(f"    Successfully loaded scenario: {scenario_info['name']}")
                        
                    except json.JSONDecodeError as e:
                        logging.warning(f"    Failed to decode JSON in file {filename}: {str(e)}")
                        logging.debug(f"    JSONDecodeError details: {e.msg}")
                    except Exception as e:
                        logging.warning(f"    Error loading scenario from {filename}: {str(e)}")
                else:
                    logging.debug(f"    Skipping non-JSON file: {filename}")
            
            logging.debug(f"  Total scenarios loaded: {len(scenarios)}")
            
        except Exception as e:
            logging.error(f"Error loading scenarios: {str(e)}")
            logging.debug(f"  Exception type: {type(e).__name__}")
        
        logging.debug(f"  Returning {len(scenarios)} scenarios")
        return scenarios
    
    def delete_scenario(self, scenario_name):
        """
        Delete a scenario file
        
        Args:
            scenario_name: Name of scenario to delete
        """
        logging.debug(f"ScenarioManager.delete_scenario called: scenario_name='{scenario_name}'")
        
        filename = f"{scenario_name.lower().replace(' ', '_')}.json"
        filepath = os.path.join(self.scenarios_dir, filename)
        
        logging.debug(f"  Constructed filename: {filename}")
        logging.debug(f"  Full filepath: {filepath}")
        
        try:
            if not os.path.exists(filepath):
                logging.warning(f"Scenario file not found: {scenario_name}")
                logging.debug(f"  File does not exist at path: {filepath}")
                return False
            
            # Check if it's a default scenario
            is_default = False
            default_filenames = [
                '5g_beamforming.json',
                'ultrasound_imaging.json',
                'tumor_ablation.json',
                'receiver_mode_5g.json'
            ]
            if filename in default_filenames:
                is_default = True
                logging.debug(f"  Note: This is a default scenario file")
            
            os.remove(filepath)
            
            logging.info(f"Deleted scenario: {scenario_name}")
            logging.debug(f"  Successfully removed file: {filepath}")
            if is_default:
                logging.debug(f"  Default scenario deleted - it will be recreated if needed")
            
            return True
            
        except FileNotFoundError:
            logging.warning(f"Scenario file not found: {scenario_name}")
            logging.debug(f"  FileNotFoundError: {filepath} does not exist")
            return False
        except PermissionError as e:
            logging.error(f"Permission denied deleting scenario: {str(e)}")
            logging.debug(f"  PermissionError: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Error deleting scenario: {str(e)}")
            logging.debug(f"  Exception type: {type(e).__name__}")
            return False
    
    def validate_scenario(self, scenario_data):
        """
        Validate scenario configuration
        
        Args:
            scenario_data: Dictionary with scenario configuration
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        logging.debug(f"ScenarioManager.validate_scenario called")
        logging.debug(f"  scenario_data keys: {list(scenario_data.keys())}")
        
        required_fields = ['name', 'num_elements', 'frequency', 'array_type']
        logging.debug(f"  Required fields: {required_fields}")
        
        for field in required_fields:
            if field not in scenario_data:
                error_msg = f"Missing required field: {field}"
                logging.debug(f"  Validation failed: {error_msg}")
                return False, error_msg
        
        logging.debug(f"  All required fields present")
        
        # Validate numeric ranges
        num_elements = scenario_data['num_elements']
        logging.debug(f"  Validating num_elements: {num_elements}")
        if num_elements < 2 or num_elements > 256:
            error_msg = "num_elements must be between 2 and 256"
            logging.debug(f"  Validation failed: {error_msg}")
            return False, error_msg
        
        frequency = scenario_data['frequency']
        logging.debug(f"  Validating frequency: {frequency}")
        if frequency <= 0:
            error_msg = "frequency must be positive"
            logging.debug(f"  Validation failed: {error_msg}")
            return False, error_msg
        
        array_type = scenario_data['array_type']
        logging.debug(f"  Validating array_type: {array_type}")
        valid_array_types = ['Linear', 'Curved', 'linear', 'curved']
        if array_type not in valid_array_types:
            error_msg = "array_type must be 'Linear' or 'Curved'"
            logging.debug(f"  Validation failed: {error_msg}")
            return False, error_msg
        
        # Additional validation for curved arrays
        if array_type.lower() == 'curved':
            logging.debug(f"  Additional validation for curved array")
            if 'curvature_radius' in scenario_data:
                curvature_radius = scenario_data['curvature_radius']
                logging.debug(f"    curvature_radius: {curvature_radius}")
                if curvature_radius <= 0:
                    error_msg = "curvature_radius must be positive for curved arrays"
                    logging.debug(f"  Validation failed: {error_msg}")
                    return False, error_msg
        
        logging.debug(f"  All validations passed")
        return True, ""