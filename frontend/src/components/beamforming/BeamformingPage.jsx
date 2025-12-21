import React, { useState, useEffect, useCallback, useRef } from 'react';
import './BeamformingStyles.css';
import BeamVisualization from './BeamVisualization';
import BeamProfile from './BeamProfile';

const API_BASE = 'http://localhost:5000/api';

const BeamformingPage = () => {
    // Main state
    const [numElements, setNumElements] = useState(8);
    const [elementSpacing, setElementSpacing] = useState(0.5);
    const [phaseShift, setPhaseShift] = useState(0);
    const [frequency, setFrequency] = useState(5);
    const [geometry, setGeometry] = useState('linear');
    const [curvatureRadius, setCurvatureRadius] = useState(5);
    const [mode, setMode] = useState('transmitter');

    // Visualization data
    const [interferenceData, setInterferenceData] = useState(null);
    const [beamProfileData, setBeamProfileData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    // Scenarios
    const [scenarios, setScenarios] = useState([]);
    const [selectedScenario, setSelectedScenario] = useState('');

    // Debounce ref
    const updateTimeoutRef = useRef(null);

    // Load scenarios
    useEffect(() => {
        fetch(`${API_BASE}/scenarios`)
            .then(res => res.json())
            .then(data => {
                if (data.success) setScenarios(data.scenarios);
            })
            .catch(console.error);
    }, []);

    // Update visualization
    const updateVisualization = useCallback(async () => {
        if (updateTimeoutRef.current) {
            clearTimeout(updateTimeoutRef.current);
        }

        updateTimeoutRef.current = setTimeout(async () => {
            setIsLoading(true);

            const payload = {
                frequency,
                mode,
                grid_size: 300,
                grid_range: 20,
                arrays: [{
                    num_elements: numElements,
                    element_spacing: elementSpacing,
                    geometry,
                    curvature_radius: curvatureRadius,
                    position: [0, 0],
                    orientation: 0,
                    phase_shift: phaseShift
                }]
            };

            try {
                const [interferenceRes, profileRes] = await Promise.all([
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

                const interferenceJson = await interferenceRes.json();
                const profileJson = await profileRes.json();

                if (interferenceJson.success) setInterferenceData(interferenceJson.data);
                if (profileJson.success) setBeamProfileData(profileJson.data);
            } catch (error) {
                console.error('Error updating visualization:', error);
            } finally {
                setIsLoading(false);
            }
        }, 100);
    }, [numElements, elementSpacing, phaseShift, frequency, geometry, curvatureRadius, mode]);

    // Trigger updates
    useEffect(() => {
        updateVisualization();
    }, [updateVisualization]);

    // Load scenario
    const loadScenario = async (scenarioId) => {
        if (!scenarioId) return;
        setSelectedScenario(scenarioId);

        try {
            const res = await fetch(`${API_BASE}/scenario/${scenarioId}`);
            const data = await res.json();

            if (data.success && data.scenario) {
                const s = data.scenario;
                const arr = s.arrays?.[0] || {};

                setNumElements(arr.num_elements || 8);
                setElementSpacing(arr.element_spacing || 0.5);
                setPhaseShift(arr.phase_shift || 0);
                setFrequency(s.frequency || 5);
                setGeometry(arr.geometry || 'linear');
                setCurvatureRadius(arr.curvature_radius || 5);
                setMode(s.mode || 'transmitter');
            }
        } catch (error) {
            console.error('Error loading scenario:', error);
        }
    };

    // Prepare field data for visualization
    const fieldData = interferenceData ? {
        intensity: interferenceData.interference,
        x_coords: interferenceData.x_grid?.[0] || [],
        y_coords: interferenceData.y_grid?.map(row => row[0]) || [],
        element_positions: interferenceData.positions,
        beam_profile: beamProfileData ? {
            angles: beamProfileData.angles,
            intensity: beamProfileData.magnitude
        } : undefined
    } : null;

    return (
        <div className="beamforming-container">
            {/* Control Panel */}
            <div className="control-panel">
                {/* Mode Toggle */}
                <div className="control-group">
                    <label>Mode</label>
                    <div className="toggle-group">
                        <button
                            className={mode === 'transmitter' ? 'active' : ''}
                            onClick={() => setMode('transmitter')}
                        >
                            Transmitting
                        </button>
                        <button
                            className={mode === 'receiver' ? 'active' : ''}
                            onClick={() => setMode('receiver')}
                        >
                            Receiving
                        </button>
                    </div>
                </div>

                {/* Number of Elements */}
                <div className="control-group">
                    <label>Number of Elements: <span className="value">{numElements}</span></label>
                    <div className="stepper">
                        <button onClick={() => setNumElements(Math.max(2, numElements - 1))}>−</button>
                        <input
                            type="range"
                            min="2"
                            max="64"
                            value={numElements}
                            onChange={(e) => setNumElements(parseInt(e.target.value))}
                        />
                        <button onClick={() => setNumElements(Math.min(64, numElements + 1))}>+</button>
                    </div>
                </div>

                {/* Phase Shift */}
                <div className="control-group">
                    <label>Phase Shift: <span className="value">{(phaseShift / Math.PI).toFixed(2)}π</span></label>
                    <input
                        type="range"
                        min={-Math.PI}
                        max={Math.PI}
                        step={0.01}
                        value={phaseShift}
                        onChange={(e) => setPhaseShift(parseFloat(e.target.value))}
                    />
                </div>

                {/* Frequency */}
                <div className="control-group">
                    <label>Frequency: <span className="value">{frequency}</span></label>
                    <input
                        type="range"
                        min="1"
                        max="20"
                        value={frequency}
                        onChange={(e) => setFrequency(parseInt(e.target.value))}
                    />
                </div>

                {/* Element Spacing */}
                <div className="control-group">
                    <label>Element Spacing: <span className="value">{elementSpacing.toFixed(2)}λ</span></label>
                    <input
                        type="range"
                        min="0.1"
                        max="2"
                        step="0.05"
                        value={elementSpacing}
                        onChange={(e) => setElementSpacing(parseFloat(e.target.value))}
                    />
                </div>

                {/* Geometry */}
                <div className="control-group">
                    <label>Array Geometry</label>
                    <div className="toggle-group">
                        <button
                            className={geometry === 'linear' ? 'active' : ''}
                            onClick={() => setGeometry('linear')}
                        >
                            Linear
                        </button>
                        <button
                            className={geometry === 'curved' ? 'active' : ''}
                            onClick={() => setGeometry('curved')}
                        >
                            Curved
                        </button>
                    </div>
                </div>

                {/* Curvature Radius (shown only for curved) */}
                {geometry === 'curved' && (
                    <div className="control-group">
                        <label>Curvature Radius: <span className="value">{curvatureRadius}</span></label>
                        <input
                            type="range"
                            min="1"
                            max="20"
                            value={curvatureRadius}
                            onChange={(e) => setCurvatureRadius(parseInt(e.target.value))}
                        />
                    </div>
                )}

                {/* Scenarios */}
                <div className="control-group scenarios">
                    <label>Load Scenario</label>
                    <div className="scenario-buttons">
                        {scenarios.map(s => (
                            <button
                                key={s.id}
                                className={selectedScenario === s.id ? 'active' : ''}
                                onClick={() => loadScenario(s.id)}
                                title={s.description}
                            >
                                {s.name}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Visualization Panel */}
            <div className="visualization-panel">
                <div className="viz-box">
                    <div className="viz-title">Constructive/Destructive Interference Map</div>
                    <div className="viz-content">
                        <BeamVisualization fieldData={fieldData} isLoading={isLoading} />
                    </div>
                </div>
                <div className="viz-box">
                    <div className="viz-title">Beam Profile</div>
                    <div className="viz-content">
                        <BeamProfile fieldData={fieldData} isLoading={isLoading} />
                    </div>
                </div>
            </div>

            {/* Loading indicator */}
            {isLoading && <div className="global-loading">Updating...</div>}
        </div>
    );
};

export default BeamformingPage;
