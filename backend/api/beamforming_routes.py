"""
Beamforming API Routes
Handles all beamforming-related API endpoints
"""
from flask import Blueprint, request, jsonify
import logging
import sys

from core.beamforming.beamforming_simulator import BeamformingSimulator
from core.beamforming.scenario_manager import ScenarioManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

beamforming_bp = Blueprint('beamforming', __name__, url_prefix='/api')

# Initialize scenario manager
scenario_manager = ScenarioManager(scenarios_dir='scenarios')

@beamforming_bp.route('/scenarios', methods=['GET'])
def get_scenarios():
    """Get all available scenarios"""
    try:
        scenarios = scenario_manager.get_all_scenarios()
        return jsonify({'success': True, 'scenarios': scenarios})
    except Exception as e:
        logging.error(f"Error fetching scenarios: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@beamforming_bp.route('/scenario/<scenario_name>', methods=['GET'])
def get_scenario(scenario_name):
    """Get a specific scenario by name"""
    try:
        scenario = scenario_manager.load_scenario(scenario_name)
        if scenario:
            return jsonify({'success': True, 'scenario': scenario})
        return jsonify({'success': False, 'error': 'Scenario not found'}), 404
    except Exception as e:
        logging.error(f"Error loading scenario: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@beamforming_bp.route('/compute_interference', methods=['POST'])
def compute_interference():
    """Compute interference map"""
    try:
        data = request.json

        simulator = BeamformingSimulator(
            frequency=data.get('frequency', 2.4e9),
            mode=data.get('mode', 'transmitter')
        )
        if 'arrays' in data:
            simulator.update_parameters(arrays=data['arrays'])
        else:
            simulator.update_parameters(
                num_elements=data.get('num_elements', 16),
                element_spacing=data.get('element_spacing', 0.5),
                beam_angle=data.get('beam_angle', 0),
                array_type=data.get('array_type', 'linear'),
                mode=data.get('mode', 'transmitter')
            )

        result = simulator.compute_interference_map(
            grid_size=data.get('grid_size', 400),
            grid_range=data.get('grid_range', 20)
        )

        return jsonify({
            'success': True,
            'data': {
                'interference': result['interference'].tolist(),
                'intensity': result['intensity'].tolist(),
                'x_grid': result['X'].tolist(),
                'y_grid': result['Y'].tolist(),
                'positions': result['positions'].tolist()
            }
        })
    except Exception as e:
        logging.error(f"Error computing interference: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@beamforming_bp.route('/compute_beam_profile', methods=['POST'])
def compute_beam_profile():
    """Compute beam profile"""
    try:
        data = request.json

        simulator = BeamformingSimulator(
            frequency=data.get('frequency', 2.4e9),
            mode=data.get('mode', 'transmitter')
        )
        if 'arrays' in data:
            simulator.update_parameters(arrays=data['arrays'])
        else:
            simulator.update_parameters(
                num_elements=data.get('num_elements', 16),
                element_spacing=data.get('element_spacing', 0.5),
                beam_angle=data.get('beam_angle', 0),
                array_type=data.get('array_type', 'linear'),
                mode=data.get('mode', 'transmitter')
            )

        result = simulator.compute_beam_profile(
            num_angles=data.get('num_angles', 1000)
        )

        return jsonify({
            'success': True,
            'data': {
                'angles': result['angles'] if isinstance(result['angles'], list) else result['angles'].tolist(),
                'magnitude': result['magnitude'] if isinstance(result['magnitude'], list) else result['magnitude'].tolist(),
                'magnitude_db': result['magnitude_db'] if isinstance(result['magnitude_db'], list) else result['magnitude_db'].tolist()
            }
        })
    except Exception as e:
        logging.error(f"Error computing beam profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@beamforming_bp.route('/compute_array_positions', methods=['POST'])
def compute_array_positions():
    """Compute array element positions"""
    try:
        data = request.json

        simulator = BeamformingSimulator(frequency=data.get('frequency', 2.4e9))
        if 'arrays' in data:
            simulator.update_parameters(arrays=data['arrays'])
        else:
            simulator.update_parameters(
                num_elements=data.get('num_elements', 16),
                element_spacing=data.get('element_spacing', 0.5),
                array_type=data.get('array_type', 'linear')
            )

        positions = simulator.get_element_positions()

        return jsonify({
            'success': True,
            'data': {
                'x_positions': positions[0].tolist(),
                'y_positions': positions[1].tolist()
            }
        })
    except Exception as e:
        logging.error(f"Error computing positions: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@beamforming_bp.route('/save_scenario', methods=['POST'])
def save_scenario():
    """Save a scenario"""
    try:
        data = request.json
        scenario_manager.save_scenario(data)
        return jsonify({'success': True, 'message': 'Scenario saved successfully'})
    except Exception as e:
        logging.error(f"Error saving scenario: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
