import React from 'react'
import ImageViewport from './cards/ImageViewport'
import { ImageData } from '../../App'

interface ViewportSectionProps {
  images: ImageData[]
  onImageUpload: (id: number, file: File) => void
  onBrightnessContrastChange: (id: number, brightness: number, contrast: number) => void
}

const ViewportSection: React.FC<ViewportSectionProps> = ({ images, onImageUpload, onBrightnessContrastChange }) => {
  return (
    <section className="viewport-section">
      <div className="section-header">
        <h2>Input Images</h2>
        <span className="section-badge">4 Viewports</span>
      </div>
      <div className="viewport-grid">
        {images.map(image => (
          <ImageViewport 
            key={image.id}
            image={image}
            onUpload={(file) => onImageUpload(image.id, file)}
            onBrightnessContrastChange={(brightness, contrast) => onBrightnessContrastChange(image.id, brightness, contrast)}
          />
        ))}
      </div>
    </section>
  )
}

export default ViewportSection
