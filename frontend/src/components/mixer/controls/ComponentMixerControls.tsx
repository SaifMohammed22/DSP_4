import React from 'react'
import { ImageData } from '../../../App'

interface ComponentMixerControlsProps {
  weights: { [key: number]: number }
  selectedComponent: 'magnitude' | 'phase' | 'real' | 'imaginary'
  onWeightsChange: (weights: { [key: number]: number }) => void
  onComponentChange: (component: 'magnitude' | 'phase' | 'real' | 'imaginary') => void
  images: ImageData[]
}

const ComponentMixerControls: React.FC<ComponentMixerControlsProps> = ({
  weights,
  selectedComponent,
  onWeightsChange,
  onComponentChange,
  images
}) => {
  const handleWeightChange = (id: number, value: number) => {
    onWeightsChange({ ...weights, [id]: value })
  }

  return (
    <div className="control-group">
      <div className="control-group-header">
        <h3>Component Mixer</h3>
      </div>
      
      <div className="control-item">
        <label>FT Component</label>
        <select 
          value={selectedComponent}
          onChange={(e) => onComponentChange(e.target.value as any)}
          className="control-select"
        >
          <option value="magnitude">Magnitude</option>
          <option value="phase">Phase</option>
          <option value="real">Real</option>
          <option value="imaginary">Imaginary</option>
        </select>
      </div>

      <div className="control-item">
        <label>Image Weights</label>
        <div className="weight-sliders">
          {images.map(image => (
            <div key={image.id} className="weight-slider-row">
              <span className="weight-label">
                Image {image.id}
                {!image.file && <span className="inactive-badge">Empty</span>}
              </span>
              <input 
                type="range"
                min="0"
                max="100"
                value={weights[image.id]}
                onChange={(e) => handleWeightChange(image.id, parseInt(e.target.value))}
                className="weight-slider"
                disabled={!image.file}
              />
              <span className="weight-value">{weights[image.id]}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ComponentMixerControls
