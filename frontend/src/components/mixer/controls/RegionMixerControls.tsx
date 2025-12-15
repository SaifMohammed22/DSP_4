import React from 'react'

interface RegionMixerControlsProps {
  regionType: 'full' | 'inner' | 'outer'
  regionSize: number
  onRegionTypeChange: (type: 'full' | 'inner' | 'outer') => void
  onRegionSizeChange: (size: number) => void
}

const RegionMixerControls: React.FC<RegionMixerControlsProps> = ({
  regionType,
  regionSize,
  onRegionTypeChange,
  onRegionSizeChange
}) => {
  return (
    <div className="control-group">
      <div className="control-group-header">
        <h3>Region Selection</h3>
      </div>
      
      <div className="control-item">
        <label>Region Type</label>
        <div className="region-buttons">
          <button 
            className={`region-btn ${regionType === 'full' ? 'active' : ''}`}
            onClick={() => onRegionTypeChange('full')}
          >
            Full
          </button>
          <button 
            className={`region-btn ${regionType === 'inner' ? 'active' : ''}`}
            onClick={() => onRegionTypeChange('inner')}
          >
            Inner
          </button>
          <button 
            className={`region-btn ${regionType === 'outer' ? 'active' : ''}`}
            onClick={() => onRegionTypeChange('outer')}
          >
            Outer
          </button>
        </div>
      </div>

      {regionType !== 'full' && (
        <div className="control-item">
          <label>Region Size</label>
          <div className="slider-row">
            <input 
              type="range"
              min="10"
              max="90"
              value={regionSize}
              onChange={(e) => onRegionSizeChange(parseInt(e.target.value))}
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
