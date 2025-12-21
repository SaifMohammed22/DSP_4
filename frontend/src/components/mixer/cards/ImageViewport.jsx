import React, { useState, useRef, useCallback, useEffect } from 'react'

const ImageViewport = ({ image, unifiedRoi, onUpload, onBrightnessContrastChange, onRegionSelect }) => {
    const [viewMode, setViewMode] = useState('magnitude')
    const [isDragging, setIsDragging] = useState(false)
    const [isAdjusting, setIsAdjusting] = useState(false)
    const [isResizing, setIsResizing] = useState(false)
    const [resizeHandle, setResizeHandle] = useState(null)
    const [localBrightness, setLocalBrightness] = useState(image.brightness || 0)
    const [localContrast, setLocalContrast] = useState(image.contrast || 0)
    const fileInputRef = useRef(null)
    const adjustStartRef = useRef(null)
    const ftContainerRef = useRef(null)
    const [isDrawingRoi, setIsDrawingRoi] = useState(false)
    const [roiStart, setRoiStart] = useState(null)

    // ROI Selection/Resizing handlers for FT component
    const handleRoiMouseDown = useCallback((e) => {
        if (!image.file || e.button !== 0 || e.ctrlKey) return

        // Prevent conflict with select menu and other interactive elements
        if (e.target.closest('.panel-label-row') || e.target.tagName === 'SELECT') return

        const imgElement = ftContainerRef.current?.querySelector('img')
        if (!imgElement) return

        const rect = imgElement.getBoundingClientRect()

        // Ensure the initial click is actually within the image area
        if (e.clientX < rect.left || e.clientX > rect.right ||
            e.clientY < rect.top || e.clientY > rect.bottom) {
            // Unless we are clicking a handle, ignore
            if (!e.target.classList.contains('resize-handle')) return
        }

        const x = ((e.clientX - rect.left) / rect.width) * 100
        const y = ((e.clientY - rect.top) / rect.height) * 100

        // Check if clicking a handle
        if (e.target.classList.contains('resize-handle')) {
            e.stopPropagation()
            setIsResizing(true)
            setResizeHandle(e.target.dataset.handle)
            setRoiStart({ x, y, roi: { ...unifiedRoi } })
            return
        }

        setIsDrawingRoi(true)
        setRoiStart({ x, y })
        onRegionSelect({ x, y, width: 0, height: 0 })
    }, [image.file, unifiedRoi, onRegionSelect])

    const handleRoiMouseMove = useCallback((e) => {
        const imgElement = ftContainerRef.current?.querySelector('img')
        if (!imgElement) return
        const rect = imgElement.getBoundingClientRect()
        const currentX = Math.max(0, Math.min(100, ((e.clientX - rect.left) / rect.width) * 100))
        const currentY = Math.max(0, Math.min(100, ((e.clientY - rect.top) / rect.height) * 100))

        if (isDrawingRoi && roiStart) {
            const newRoi = {
                x: Math.min(roiStart.x, currentX),
                y: Math.min(roiStart.y, currentY),
                width: Math.abs(currentX - roiStart.x),
                height: Math.abs(currentY - roiStart.y)
            }
            onRegionSelect(newRoi)
        } else if (isResizing && resizeHandle && roiStart) {
            const dx = currentX - roiStart.x
            const dy = currentY - roiStart.y
            const initialRoi = roiStart.roi
            let newRoi = { ...initialRoi }

            if (resizeHandle.includes('e')) newRoi.width = Math.max(1, initialRoi.width + dx)
            if (resizeHandle.includes('w')) {
                const newWidth = initialRoi.width - dx
                if (newWidth > 1) {
                    newRoi.x = initialRoi.x + dx
                    newRoi.width = newWidth
                }
            }
            if (resizeHandle.includes('s')) newRoi.height = Math.max(1, initialRoi.height + dy)
            if (resizeHandle.includes('n')) {
                const newHeight = initialRoi.height - dy
                if (newHeight > 1) {
                    newRoi.y = initialRoi.y + dy
                    newRoi.height = newHeight
                }
            }
            onRegionSelect(newRoi)
        }
    }, [isDrawingRoi, isResizing, resizeHandle, roiStart, onRegionSelect])

    const handleRoiMouseUp = useCallback(() => {
        setIsDrawingRoi(false)
        setIsResizing(false)
        setResizeHandle(null)
        setRoiStart(null)
    }, [])

    useEffect(() => {
        if (isDrawingRoi || isResizing) {
            window.addEventListener('mouseup', handleRoiMouseUp)
            window.addEventListener('mousemove', handleRoiMouseMove)
            return () => {
                window.removeEventListener('mouseup', handleRoiMouseUp)
                window.removeEventListener('mousemove', handleRoiMouseMove)
            }
        }
    }, [isDrawingRoi, isResizing, handleRoiMouseUp, handleRoiMouseMove])

    // ... rest of the component remains similar ...
    const handleDrop = (e) => {
        e.preventDefault()
        setIsDragging(false)
        const file = e.dataTransfer.files[0]
        if (file && file.type.startsWith('image/')) onUpload(file)
    }

    const handleFileUpload = (e) => {
        const file = e.target.files?.[0]
        if (file) onUpload(file)
    }

    const handleMouseDown = (e) => {
        if (!image.file || !image.originalUrl) return
        if (e.button === 2 || (e.button === 0 && e.ctrlKey)) {
            e.preventDefault()
            setIsAdjusting(true)
            adjustStartRef.current = { x: e.clientX, y: e.clientY, brightness: localBrightness, contrast: localContrast }
        }
    }

    const handleMouseMove = (e) => {
        if (!isAdjusting || !adjustStartRef.current) return
        const deltaX = e.clientX - adjustStartRef.current.x
        const deltaY = e.clientY - adjustStartRef.current.y
        setLocalContrast(Math.max(-100, Math.min(100, adjustStartRef.current.contrast + deltaX * 0.5)))
        setLocalBrightness(Math.max(-100, Math.min(100, adjustStartRef.current.brightness - deltaY * 0.5)))
    }

    const finishAdjustment = () => {
        if (isAdjusting) {
            setIsAdjusting(false)
            onBrightnessContrastChange(localBrightness, localContrast)
        }
    }

    const getFtImageUrl = () => {
        if (!image.file) return null
        switch (viewMode) {
            case 'magnitude': return image.ftMagnitudeUrl
            case 'phase': return image.ftPhaseUrl
            case 'real': return image.ftRealUrl
            case 'imaginary': return image.ftImaginaryUrl
            default: return image.ftMagnitudeUrl
        }
    }

    const ftUrl = getFtImageUrl()

    return (
        <div className="image-viewport compact">
            <div className="viewport-header">
                <span className="viewport-title">Image {image.id}</span>
                {image.file && (
                    <span className="bc-indicator">
                        B:{Math.round(localBrightness)} C:{Math.round(localContrast)}
                    </span>
                )}
            </div>

            <div className="viewport-dual-content">
                <div
                    className={`viewport-panel original-panel ${isDragging ? 'dragging' : ''} ${isAdjusting ? 'adjusting' : ''}`}
                    onDrop={handleDrop}
                    onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                    onDragLeave={() => setIsDragging(false)}
                    onClick={() => !image.file && fileInputRef.current.click()}
                    onMouseDown={handleMouseDown}
                    onMouseMove={handleMouseMove}
                    onMouseUp={finishAdjustment}
                    onMouseLeave={finishAdjustment}
                    onContextMenu={(e) => e.preventDefault()}
                >
                    <div className="panel-label">Original</div>
                    {image.originalUrl ? (
                        <img src={image.originalUrl} alt="Original" draggable={false} />
                    ) : (
                        <div className="upload-placeholder compact">
                            <p>Drop image</p>
                        </div>
                    )}
                </div>

                <div
                    ref={ftContainerRef}
                    className="viewport-panel ft-panel"
                    onMouseDown={handleRoiMouseDown}
                >
                    <div className="panel-label-row">
                        <select
                            className="ft-mode-select"
                            value={viewMode}
                            onChange={(e) => setViewMode(e.target.value)}
                            disabled={!image.file}
                        >
                            <option value="magnitude">Magnitude</option>
                            <option value="phase">Phase</option>
                            <option value="real">Real</option>
                            <option value="imaginary">Imaginary</option>
                        </select>
                    </div>
                    {ftUrl ? (
                        <div className="ft-relative-container">
                            <img src={ftUrl} alt="FT" draggable={false} />
                            {unifiedRoi && (
                                <div
                                    className={`roi-overlay mode-${unifiedRoi.mode}`}
                                    style={{
                                        left: `${unifiedRoi.x}%`,
                                        top: `${unifiedRoi.y}%`,
                                        width: `${unifiedRoi.width}%`,
                                        height: `${unifiedRoi.height}%`
                                    }}
                                >
                                    <div className="resize-handle nw" data-handle="nw"></div>
                                    <div className="resize-handle n" data-handle="n"></div>
                                    <div className="resize-handle ne" data-handle="ne"></div>
                                    <div className="resize-handle w" data-handle="w"></div>
                                    <div className="resize-handle e" data-handle="e"></div>
                                    <div className="resize-handle sw" data-handle="sw"></div>
                                    <div className="resize-handle s" data-handle="s"></div>
                                    <div className="resize-handle se" data-handle="se"></div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="empty-ft-placeholder">FT Component</div>
                    )}
                </div>
            </div>

            <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileUpload} style={{ display: 'none' }} />
        </div>
    )
}

export default ImageViewport
