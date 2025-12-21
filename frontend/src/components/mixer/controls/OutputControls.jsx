import React from 'react'

const OutputControls = ({
    outputPort,
    onOutputPortChange
}) => {
    return (
        <div className="control-group">
            <div className="control-group-header">
                <h3>Output Settings</h3>
            </div>

            <div className="control-item">
                <label>Output Port</label>
                <div className="output-buttons">
                    <button
                        className={`output-btn ${outputPort === 1 ? 'active' : ''}`}
                        onClick={() => onOutputPortChange(1)}
                    >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="btn-icon">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                        </svg>
                        Output 1
                    </button>
                    <button
                        className={`output-btn ${outputPort === 2 ? 'active' : ''}`}
                        onClick={() => onOutputPortChange(2)}
                    >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="btn-icon">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                        </svg>
                        Output 2
                    </button>
                </div>
            </div>
        </div>
    )
}

export default OutputControls
