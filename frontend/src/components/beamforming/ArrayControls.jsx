import React from 'react';

const ArrayControls = ({
    arrays,
    selectedArrayId,
    onSelectArray,
    onAddArray,
    onDeleteArray
}) => {
    // Get display name for array
    const getArrayDisplayName = (array, index) => {
        return `Array ${index + 1}`;
    };

    // Get geometry label
    const getGeometryLabel = (geometry) => {
        return geometry === 'curved' ? 'Curved' : 'Linear';
    };

    return (
        <div className="control-section">
            <div className="section-header">
                <h3>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="3" y="3" width="7" height="7" />
                        <rect x="14" y="3" width="7" height="7" />
                        <rect x="14" y="14" width="7" height="7" />
                        <rect x="3" y="14" width="7" height="7" />
                    </svg>
                    Phased Arrays
                </h3>
                <span className="section-badge">
                    {arrays.length} array{arrays.length !== 1 ? 's' : ''}
                </span>
            </div>
            <div className="section-content">
                <div className="array-list">
                    {arrays.map((array, index) => (
                        <div
                            key={array.array_id}
                            className={`array-item ${selectedArrayId === array.array_id ? 'selected' : ''}`}
                            onClick={() => onSelectArray(array.array_id)}
                        >
                            <div className="array-info">
                                <div
                                    className="array-indicator"
                                    style={{
                                        background: index === 0 ? 'var(--accent-primary)' :
                                            index === 1 ? '#00ff88' :
                                                index === 2 ? '#ff8800' : '#ff0088'
                                    }}
                                />
                                <div>
                                    <div className="array-name">{getArrayDisplayName(array, index)}</div>
                                    <div className="array-details">
                                        {array.num_elements} elements · {getGeometryLabel(array.geometry)}
                                    </div>
                                </div>
                            </div>
                            <div className="array-actions">
                                <button
                                    className="array-btn delete"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        onDeleteArray(array.array_id);
                                    }}
                                    title="Delete array"
                                >
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <polyline points="3 6 5 6 21 6" />
                                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    ))}
                </div>

                <button className="add-array-btn" onClick={onAddArray}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="10" />
                        <line x1="12" y1="8" x2="12" y2="16" />
                        <line x1="8" y1="12" x2="16" y2="12" />
                    </svg>
                    Add New Array
                </button>
            </div>
        </div>
    );
};

export default ArrayControls;
