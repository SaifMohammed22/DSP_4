import React, { useState, useRef } from 'react'
import { ImageData } from '../../../App'

interface ImageViewportProps {
  image: ImageData
  onUpload: (file: File) => void
  onBrightnessContrastChange: (brightness: number, contrast: number) => void
}

type ViewMode = 'original' | 'magnitude' | 'phase' | 'real' | 'imaginary'

const ImageViewport: React.FC<ImageViewportProps> = ({ image, onUpload, onBrightnessContrastChange }) => {
  const [viewMode, setViewMode] = useState<ViewMode>('original')
  const [isDragging, setIsDragging] = useState(false)
  const [isAdjusting, setIsAdjusting] = useState(false)
  const [localBrightness, setLocalBrightness] = useState(image.brightness || 0)
  const [localContrast, setLocalContrast] = useState(image.contrast || 0)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const adjustStartRef = useRef<{ x: number; y: number; brightness: number; contrast: number } | null>(null)

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file && file.type.startsWith('image/')) {
      onUpload(file)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      onUpload(file)
    }
  }

  // Mouse drag for brightness/contrast adjustment
  const handleMouseDown = (e: React.MouseEvent) => {
    if (!image.file || !image.originalUrl) return
    
    // Only adjust on right click or ctrl+left click
    if (e.button === 2 || (e.button === 0 && e.ctrlKey)) {
      e.preventDefault()
      setIsAdjusting(true)
      adjustStartRef.current = {
        x: e.clientX,
        y: e.clientY,
        brightness: localBrightness,
        contrast: localContrast
      }
    }
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isAdjusting || !adjustStartRef.current) return
    
    const deltaX = e.clientX - adjustStartRef.current.x
    const deltaY = e.clientY - adjustStartRef.current.y
    
    // Horizontal movement controls contrast, vertical controls brightness
    const newContrast = Math.max(-100, Math.min(100, adjustStartRef.current.contrast + deltaX * 0.5))
    const newBrightness = Math.max(-100, Math.min(100, adjustStartRef.current.brightness - deltaY * 0.5))
    
    setLocalContrast(newContrast)
    setLocalBrightness(newBrightness)
  }

  const handleMouseUp = () => {
    if (isAdjusting) {
      setIsAdjusting(false)
      onBrightnessContrastChange(localBrightness, localContrast)
    }
  }

  const handleContextMenu = (e: React.MouseEvent) => {
    if (image.file) {
      e.preventDefault()
    }
  }

  const handleDoubleClick = () => {
    if (image.file) {
      fileInputRef.current?.click()
    }
  }

  const getCurrentImageUrl = (): string | null => {
    switch (viewMode) {
      case 'original': return image.originalUrl
      case 'magnitude': return image.ftMagnitudeUrl
      case 'phase': return image.ftPhaseUrl
      case 'real': return image.ftRealUrl
      case 'imaginary': return image.ftImaginaryUrl
      default: return image.originalUrl
    }
  }

  const currentUrl = getCurrentImageUrl()

  return (
    <div className="image-viewport">
      <div className="viewport-header">
        <span className="viewport-title">Image {image.id}</span>
        {image.file && (
          <span className="bc-indicator" title="Brightness / Contrast">
            B:{Math.round(localBrightness)} C:{Math.round(localContrast)}
          </span>
        )}
        <select 
          className="view-mode-select"
          value={viewMode}
          onChange={(e) => setViewMode(e.target.value as ViewMode)}
          disabled={!image.file}
        >
          <option value="original">Original</option>
          <option value="magnitude">FT Magnitude</option>
          <option value="phase">FT Phase</option>
          <option value="real">FT Real</option>
          <option value="imaginary">FT Imaginary</option>
        </select>
      </div>
      
      <div 
        className={`viewport-content ${isDragging ? 'dragging' : ''} ${isAdjusting ? 'adjusting' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={!image.file ? handleClick : undefined}
        onDoubleClick={handleDoubleClick}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onContextMenu={handleContextMenu}
      >
        {currentUrl ? (
          <img 
            src={currentUrl} 
            alt={`Image ${image.id} - ${viewMode}`} 
            draggable={false}
          />
        ) : (
          <div className="upload-placeholder">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="upload-icon">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            <p>Drop image here or click to upload</p>
            <p className="hint">Right-click + drag to adjust brightness/contrast</p>
          </div>
        )}
        <input 
          ref={fileInputRef}
          type="file" 
          accept="image/*"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
      </div>
    </div>
  )
}

export default ImageViewport
