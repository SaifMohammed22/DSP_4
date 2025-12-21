import React from 'react'

const RegionMixerControls = ({
    regionType,
    regionSize,
    onRegionTypeChange,
    onRegionSizeChange,
    unifiedRoi,
    onRoiChange
}) => {
    const handleModeChange = (mode) => {
        onRoiChange({ mode })
    }

    const handleSizeSliderChange = (sizePercent) => {
        onRegionSizeChange(sizePercent)
        // Adjust width and height based on the slider, centered
        const size = sizePercent / 100 // 0.1 to 0.9
        const width = size * 100
        const height = size * 100
        const x = 50 - width / 2
        const y = 50 - height / 2
        onRoiChange({ x, y, width, height })
    }

    return (
        <div className="control-group">
            <div className="control-group-header">
                <h3>Region Selection</h3>
            </div>

            <div className="control-item">
                <label>Selection Shape</label>
                <div className="region-buttons">
                    <button
                        className={`region-btn ${regionType === 'full' ? 'active' : ''}`}
                        onClick={() => onRegionTypeChange('full')}
                    >
                        Full
                    </button>
                    <button
                        className={`region-btn ${regionType === 'rectangle' ? 'active' : ''}`}
                        onClick={() => onRegionTypeChange('rectangle')}
                    >
                        Rectangle
                    </button>
                    {/* Keep legacy for backwards compatibility if needed, or remove */}
                    <button
                        className={`region-btn ${['inner', 'outer'].includes(regionType) ? 'active' : ''}`}
                        onClick={() => onRegionTypeChange('inner')}
                    >
                        Circular
                    </button>
                </div>
            </div>

            {regionType === 'rectangle' && (
                <div className="control-item">
                    <label>Selection Mode</label>
                    <div className="region-buttons">
                        <button
                            className={`region-btn ${unifiedRoi.mode === 'inner' ? 'active' : ''}`}
                            onClick={() => handleModeChange('inner')}
                        >
                            Inside
                        </button>
                        <button
                            className={`region-btn ${unifiedRoi.mode === 'outer' ? 'active' : ''}`}
                            onClick={() => handleModeChange('outer')}
                        >
                            Outside
                        </button>
                    </div>
                </div>
            )}

            {(regionType !== 'full') && (
                <div className="control-item">
                    <label>Region Size</label>
                    <div className="slider-row">
                        <input
                            type="range"
                            min="10"
                            max="95"
                            value={regionSize}
                            onChange={(e) => handleSizeSliderChange(parseInt(e.target.value))}
                            className="control-slider"
                        />
                        <span className="slider-value">{regionSize}%</span>
                    </div>
                </div>
            )}
        </div>
    )
}

export default RegionMixerControls
