import unittest
import numpy as np
import json
import tempfile
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.beamforming_engine import BeamformingEngine
from models.scenario_model import Scenario, ScenarioType, Source
from models.array_model import PhasedArray, ArrayType
from utils.signal_utils import generate_sine_wave, compute_power_spectrum

class TestBeamforming(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.beamforming_engine = BeamformingEngine()
        
        # Create test scenario
        self.test_scenario = self._create_test_scenario()
        
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def _create_test_scenario(self) -> Scenario:
        """Create a test scenario"""
        scenario = Scenario(
            scenario_id="test_scenario",
            name="Test Scenario",
            scenario_type=ScenarioType.CUSTOM
        )
        
        # Add parameters
        scenario.parameters.frequency = 2.4e9
        scenario.parameters.num_elements = 8
        scenario.parameters.array_type = "linear"
        
        # Add a source
        source = Source(
            source_id="test_source",
            type="transmitter",
            position=[5.0, 3.0],
            frequency=2.4e9,
            amplitude=1.0
        )
        scenario.add_source(source)
        
        # Add an array
        scenario.add_array({
            'array_id': 'test_array',
            'type': 'linear',
            'num_elements': 8,
            'spacing': 0.5,
            'position': [0.0, 0.0],
            'orientation': 0.0
        })
        
        return scenario
    
    def test_beamforming_engine_initialization(self):
        """Test beamforming engine initialization"""
        self.assertIsNotNone(self.beamforming_engine)
        self.assertEqual(len(self.beamforming_engine.arrays), 0)
        self.assertEqual(len(self.beamforming_engine.frequencies), 0)
    
    def test_add_array(self):
        """Test adding array to engine"""
        array_config = {
            'type': 'linear',
            'num_elements': 8,
            'spacing': 0.5,
            'position': [0.0, 0.0],
            'orientation': 0.0
        }
        
        array_id = self.beamforming_engine.add_array(array_config)
        self.assertEqual(array_id, 0)  # First array should have ID 0
        self.assertEqual(len(self.beamforming_engine.arrays), 1)
        
        # Check array properties
        array = self.beamforming_engine.arrays[array_id]
        self.assertEqual(array['type'], 'linear')
        self.assertEqual(array['num_elements'], 8)
        self.assertEqual(array['spacing'], 0.5)
    
    def test_compute_beam_pattern(self):
        """Test beam pattern computation"""
        # Add an array
        array_config = {
            'type': 'linear',
            'num_elements': 8,
            'spacing': 0.5,
            'position': [0.0, 0.0],
            'orientation': 0.0
        }
        self.beamforming_engine.add_array(array_config)
        
        # Set frequency
        frequencies = [2.4e9]
        steering_angle = 30.0
        
        # Compute beam pattern
        beam_pattern = self.beamforming_engine.compute_beam_pattern(frequencies, steering_angle)
        
        # Check beam pattern structure
        self.assertIsNotNone(beam_pattern)
        self.assertIn('magnitude', beam_pattern)
        self.assertIn('phase', beam_pattern)
        self.assertIn('X', beam_pattern)
        self.assertIn('Y', beam_pattern)
        self.assertEqual(beam_pattern['steering_angle'], steering_angle)
        
        # Check array shapes
        magnitude = beam_pattern['magnitude']
        X = beam_pattern['X']
        Y = beam_pattern['Y']
        
        self.assertEqual(len(magnitude.shape), 2)
        self.assertEqual(X.shape, Y.shape)
        self.assertEqual(magnitude.shape, X.shape)
    
    def test_compute_interference_map(self):
        """Test interference map computation"""
        # Define sources
        sources = [
            {
                'position': [3.0, 3.0],
                'frequency': 2.4e9,
                'amplitude': 1.0
            },
            {
                'position': [-3.0, -3.0],
                'frequency': 2.4e9,
                'amplitude': 0.8
            }
        ]
        
        # Compute interference map
        interference_map = self.beamforming_engine.compute_interference_map(sources)
        
        # Check interference map structure
        self.assertIsNotNone(interference_map)
        self.assertIn('interference', interference_map)
        self.assertIn('X', interference_map)
        self.assertIn('Y', interference_map)
        self.assertIn('sources', interference_map)
        
        # Check data types
        interference = interference_map['interference']
        self.assertTrue(isinstance(interference, list) or isinstance(interference, np.ndarray))
    
    def test_steering_angle(self):
        """Test beam steering"""
        # Add an array
        array_config = {
            'type': 'linear',
            'num_elements': 8,
            'spacing': 0.5,
            'position': [0.0, 0.0],
            'orientation': 0.0
        }
        self.beamforming_engine.add_array(array_config)
        
        # Compute beam patterns for different steering angles
        frequencies = [2.4e9]
        
        # Test 0 degree steering
        beam_pattern_0 = self.beamforming_engine.compute_beam_pattern(frequencies, 0.0)
        
        # Test 45 degree steering
        beam_pattern_45 = self.beamforming_engine.compute_beam_pattern(frequencies, 45.0)
        
        # Patterns should be different
        self.assertFalse(np.array_equal(
            beam_pattern_0['magnitude'],
            beam_pattern_45['magnitude']
        ))
    
    def test_multiple_frequencies(self):
        """Test operation with multiple frequencies"""
        # Add an array
        array_config = {
            'type': 'linear',
            'num_elements': 8,
            'spacing': 0.5,
            'position': [0.0, 0.0],
            'orientation': 0.0
        }
        self.beamforming_engine.add_array(array_config)
        
        # Multiple frequencies
        frequencies = [2.4e9, 2.45e9, 2.5e9]
        beam_pattern = self.beamforming_engine.compute_beam_pattern(frequencies, 0.0)
        
        self.assertIsNotNone(beam_pattern)
        # Magnitude should be computed for all frequencies combined
    
    def test_scenario_loading(self):
        """Test scenario loading"""
        # Create test scenario file
        scenario_data = {
            'scenario_id': 'test_load',
            'name': 'Test Load Scenario',
            'scenario_type': '5g',
            'description': 'Test scenario for loading',
            'parameters': {
                'frequency': 3.5e9,
                'num_elements': 16,
                'array_type': 'linear'
            },
            'arrays': [
                {
                    'type': 'linear',
                    'num_elements': 16,
                    'spacing': 0.5,
                    'position': [0.0, 0.0],
                    'orientation': 0.0
                }
            ],
            'sources': [
                {
                    'source_id': 'tx1',
                    'type': 'transmitter',
                    'position': [10.0, 5.0],
                    'frequency': 3.5e9,
                    'amplitude': 1.0
                }
            ],
            'metadata': {}
        }
        
        # Save to file
        scenario_file = os.path.join(self.test_dir, 'test_scenario.json')
        with open(scenario_file, 'w') as f:
            json.dump(scenario_data, f)
        
        # Load scenario
        scenario = Scenario.load_from_file(scenario_file)
        
        # Check loaded scenario
        self.assertEqual(scenario.scenario_id, 'test_load')
        self.assertEqual(scenario.name, 'Test Load Scenario')
        self.assertEqual(scenario.scenario_type, ScenarioType.FIVE_G)
        self.assertEqual(len(scenario.sources), 1)
        self.assertEqual(len(scenario.arrays), 1)
    
    def test_phased_array_model(self):
        """Test phased array model"""
        # Create phased array
        array = PhasedArray(
            array_id='test_array',
            array_type=ArrayType.LINEAR,
            num_elements=8,
            spacing=0.5,
            position=(0.0, 0.0)
        )
        
        # Test properties
        self.assertEqual(array.array_id, 'test_array')
        self.assertEqual(array.array_type, ArrayType.LINEAR)
        self.assertEqual(array.num_elements, 8)
        self.assertEqual(len(array.elements), 8)
        
        # Test element positions
        positions = array.get_element_positions()
        self.assertEqual(positions.shape, (8, 2))
        
        # Test beam steering
        array.apply_steering(30.0)
        phases = array.get_phases()
        self.assertEqual(len(phases), 8)
        
        # Test frequency setting
        array.set_frequency(3.5e9)
        self.assertEqual(array.frequency, 3.5e9)
        self.assertEqual(array.wavelength, 3e8 / 3.5e9)
    
    def test_signal_generation(self):
        """Test signal generation utilities"""
        # Generate sine wave
        t, signal_wave = generate_sine_wave(
            frequency=1000,
            sampling_rate=44100,
            duration=1.0,
            amplitude=1.0
        )
        
        self.assertEqual(len(t), len(signal_wave))
        self.assertEqual(len(signal_wave), 44100)  # 1 second at 44.1 kHz
        
        # Compute power spectrum
        freqs, power = compute_power_spectrum(signal_wave, sampling_rate=44100)
        
        self.assertEqual(len(freqs), len(power))
        self.assertTrue(len(freqs) > 0)
    
    def test_multiple_arrays(self):
        """Test multiple array configuration"""
        # Add first array
        array1_config = {
            'type': 'linear',
            'num_elements': 8,
            'spacing': 0.5,
            'position': [0.0, 0.0],
            'orientation': 0.0
        }
        array1_id = self.beamforming_engine.add_array(array1_config)
        
        # Add second array
        array2_config = {
            'type': 'linear',
            'num_elements': 8,
            'spacing': 0.5,
            'position': [5.0, 0.0],
            'orientation': 0.0
        }
        array2_id = self.beamforming_engine.add_array(array2_config)
        
        self.assertEqual(array1_id, 0)
        self.assertEqual(array2_id, 1)
        self.assertEqual(len(self.beamforming_engine.arrays), 2)
        
        # Compute beam pattern with both arrays
        frequencies = [2.4e9]
        beam_pattern = self.beamforming_engine.compute_beam_pattern(frequencies, 0.0)
        
        self.assertIsNotNone(beam_pattern)
    
    def test_array_geometries(self):
        """Test different array geometries"""
        geometries = ['linear', 'curved', 'circular']
        
        for geometry in geometries:
            # Clear existing arrays
            self.beamforming_engine.arrays = []
            
            # Add array with specific geometry
            array_config = {
                'type': geometry,
                'num_elements': 8,
                'spacing': 0.5,
                'position': [0.0, 0.0],
                'orientation': 0.0
            }
            
            if geometry == 'curved':
                array_config['curvature'] = 0.1
            
            array_id = self.beamforming_engine.add_array(array_config)
            self.assertEqual(array_id, 0)
            
            # Compute beam pattern
            frequencies = [2.4e9]
            beam_pattern = self.beamforming_engine.compute_beam_pattern(frequencies, 0.0)
            
            self.assertIsNotNone(beam_pattern)
            self.assertIn('magnitude', beam_pattern)
    
    def test_scenario_save_load(self):
        """Test scenario save and load"""
        # Create scenario
        scenario = self._create_test_scenario()
        
        # Save to file
        scenario_file = os.path.join(self.test_dir, 'test_save_scenario.json')
        scenario.save_to_file(scenario_file)
        
        # Check file exists
        self.assertTrue(os.path.exists(scenario_file))
        
        # Load from file
        loaded_scenario = Scenario.load_from_file(scenario_file)
        
        # Compare
        self.assertEqual(scenario.scenario_id, loaded_scenario.scenario_id)
        self.assertEqual(scenario.name, loaded_scenario.name)
        self.assertEqual(len(scenario.sources), len(loaded_scenario.sources))
        self.assertEqual(len(scenario.arrays), len(loaded_scenario.arrays))
    
    def test_custom_delays(self):
        """Test applying custom delays to array"""
        # Add array
        array_config = {
            'type': 'linear',
            'num_elements': 8,
            'spacing': 0.5,
            'position': [0.0, 0.0],
            'orientation': 0.0,
            'delays': [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
        }
        
        array_id = self.beamforming_engine.add_array(array_config)
        array = self.beamforming_engine.arrays[array_id]
        
        # Check delays were applied
        self.assertEqual(len(array['delays']), 8)
        self.assertEqual(array['delays'][0], 0.0)
        self.assertEqual(array['delays'][-1], 0.7)

if __name__ == '__main__':
    unittest.main()