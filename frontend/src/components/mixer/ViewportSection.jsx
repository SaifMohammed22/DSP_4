import React from 'react'
import ImageViewport from './cards/ImageViewport'

const ViewportSection = ({ images, onImageUpload, onBrightnessContrastChange }) => {
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
