from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import numpy as np
import logging
import sys
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

# ===============================
# LOGGING → PRINT TO TERMINAL
# ===============================
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

app.logger.setLevel(logging.DEBUG)

# ===============================
# IMPORT CORE MODULES
# ===============================
from core.phased_array import PhasedArray
from core.beamforming_simulator import BeamformingSimulator
from models.scenario_manager import ScenarioManager

# Initialize managers
scenario_manager = ScenarioManager()

@app.route('/')
def index():
    logging.debug("Rendering index page")
    return render_template('index.html')

@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    logging.debug("GET /api/scenarios called")
    try:
        scenarios = scenario_manager.get_all_scenarios()
        logging.debug(f"Scenarios loaded: {len(scenarios)}")
        return jsonify({'success': True, 'scenarios': scenarios})
    except Exception as e:
        logging.error(f"Error fetching scenarios: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scenario/<scenario_name>', methods=['GET'])
def get_scenario(scenario_name):
    logging.debug(f"GET /api/scenario/{scenario_name} called")
    try:
        scenario = scenario_manager.load_scenario(scenario_name)
        if scenario:
            logging.debug("Scenario found")
            return jsonify({'success': True, 'scenario': scenario})
        logging.debug("Scenario not found")
        return jsonify({'success': False, 'error': 'Scenario not found'}), 404
    except Exception as e:
        logging.error(f"Error loading scenario: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/compute_interference', methods=['POST'])
def compute_interference():
    logging.debug("POST /api/compute_interference called")
    try:
        data = request.json
        logging.debug(f"Request data: {data}")

        simulator = BeamformingSimulator(
            num_elements=data.get('num_elements', 16),
            frequency=data.get('frequency', 2.4e9),
            element_spacing=data.get('element_spacing', None),
            beam_angle=data.get('beam_angle', 0),
            array_type=data.get('array_type', 'linear'),
            mode=data.get('mode', 'transmitter')
        )

        result = simulator.compute_interference_map(
            grid_size=data.get('grid_size', 400),
            grid_range=data.get('grid_range', 20)
        )

        logging.debug("Interference map computed successfully")

        return jsonify({
            'success': True,
            'data': {
                'interference': result['interference'].tolist(),
                'x_grid': result['X'].tolist(),
                'y_grid': result['Y'].tolist(),
                'positions': result['positions'].tolist()
            }
        })
    except Exception as e:
        logging.error(f"Error computing interference: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/compute_beam_profile', methods=['POST'])
def compute_beam_profile():
    logging.debug("POST /api/compute_beam_profile called")
    try:
        data = request.json
        logging.debug(f"Request data: {data}")

        simulator = BeamformingSimulator(
            num_elements=data.get('num_elements', 16),
            frequency=data.get('frequency', 2.4e9),
            element_spacing=data.get('element_spacing', None),
            beam_angle=data.get('beam_angle', 0),
            array_type=data.get('array_type', 'linear'),
            mode=data.get('mode', 'transmitter')
        )

        result = simulator.compute_beam_profile(
            num_angles=data.get('num_angles', 1000)
        )

        logging.debug("Beam profile computed successfully")

        return jsonify({
            'success': True,
            'data': {
                'angles': result['angles'].tolist(),
                'magnitude': result['magnitude'].tolist(),
                'magnitude_db': result['magnitude_db'].tolist()
            }
        })
    except Exception as e:
        logging.error(f"Error computing beam profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/compute_array_positions', methods=['POST'])
def compute_array_positions():
    logging.debug("POST /api/compute_array_positions called")
    try:
        data = request.json
        logging.debug(f"Request data: {data}")

        simulator = BeamformingSimulator(
            num_elements=data.get('num_elements', 16),
            frequency=data.get('frequency', 2.4e9),
            element_spacing=data.get('element_spacing', None),
            array_type=data.get('array_type', 'linear')
        )

        positions = simulator.get_element_positions()
        logging.debug("Array positions computed")

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

@app.route('/api/save_scenario', methods=['POST'])
def save_scenario():
    logging.debug("POST /api/save_scenario called")
    try:
        data = request.json
        logging.debug(f"Scenario data: {data}")
        scenario_manager.save_scenario(data)
        logging.debug("Scenario saved successfully")
        return jsonify({'success': True, 'message': 'Scenario saved successfully'})
    except Exception as e:
        logging.error(f"Error saving scenario: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    logging.debug("Starting Flask app in DEBUG mode")
    app.run(debug=True, host='0.0.0.0', port=5000)
