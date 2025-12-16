from flask import Blueprint, request, jsonify, current_app
from flask_socketio import emit
import uuid
import time
import os
import json
from datetime import datetime
from typing import Dict, List, Any

from core.beamforming_engine import BeamformingEngine
from core.task_manager import TaskManager
from utils.plotting_utils import (
    plot_beam_pattern, plot_interference_map, 
    plot_array_geometry, generate_3d_plot
)
from utils.async_utils import run_async_task
from .schemas import (
    SimulationRequest, SteeringRequest, ScenarioRequest,
    ScenarioSaveRequest, ArrayConfig, SourceConfig,
    BeamformingResponse, TaskStatusResponse,
    ScenarioInfo, SystemSummary, ErrorResponse
)

beamforming_bp = Blueprint('beamforming', __name__)
beamforming_engine = BeamformingEngine()
task_manager = TaskManager()

# Store active simulation sessions
sessions = {}

@beamforming_bp.route('/simulate', methods=['POST'])
def simulate_beamforming():
    """
    Start a beamforming simulation.
    
    Request body should contain array configurations, frequencies,
    steering angle, and other simulation parameters.
    """
    try:
        # Parse and validate request
        data = request.get_json()
        if not data:
            return jsonify(ErrorResponse(
                error="No data provided"
            ).dict()), 400
        
        # Create simulation request
        sim_request = SimulationRequest(**data)
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Store task parameters
        task_manager.tasks[task_id] = {
            'type': 'simulation',
            'parameters': sim_request.dict(),
            'status': 'pending',
            'progress': 0.0,
            'created_at': datetime.now(),
            'started_at': None,
            'completed_at': None,
            'result': None,
            'error': None
        }
        
        # Start async simulation
        def run_simulation():
            try:
                # Update task status
                task_manager.tasks[task_id]['status'] = 'running'
                task_manager.tasks[task_id]['started_at'] = datetime.now()
                task_manager.tasks[task_id]['progress'] = 0.1
                
                # Clear previous arrays and sources
                beamforming_engine.arrays = []
                beamforming_engine.sources = []
                
                # Add arrays
                for array_config in sim_request.arrays:
                    beamforming_engine.add_array(array_config.dict())
                
                # Add sources if provided
                if sim_request.sources:
                    for source_config in sim_request.sources:
                        beamforming_engine.add_source(source_config.dict())
                
                # Update progress
                task_manager.tasks[task_id]['progress'] = 0.3
                
                # Compute beam pattern
                beam_pattern = beamforming_engine.compute_beam_pattern(
                    frequencies=sim_request.frequencies,
                    steering_angle=sim_request.steering_angle,
                    grid_size=sim_request.grid_size,
                    grid_range=sim_request.grid_range
                )
                
                # Update progress
                task_manager.tasks[task_id]['progress'] = 0.6
                
                # Compute interference map if requested
                interference_map = None
                if sim_request.include_interference and sim_request.sources:
                    interference_map = beamforming_engine.compute_interference_map(
                        sources=[s.dict() for s in sim_request.sources],
                        grid_size=sim_request.grid_size,
                        grid_range=sim_request.grid_range
                    )
                
                # Update progress
                task_manager.tasks[task_id]['progress'] = 0.8
                
                # Generate visualizations
                visualizations = {}
                
                if beam_pattern:
                    # 2D beam pattern
                    beam_2d = plot_beam_pattern(
                        beam_pattern['magnitude'],
                        beam_pattern['X'],
                        beam_pattern['Y'],
                        title=f"Beam Pattern - {sim_request.steering_angle}°"
                    )
                    visualizations['beam_2d'] = beam_2d
                    
                    # 3D beam pattern
                    beam_3d = generate_3d_plot(
                        beam_pattern['magnitude'],
                        beam_pattern['X'],
                        beam_pattern['Y'],
                        title=f"3D Beam Pattern - {sim_request.steering_angle}°"
                    )
                    visualizations['beam_3d'] = beam_3d
                
                if interference_map:
                    # Interference map
                    interference = plot_interference_map(
                        interference_map['interference'],
                        interference_map['X'],
                        interference_map['Y'],
                        title="Interference Map"
                    )
                    visualizations['interference'] = interference
                
                # Array geometry
                array_positions = [arr['element_positions'].tolist() for arr in beamforming_engine.arrays]
                geometry_plot = plot_array_geometry(array_positions)
                visualizations['geometry'] = geometry_plot
                
                # Update progress
                task_manager.tasks[task_id]['progress'] = 0.9
                
                # Prepare result
                result = {
                    'beam_pattern': beam_pattern,
                    'interference_map': interference_map,
                    'array_positions': array_positions,
                    'source_positions': [s['position'] for s in beamforming_engine.sources],
                    'visualizations': visualizations,
                    'performance_metrics': beamforming_engine.get_simulation_summary(),
                    'timestamp': datetime.now().isoformat()
                }
                
                # Update task
                task_manager.tasks[task_id]['status'] = 'completed'
                task_manager.tasks[task_id]['progress'] = 1.0
                task_manager.tasks[task_id]['completed_at'] = datetime.now()
                task_manager.tasks[task_id]['result'] = result
                
                # Emit WebSocket event
                emit('simulation_complete', {
                    'task_id': task_id,
                    'status': 'completed'
                }, namespace='/beamforming', broadcast=True)
                
                return result
                
            except Exception as e:
                task_manager.tasks[task_id]['status'] = 'failed'
                task_manager.tasks[task_id]['error'] = str(e)
                task_manager.tasks[task_id]['completed_at'] = datetime.now()
                raise
        
        # Run simulation asynchronously
        run_async_task(run_simulation)
        
        # Return immediate response
        return jsonify(BeamformingResponse(
            task_id=task_id,
            status='processing',
            message='Simulation started',
            estimated_time=5.0  # Estimated 5 seconds
        ).dict()), 202
        
    except Exception as e:
        return jsonify(ErrorResponse(
            error="Simulation failed",
            details={'message': str(e)}
        ).dict()), 500

@beamforming_bp.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get status of a simulation task"""
    if task_id not in task_manager.tasks:
        return jsonify(ErrorResponse(
            error="Task not found"
        ).dict()), 404
    
    task_data = task_manager.tasks[task_id]
    
    # Build response
    response_data = {
        'task_id': task_id,
        'status': task_data['status'],
        'progress': task_data['progress'],
        'created_at': task_data['created_at'].isoformat() if task_data['created_at'] else None,
        'started_at': task_data['started_at'].isoformat() if task_data['started_at'] else None,
        'completed_at': task_data['completed_at'].isoformat() if task_data['completed_at'] else None,
        'error': task_data.get('error')
    }
    
    # Include result if available
    if task_data['status'] == 'completed' and task_data['result']:
        response_data['result'] = task_data['result']
    
    return jsonify(response_data), 200

@beamforming_bp.route('/steer', methods=['POST'])
def steer_beam():
    """Steer beam in real-time"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(ErrorResponse(
                error="No data provided"
            ).dict()), 400
        
        # Parse request
        steer_request = SteeringRequest(**data)
        
        # Update steering angle
        beam_pattern = beamforming_engine.steer_beam(steer_request.steering_angle)
        
        # Generate updated visualization
        visualizations = {}
        
        if beam_pattern:
            beam_2d = plot_beam_pattern(
                beam_pattern['magnitude'],
                beam_pattern['X'],
                beam_pattern['Y'],
                title=f"Beam Pattern - {steer_request.steering_angle}°"
            )
            visualizations['beam_2d'] = beam_2d
        
        return jsonify({
            'status': 'success',
            'steering_angle': steer_request.steering_angle,
            'beam_pattern': beam_pattern,
            'visualizations': visualizations,
            'message': f'Beam steered to {steer_request.steering_angle}°'
        }), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            error="Beam steering failed",
            details={'message': str(e)}
        ).dict()), 500

@beamforming_bp.route('/scenarios', methods=['GET'])
def get_scenarios():
    """Get list of available scenarios"""
    try:
        scenario_names = beamforming_engine.get_available_scenarios()
        
        # Load scenario details
        scenarios = []
        for name in scenario_names:
            try:
                # Try to load scenario to get details
                scenario_path = os.path.join('config/scenarios', f"{name}.json")
                with open(scenario_path, 'r') as f:
                    scenario_data = json.load(f)
                
                scenarios.append(ScenarioInfo(
                    name=name,
                    description=scenario_data.get('description', ''),
                    type=scenario_data.get('type', 'custom'),
                    parameters=scenario_data.get('parameters', {}),
                    num_arrays=len(scenario_data.get('arrays', [])),
                    num_sources=len(scenario_data.get('sources', []))
                ).dict())
            except:
                # Just include name if loading fails
                scenarios.append({
                    'name': name,
                    'description': '',
                    'type': 'custom',
                    'parameters': {},
                    'num_arrays': 0,
                    'num_sources': 0
                })
        
        return jsonify({
            'scenarios': scenarios,
            'count': len(scenarios)
        }), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            error="Failed to load scenarios",
            details={'message': str(e)}
        ).dict()), 500

@beamforming_bp.route('/scenarios/<scenario_name>', methods=['POST'])
def load_scenario(scenario_name):
    """Load a specific scenario"""
    try:
        # Parse custom parameters if provided
        data = request.get_json() or {}
        custom_params = data.get('custom_parameters', {})
        
        # Load scenario
        scenario_data = beamforming_engine.load_scenario(scenario_name)
        
        # Apply custom parameters
        for key, value in custom_params.items():
            if hasattr(beamforming_engine, key):
                setattr(beamforming_engine, key, value)
        
        # Create session
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            'scenario_name': scenario_name,
            'scenario_data': scenario_data,
            'loaded_at': datetime.now(),
            'custom_params': custom_params
        }
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'scenario_name': scenario_name,
            'scenario_data': scenario_data,
            'message': f'Scenario {scenario_name} loaded successfully'
        }), 200
        
    except FileNotFoundError:
        return jsonify(ErrorResponse(
            error="Scenario not found",
            details={'scenario_name': scenario_name}
        ).dict()), 404
    except Exception as e:
        return jsonify(ErrorResponse(
            error="Failed to load scenario",
            details={'message': str(e)}
        ).dict()), 500

@beamforming_bp.route('/scenarios/save', methods=['POST'])
def save_scenario():
    """Save current configuration as a scenario"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(ErrorResponse(
                error="No data provided"
            ).dict()), 400
        
        # Parse request
        save_request = ScenarioSaveRequest(**data)
        
        # Save scenario
        filepath = beamforming_engine.save_scenario(
            name=save_request.name,
            description=save_request.description
        )
        
        return jsonify({
            'status': 'success',
            'scenario_name': save_request.name,
            'filepath': filepath,
            'message': f'Scenario {save_request.name} saved successfully'
        }), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            error="Failed to save scenario",
            details={'message': str(e)}
        ).dict()), 500

@beamforming_bp.route('/array', methods=['POST'])
def add_array():
    """Add a new array to the simulation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(ErrorResponse(
                error="No data provided"
            ).dict()), 400
        
        # Parse array configuration
        array_config = ArrayConfig(**data)
        
        # Add array
        array_id = beamforming_engine.add_array(array_config.dict())
        
        # Get array details
        array_details = beamforming_engine.arrays[array_id] if array_id < len(beamforming_engine.arrays) else None
        
        return jsonify({
            'status': 'success',
            'array_id': array_id,
            'array_details': array_details,
            'message': 'Array added successfully'
        }), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            error="Failed to add array",
            details={'message': str(e)}
        ).dict()), 500

@beamforming_bp.route('/array/<array_id>', methods=['PUT'])
def update_array(array_id):
    """Update array parameters"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(ErrorResponse(
                error="No data provided"
            ).dict()), 400
        
        # Try to parse as integer first, then as string
        try:
            array_idx = int(array_id)
        except ValueError:
            # Look up array by ID
            array_idx = None
            for i, array in enumerate(beamforming_engine.arrays):
                if array.get('array_id') == array_id:
                    array_idx = i
                    break
        
        if array_idx is None or array_idx >= len(beamforming_engine.arrays):
            return jsonify(ErrorResponse(
                error="Array not found"
            ).dict()), 404
        
        # Update array parameters
        for key, value in data.items():
            if key in beamforming_engine.arrays[array_idx]:
                beamforming_engine.arrays[array_idx][key] = value
        
        # Recalculate element positions if geometry parameters changed
        if any(k in data for k in ['type', 'num_elements', 'spacing', 'position', 'orientation', 'curvature']):
            beamforming_engine.arrays[array_idx]['element_positions'] = beamforming_engine._calculate_element_positions(
                beamforming_engine.arrays[array_idx]
            )
        
        return jsonify({
            'status': 'success',
            'array_id': array_idx,
            'updated_parameters': data,
            'message': 'Array updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            error="Failed to update array",
            details={'message': str(e)}
        ).dict()), 500

@beamforming_bp.route('/source', methods=['POST'])
def add_source():
    """Add a new source to the simulation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(ErrorResponse(
                error="No data provided"
            ).dict()), 400
        
        # Parse source configuration
        source_config = SourceConfig(**data)
        
        # Add source
        source_id = beamforming_engine.add_source(source_config.dict())
        
        return jsonify({
            'status': 'success',
            'source_id': source_id,
            'message': 'Source added successfully'
        }), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            error="Failed to add source",
            details={'message': str(e)}
        ).dict()), 500

@beamforming_bp.route('/visualize', methods=['POST'])
def visualize():
    """Generate custom visualizations"""
    try:
        data = request.get_json() or {}
        viz_type = data.get('type', 'beam_pattern')
        parameters = data.get('parameters', {})
        
        visualizations = {}
        
        if viz_type == 'beam_pattern' and beamforming_engine.beam_pattern:
            # Generate beam pattern visualization
            beam_2d = plot_beam_pattern(
                beamforming_engine.beam_pattern['magnitude'],
                beamforming_engine.beam_pattern['X'],
                beamforming_engine.beam_pattern['Y'],
                title="Current Beam Pattern"
            )
            visualizations['beam_2d'] = beam_2d
            
            # Generate 3D visualization
            beam_3d = generate_3d_plot(
                beamforming_engine.beam_pattern['magnitude'],
                beamforming_engine.beam_pattern['X'],
                beamforming_engine.beam_pattern['Y'],
                title="3D Beam Pattern"
            )
            visualizations['beam_3d'] = beam_3d
        
        elif viz_type == 'interference' and beamforming_engine.interference_map:
            # Generate interference visualization
            interference = plot_interference_map(
                beamforming_engine.interference_map['interference'],
                beamforming_engine.interference_map['X'],
                beamforming_engine.interference_map['Y'],
                title="Interference Map"
            )
            visualizations['interference'] = interference
        
        elif viz_type == 'geometry':
            # Generate array geometry visualization
            array_positions = [arr['element_positions'].tolist() for arr in beamforming_engine.arrays]
            geometry = plot_array_geometry(array_positions)
            visualizations['geometry'] = geometry
        
        elif viz_type == 'all':
            # Generate all available visualizations
            if beamforming_engine.beam_pattern:
                beam_2d = plot_beam_pattern(
                    beamforming_engine.beam_pattern['magnitude'],
                    beamforming_engine.beam_pattern['X'],
                    beamforming_engine.beam_pattern['Y']
                )
                visualizations['beam_2d'] = beam_2d
            
            if beamforming_engine.interference_map:
                interference = plot_interference_map(
                    beamforming_engine.interference_map['interference'],
                    beamforming_engine.interference_map['X'],
                    beamforming_engine.interference_map['Y']
                )
                visualizations['interference'] = interference
            
            array_positions = [arr['element_positions'].tolist() for arr in beamforming_engine.arrays]
            geometry = plot_array_geometry(array_positions)
            visualizations['geometry'] = geometry
        
        return jsonify({
            'visualizations': visualizations,
            'type': viz_type,
            'parameters': parameters
        }), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            error="Visualization failed",
            details={'message': str(e)}
        ).dict()), 500

@beamforming_bp.route('/summary', methods=['GET'])
def get_summary():
    """Get summary of current simulation setup"""
    try:
        summary = beamforming_engine.get_simulation_summary()
        
        return jsonify(SystemSummary(
            num_arrays=summary['num_arrays'],
            num_sources=summary['num_sources'],
            frequencies=beamforming_engine.frequencies,
            grid_size=beamforming_engine.grid_size,
            grid_range=beamforming_engine.grid_range,
            beam_pattern_available=summary['has_beam_pattern'],
            interference_map_available=summary['has_interference_map']
        ).dict()), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            error="Failed to get summary",
            details={'message': str(e)}
        ).dict()), 500

@beamforming_bp.route('/clear', methods=['POST'])
def clear_simulation():
    """Clear all simulation data"""
    try:
        beamforming_engine.clear_simulation()
        task_manager.tasks.clear()
        
        return jsonify({
            'status': 'success',
            'message': 'Simulation cleared successfully'
        }), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            error="Failed to clear simulation",
            details={'message': str(e)}
        ).dict()), 500

@beamforming_bp.route('/export', methods=['POST'])
def export_results():
    """Export simulation results"""
    try:
        data = request.get_json() or {}
        export_type = data.get('type', 'json')
        
        # Prepare export data
        export_data = {
            'arrays': beamforming_engine.arrays,
            'sources': beamforming_engine.sources,
            'frequencies': beamforming_engine.frequencies,
            'beam_pattern': beamforming_engine.beam_pattern,
            'interference_map': beamforming_engine.interference_map,
            'grid_size': beamforming_engine.grid_size,
            'grid_range': beamforming_engine.grid_range,
            'export_time': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        if export_type == 'json':
            return jsonify(export_data), 200
        elif export_type == 'csv':
            # Convert to CSV format (simplified)
            csv_lines = []
            csv_lines.append("Parameter,Value")
            csv_lines.append(f"num_arrays,{len(beamforming_engine.arrays)}")
            csv_lines.append(f"num_sources,{len(beamforming_engine.sources)}")
            csv_lines.append(f"frequencies,{','.join(map(str, beamforming_engine.frequencies))}")
            
            response = "\n".join(csv_lines)
            return response, 200, {'Content-Type': 'text/csv'}
        else:
            return jsonify(ErrorResponse(
                error="Unsupported export type",
                details={'supported_types': ['json', 'csv']}
            ).dict()), 400
            
    except Exception as e:
        return jsonify(ErrorResponse(
            error="Export failed",
            details={'message': str(e)}
        ).dict()), 500

@beamforming_bp.route('/performance', methods=['GET'])
def get_performance():
    """Get performance metrics for current setup"""
    try:
        from utils.array_utils import analyze_array_performance
        
        if not beamforming_engine.arrays:
            return jsonify(ErrorResponse(
                error="No arrays configured"
            ).dict()), 400
        
        # Analyze first array
        array = beamforming_engine.arrays[0]
        positions = array['element_positions']
        frequency = beamforming_engine.frequencies[0] if beamforming_engine.frequencies else 2.4e9
        
        # Get weights
        weights = array.get('amplitudes')
        if weights is None:
            weights = np.ones(len(positions))
        
        # Analyze performance
        performance = analyze_array_performance(
            positions=positions,
            frequency=frequency,
            steering_angle=0.0,  # Assume broadside for analysis
            weights=weights
        )
        
        return jsonify({
            'performance': performance,
            'array_type': array['type'],
            'num_elements': array['num_elements'],
            'frequency': frequency
        }), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            error="Performance analysis failed",
            details={'message': str(e)}
        ).dict()), 500