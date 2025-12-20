import React, { useRef, useEffect, useCallback } from 'react';

const BeamVisualization = ({
    fieldData,
    isLoading
}) => {
    const canvasRef = useRef(null);

    // Color map function (jet-like colormap)
    const getColor = useCallback((value) => {
        // Normalize value between 0 and 1
        const v = Math.max(0, Math.min(1, value));

        let r, g, b;

        if (v < 0.25) {
            // Blue to Cyan
            r = 0;
            g = v * 4;
            b = 1;
        } else if (v < 0.5) {
            // Cyan to Green
            r = 0;
            g = 1;
            b = 1 - (v - 0.25) * 4;
        } else if (v < 0.75) {
            // Green to Yellow
            r = (v - 0.5) * 4;
            g = 1;
            b = 0;
        } else {
            // Yellow to Red
            r = 1;
            g = 1 - (v - 0.75) * 4;
            b = 0;
        }

        return [Math.floor(r * 255), Math.floor(g * 255), Math.floor(b * 255)];
    }, []);

    // Draw the field on canvas
    const drawField = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas || !fieldData) return;

        const container = canvas.parentElement;
        if (container) {
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Clear canvas
        ctx.fillStyle = '#0a0a0f';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const { intensity } = fieldData;
        if (!intensity || !Array.isArray(intensity) || intensity.length === 0) return;

        const rows = intensity.length;
        const cols = Array.isArray(intensity[0]) ? intensity[0].length : 0;

        if (cols === 0) return;

        // Create temporary canvas for the data
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = cols;
        tempCanvas.height = rows;
        const tempCtx = tempCanvas.getContext('2d');
        if (!tempCtx) return;

        const imageData = tempCtx.createImageData(cols, rows);

        // Find min and max for normalization
        let minVal = Infinity;
        let maxVal = -Infinity;

        // First pass: find range
        for (let i = 0; i < rows; i++) {
            for (let j = 0; j < cols; j++) {
                const val = intensity[i][j];
                if (typeof val === 'number' && !isNaN(val)) {
                    if (val < minVal) minVal = val;
                    if (val > maxVal) maxVal = val;
                }
            }
        }

        // Handle uniform or empty data
        if (minVal === Infinity || maxVal === -Infinity) {
            minVal = 0;
            maxVal = 1;
        }

        const range = maxVal - minVal || 1;

        // Second pass: fill data
        for (let i = 0; i < rows; i++) {
            for (let j = 0; j < cols; j++) {
                let val = intensity[i][j];
                let normalized = 0;

                if (typeof val === 'number' && !isNaN(val)) {
                    normalized = (val - minVal) / range;
                }

                const [r, g, b] = getColor(normalized);

                // Index for row i, col j
                const idx = (i * cols + j) * 4;
                imageData.data[idx] = r;
                imageData.data[idx + 1] = g;
                imageData.data[idx + 2] = b;
                imageData.data[idx + 3] = 255;
            }
        }

        tempCtx.putImageData(imageData, 0, 0);

        // Draw scaled to main canvas
        ctx.imageSmoothingEnabled = false; // Use nearest-neighbor to avoid blurring artifacts for now, or true for smooth

        // Calculate fit dimensions
        const dataAspect = cols / rows;
        const canvasAspect = canvas.width / canvas.height;

        let drawWidth, drawHeight, drawX, drawY;

        if (canvasAspect > dataAspect) {
            // Canvas is wider - fit to height
            drawHeight = canvas.height;
            drawWidth = drawHeight * dataAspect;
            drawX = (canvas.width - drawWidth) / 2;
            drawY = 0;
        } else {
            // Canvas is taller - fit to width
            drawWidth = canvas.width;
            drawHeight = drawWidth / dataAspect;
            drawX = 0;
            drawY = (canvas.height - drawHeight) / 2;
        }

        ctx.drawImage(tempCanvas, drawX, drawY, drawWidth, drawHeight);

        // Draw element positions
        if (fieldData.element_positions) {
            drawArrayElements(ctx, fieldData, drawX, drawY, drawWidth, drawHeight);
        }
    }, [fieldData, getColor]);

    const drawArrayElements = (ctx, data, mapX, mapY, mapW, mapH) => {
        if (!data.x_coords || !data.y_coords || data.x_coords.length === 0) return;

        // Determine spatial bounds from the grid coordinates
        const xMin = data.x_coords[0];
        const xMax = data.x_coords[data.x_coords.length - 1];
        const yMin = data.y_coords[0];
        const yMax = data.y_coords[data.y_coords.length - 1];

        const xRange = xMax - xMin || 1;
        const yRange = yMax - yMin || 1;

        data.element_positions.forEach(pos => {
            const [ex, ey] = pos;

            // Map physical coordinates to canvas pixel coordinates
            // Assuming y grows downwards in grid index but upwards physically? 
            // In meshgrid: y increases with index (row).
            // So index 0 is y_min (or y_max depending on linspace).
            // Backend: y = np.linspace(-R, R). Index 0 is -R.

            const px = mapX + ((ex - xMin) / xRange) * mapW;
            const py = mapY + ((ey - yMin) / yRange) * mapH;

            ctx.beginPath();
            ctx.fillStyle = '#ff3333';
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;
            ctx.arc(px, py, 5, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
        });
    };

    // Redraw on data change or resize
    useEffect(() => {
        drawField();

        const handleResize = () => {
            drawField();
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, [drawField]);

    return (
        <>
            <canvas ref={canvasRef} className="viz-canvas" />

            {/* Color scale legend */}
            <div className="color-scale">
                <div className="color-gradient" />
            </div>
            <div className="scale-labels">
                <span>Max</span>
                <span>Min</span>
            </div>

            {/* Loading overlay */}
            {isLoading && (
                <div className="loading-overlay">
                    <div className="loading-spinner" />
                    <span className="loading-text">Computing field...</span>
                </div>
            )}

            {/* Placeholder when no data */}
            {!fieldData && !isLoading && (
                <div className="viz-placeholder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
                        <rect x="3" y="3" width="18" height="18" rx="2" />
                        <circle cx="12" cy="12" r="4" />
                        <path d="M12 2v4M12 18v4M2 12h4M18 12h4" />
                    </svg>
                    <p>Select a scenario or configure an array to view the interference field</p>
                </div>
            )}
        </>
    );
};

export default BeamVisualization;
