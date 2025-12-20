import React, { useState, useEffect } from 'react';

const ParameterControls = ({
    array,
    onUpdateArray,
    isLoading
}) => {
    // Local state for controlled inputs
    const [numElements, setNumElements] = useState(8);
    const [elementSpacing, setElementSpacing] = useState(0.5);
    const [geometry, setGeometry] = useState('linear');
    const [curvatureRadius, setCurvatureRadius] = useState(10);
    const [phaseShift, setPhaseShift] = useState(0);
    const [posX, setPosX] = useState(0);
    const [posY, setPosY] = useState(0);
    const [orientation, setOrientation] = useState(0);

    // Sync with array prop
    useEffect(() => {
        if (array) {
            setNumElements(array.num_elements);
            setElementSpacing(array.element_spacing);
            setGeometry(array.geometry);
            setCurvatureRadius(array.curvature_radius);
            setPosX(array.position[0]);
            setPosY(array.position[1]);
            setOrientation(array.orientation);
        }
    }, [array]);

    // Handle changes with debounce
    const handleNumElementsChange = (value) => {
        setNumElements(value);
        onUpdateArray({ num_elements: value });
    };

    const handleSpacingChange = (value) => {
        setElementSpacing(value);
        onUpdateArray({ element_spacing: value });
    };

    const handleGeometryChange = (value) => {
        setGeometry(value);
        onUpdateArray({ geometry: value });
    };

    const handleCurvatureChange = (value) => {
        setCurvatureRadius(value);
        onUpdateArray({ curvature_radius: value });
    };

    const handlePhaseShiftChange = (value) => {
        setPhaseShift(value);
        onUpdateArray({ phase_shift: value });
    };

    const handlePositionChange = (x, y) => {
        setPosX(x);
        setPosY(y);
        onUpdateArray({ position: [x, y] });
    };

    const handleOrientationChange = (value) => {
        setOrientation(value);
        onUpdateArray({ orientation: value });
    };

    return (
        <div className="control-section">
            <div className="section-header">
                <h3>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="3" />
                        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
                    </svg>
                    Array Parameters
                </h3>
            </div>
            <div className="section-content">
                {/* Geometry Toggle */}
                <div className="geometry-toggle">
                    <button
                        className={`geometry-btn ${geometry === 'linear' ? 'active' : ''}`}
                        onClick={() => handleGeometryChange('linear')}
                        disabled={isLoading}
                    >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="5" y1="12" x2="19" y2="12" />
                            <circle cx="5" cy="12" r="2" />
                            <circle cx="12" cy="12" r="2" />
                            <circle cx="19" cy="12" r="2" />
                        </svg>
                        Linear
                    </button>
                    <button
                        className={`geometry-btn ${geometry === 'curved' ? 'active' : ''}`}
                        onClick={() => handleGeometryChange('curved')}
                        disabled={isLoading}
                    >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M4 16c0-6 5.5-10 8-10s8 4 8 10" />
                            <circle cx="4" cy="16" r="2" />
                            <circle cx="12" cy="6" r="2" />
                            <circle cx="20" cy="16" r="2" />
                        </svg>
                        Curved
                    </button>
                </div>

                {/* Number of Elements */}
                <div className="parameter-group">
                    <div className="parameter-label">
                        <span>Number of Elements</span>
                        <span className="parameter-value">{numElements}</span>
                    </div>
                    <input
                        type="range"
                        className="parameter-slider"
                        min="4"
                        max="128"
                        step="1"
                        value={numElements}
                        onChange={(e) => handleNumElementsChange(parseInt(e.target.value))}
                        disabled={isLoading}
                    />
                </div>

                {/* Element Spacing */}
                <div className="parameter-group">
                    <div className="parameter-label">
                        <span>Element Spacing (λ)</span>
                        <span className="parameter-value">{elementSpacing.toFixed(2)}</span>
                    </div>
                    <input
                        type="range"
                        className="parameter-slider"
                        min="0.1"
                        max="2.0"
                        step="0.05"
                        value={elementSpacing}
                        onChange={(e) => handleSpacingChange(parseFloat(e.target.value))}
                        disabled={isLoading}
                    />
                </div>

                {/* Curvature Radius (only for curved) */}
                {geometry === 'curved' && (
                    <div className="parameter-group">
                        <div className="parameter-label">
                            <span>Curvature Radius (λ)</span>
                            <span className="parameter-value">{curvatureRadius.toFixed(1)}</span>
                        </div>
                        <input
                            type="range"
                            className="parameter-slider"
                            min="5"
                            max="100"
                            step="1"
                            value={curvatureRadius}
                            onChange={(e) => handleCurvatureChange(parseFloat(e.target.value))}
                            disabled={isLoading}
                        />
                    </div>
                )}

                {/* Phase Shift */}
                <div className="parameter-group">
                    <div className="parameter-label">
                        <span>Phase Shift (°)</span>
                        <span className="parameter-value">{phaseShift.toFixed(0)}°</span>
                    </div>
                    <input
                        type="range"
                        className="parameter-slider"
                        min="-180"
                        max="180"
                        step="1"
                        value={phaseShift}
                        onChange={(e) => handlePhaseShiftChange(parseFloat(e.target.value))}
                        disabled={isLoading}
                    />
                </div>

                {/* Orientation */}
                <div className="parameter-group">
                    <div className="parameter-label">
                        <span>Orientation (°)</span>
                        <span className="parameter-value">{orientation.toFixed(0)}°</span>
                    </div>
                    <input
                        type="range"
                        className="parameter-slider"
                        min="-90"
                        max="90"
                        step="1"
                        value={orientation}
                        onChange={(e) => handleOrientationChange(parseFloat(e.target.value))}
                        disabled={isLoading}
                    />
                </div>

                {/* Position Controls */}
                <div className="parameter-group">
                    <div className="parameter-label">
                        <span>Array Position</span>
                    </div>
                    <div className="position-controls">
                        <div className="position-input-group">
                            <label>X Position</label>
                            <input
                                type="number"
                                className="position-input"
                                value={posX}
                                step="0.1"
                                onChange={(e) => handlePositionChange(parseFloat(e.target.value), posY)}
                                disabled={isLoading}
                            />
                        </div>
                        <div className="position-input-group">
                            <label>Y Position</label>
                            <input
                                type="number"
                                className="position-input"
                                value={posY}
                                step="0.1"
                                onChange={(e) => handlePositionChange(posX, parseFloat(e.target.value))}
                                disabled={isLoading}
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ParameterControls;
