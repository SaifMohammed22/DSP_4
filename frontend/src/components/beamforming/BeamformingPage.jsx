import React, { useState, useEffect, useCallback, useRef } from 'react';
import './BeamformingStyles.css';
import BeamVisualization from './BeamVisualization';
import BeamProfile from './BeamProfile';
import ArrayControls from './ArrayControls';
import ParameterControls from './ParameterControls';
import ScenarioSelector from './ScenarioSelector';

const API_BASE = 'http://localhost:5000/api';

const BeamformingPage = () => {
    // State
    const [arrays, setArrays] = useState([
        {
            array_id: 'array_1',
            num_elements: 16,
            geometry: 'linear',
            element_spacing: 0.5,
            curvature_radius: 10,
            beam_angle: 0,
            position: [0, 0],
            orientation: 0,
            phase_shift: 0
        }
    ]);
    const [selectedArrayId, setSelectedArrayId] = useState('array_1');
    const [globalParams, setGlobalParams] = useState({
        frequency: 2.4e9,
        mode: 'transmitter',
        grid_size: 400,
        grid_range: 20
    });

    const [scenarios, setScenarios] = useState([]);
    const [selectedScenario, setSelectedScenario] = useState('');
    const [interferenceData, setInterferenceData] = useState(null);
    const [beamProfileData, setBeamProfileData] = useState(null);
    const [arrayPositions, setArrayPositions] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    // Frequency UI state
    const [frequencyValue, setFrequencyValue] = useState(24);
    const [frequencyUnit, setFrequencyUnit] = useState('GHz');

    // Refs
    const updateTimeoutRef = useRef(null);
    const isUpdatingRef = useRef(false);

    // Update global frequency when UI changes
    useEffect(() => {
        const freq = frequencyValue * (frequencyUnit === 'MHz' ? 1e6 : 1e9);
        setGlobalParams(prev => ({ ...prev, frequency: freq }));
    }, [frequencyValue, frequencyUnit]);

    // Load scenarios
    const loadScenarios = useCallback(async () => {
        try {
            const response = await fetch(`${API_BASE}/scenarios`);
            const data = await response.json();
            if (data.success) {
                setScenarios(data.scenarios);
            }
        } catch (error) {
            console.error('Error loading scenarios:', error);
        }
    }, []);

    // Load a specific scenario
    const handleScenarioSelect = useCallback(async (scenarioName) => {
        if (!scenarioName) return;

        try {
            setIsLoading(true);
            const response = await fetch(`${API_BASE}/scenario/${encodeURIComponent(scenarioName)}`);
            const data = await response.json();

            if (data.success) {
                const scenario = data.scenario;

                // Handle legacy scenario format vs new format
                let newArrays = [];
                if (scenario.arrays) {
                    newArrays = scenario.arrays;
                } else {
                    // Convert legacy single array to list
                    newArrays = [{
                        array_id: 'array_1',
                        num_elements: scenario.num_elements || 16,
                        geometry: scenario.array_type || 'linear',
                        element_spacing: scenario.element_spacing || 0.5,
                        curvature_radius: scenario.curvature_radius || 10,
                        beam_angle: scenario.beam_angle || 0,
                        position: [0, 0],
                        orientation: 0
                    }];
                }

                setArrays(newArrays);
                setSelectedArrayId(newArrays[0]?.array_id || null);

                // Update global params
                setGlobalParams(prev => ({
                    ...prev,
                    frequency: scenario.frequency || prev.frequency,
                    mode: scenario.mode || prev.mode,
                    grid_range: scenario.grid_range || prev.grid_range
                }));

                // Update frequency UI
                const freq = scenario.frequency || 2.4e9;
                if (freq >= 1e9) {
                    setFrequencyUnit('GHz');
                    setFrequencyValue(freq / 1e9);
                } else {
                    setFrequencyUnit('MHz');
                    setFrequencyValue(freq / 1e6);
                }

                setSelectedScenario(scenarioName);
            }
        } catch (error) {
            console.error('Error loading scenario:', error);
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Array Management
    const handleAddArray = () => {
        const newArrayId = `array_${Date.now()}`;
        const newArray = {
            array_id: newArrayId,
            num_elements: 16,
            geometry: 'linear',
            element_spacing: 0.5,
            curvature_radius: 10,
            beam_angle: 0,
            position: [0, 0],
            orientation: 0,
            phase_shift: 0
        };
        setArrays([...arrays, newArray]);
        setSelectedArrayId(newArrayId);
    };

    const handleDeleteArray = (arrayId) => {
        if (arrays.length <= 1) return; // Prevent deleting last array
        const newArrays = arrays.filter(a => a.array_id !== arrayId);
        setArrays(newArrays);
        if (selectedArrayId === arrayId) {
            setSelectedArrayId(newArrays[0].array_id);
        }
    };

    const handleUpdateArray = (updates) => {
        setArrays(prevArrays => prevArrays.map(arr =>
            arr.array_id === selectedArrayId ? { ...arr, ...updates } : arr
        ));
    };

    // Visualization Update
    const updateVisualization = useCallback(async () => {
        if (isUpdatingRef.current) return;

        if (updateTimeoutRef.current) {
            clearTimeout(updateTimeoutRef.current);
        }

        updateTimeoutRef.current = window.setTimeout(async () => {
            isUpdatingRef.current = true;
            setIsLoading(true);

            try {
                const payload = {
                    ...globalParams,
                    arrays: arrays
                };

                const [arrayRes, interferenceRes, profileRes] = await Promise.all([
                    fetch(`${API_BASE}/compute_array_positions`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    }),
                    fetch(`${API_BASE}/compute_interference`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    }),
                    fetch(`${API_BASE}/compute_beam_profile`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    })
                ]);

                const arrayData = await arrayRes.json();
                const interferenceData = await interferenceRes.json();
                const profileData = await profileRes.json();

                if (arrayData.success) setArrayPositions(arrayData.data);
                if (interferenceData.success) setInterferenceData(interferenceData.data);
                if (profileData.success) setBeamProfileData(profileData.data);
            } catch (error) {
                console.error('Error updating visualization:', error);
            } finally {
                setIsLoading(false);
                isUpdatingRef.current = false;
            }
        }, 150); // Small debounce
    }, [arrays, globalParams]);

    // Initial load
    useEffect(() => {
        loadScenarios();
        // Initial visualization update is triggered by effect below
    }, [loadScenarios]);

    // Update when state changes
    useEffect(() => {
        updateVisualization();
    }, [updateVisualization]);

    // Prepare field data
    const fieldData = interferenceData ? {
        intensity: interferenceData.interference,
        x_coords: interferenceData.x_grid[0] || [],
        y_coords: interferenceData.y_grid.map(row => row[0]) || [],
        element_positions: interferenceData.positions,
        beam_profile: beamProfileData ? {
            angles: beamProfileData.angles,
            intensity: beamProfileData.magnitude
        } : undefined
    } : null;

    const selectedArray = arrays.find(a => a.array_id === selectedArrayId) || arrays[0];

    return (
        <div className="beamforming-page">
            {/* Control Panel */}
            <div className="beamforming-controls">

                {/* Global Settings */}
                <div className="control-section">
                    <div className="section-header">
                        <h3>Global Settings</h3>
                    </div>
                    <div className="section-content">
                        <div className="parameter-group">
                            <div className="parameter-label">
                                <span>Frequency: {frequencyValue} {frequencyUnit}</span>
                            </div>
                            <div className="slider-row">
                                <input
                                    type="range"
                                    className="parameter-slider"
                                    min="1"
                                    max="100"
                                    value={frequencyValue}
                                    onChange={(e) => setFrequencyValue(parseInt(e.target.value))}
                                />
                                <select
                                    value={frequencyUnit}
                                    onChange={(e) => setFrequencyUnit(e.target.value)}
                                    className="control-select frequency-unit"
                                >
                                    <option value="MHz">MHz</option>
                                    <option value="GHz">GHz</option>
                                </select>
                            </div>
                        </div>

                        <div className="parameter-group" style={{ marginTop: '12px' }}>
                            <label className="parameter-label">Mode</label>
                            <select
                                value={globalParams.mode}
                                onChange={(e) => setGlobalParams(prev => ({ ...prev, mode: e.target.value }))}
                                className="control-select"
                            >
                                <option value="transmitter">Transmitter</option>
                                <option value="receiver">Receiver</option>
                            </select>
                        </div>
                    </div>
                </div>

                <ScenarioSelector
                    scenarios={scenarios}
                    activeScenario={selectedScenario}
                    onSelect={handleScenarioSelect}
                    isLoading={isLoading}
                />

                <ArrayControls
                    arrays={arrays}
                    selectedArrayId={selectedArrayId}
                    onSelectArray={setSelectedArrayId}
                    onAddArray={handleAddArray}
                    onDeleteArray={handleDeleteArray}
                />

                {selectedArray && (
                    <ParameterControls
                        array={selectedArray}
                        onUpdateArray={handleUpdateArray}
                        isLoading={isLoading}
                    />
                )}
            </div>

            {/* Visualization Panel */}
            <div className="visualization-panel">
                <div className="viz-section">
                    <h3>Constructive/Destructive Interference Map</h3>
                    <div className="plot-container">
                        <BeamVisualization fieldData={fieldData} isLoading={isLoading} />
                    </div>
                </div>

                <div className="viz-section">
                    <h3>Beam Profile (Polar)</h3>
                    <div className="plot-container">
                        <BeamProfile fieldData={fieldData} isLoading={isLoading} />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default BeamformingPage;
