import React, { useRef, useEffect, useCallback } from 'react';

const BeamVisualization = ({ fieldData, isLoading }) => {
    const canvasRef = useRef(null);

    // Red-Blue interference colormap (like reference app)
    const getColor = useCallback((value) => {
        // value is 0 to 1, normalized
        // 0 = blue (destructive), 0.5 = middle, 1 = red (constructive)
        const v = Math.max(0, Math.min(1, value));

        // Simple red-blue diverging: blue at low, red at high
        const r = Math.floor(255 * v);
        const g = 0;
        const b = Math.floor(255 * (1 - v));

        return [r, g, b];
    }, []);

    const drawField = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const container = canvas.parentElement;
        if (container) {
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Clear with dark background
        ctx.fillStyle = '#0a0a0f';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        if (!fieldData?.intensity) return;

        const { intensity } = fieldData;
        if (!Array.isArray(intensity) || intensity.length === 0) return;

        const rows = intensity.length;
        const cols = intensity[0]?.length || 0;
        if (cols === 0) return;

        // Create off-screen canvas for the heatmap
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = cols;
        tempCanvas.height = rows;
        const tempCtx = tempCanvas.getContext('2d');
        if (!tempCtx) return;

        const imageData = tempCtx.createImageData(cols, rows);

        // Fill image data
        for (let i = 0; i < rows; i++) {
            for (let j = 0; j < cols; j++) {
                const val = intensity[i][j];
                const [r, g, b] = getColor(val);
                const idx = (i * cols + j) * 4;
                imageData.data[idx] = r;
                imageData.data[idx + 1] = g;
                imageData.data[idx + 2] = b;
                imageData.data[idx + 3] = 255;
            }
        }

        tempCtx.putImageData(imageData, 0, 0);

        // Calculate drawing dimensions maintaining aspect ratio
        const dataAspect = cols / rows;
        const canvasAspect = canvas.width / canvas.height;

        let drawWidth, drawHeight, drawX, drawY;

        if (canvasAspect > dataAspect) {
            drawHeight = canvas.height;
            drawWidth = drawHeight * dataAspect;
            drawX = (canvas.width - drawWidth) / 2;
            drawY = 0;
        } else {
            drawWidth = canvas.width;
            drawHeight = drawWidth / dataAspect;
            drawX = 0;
            drawY = (canvas.height - drawHeight) / 2;
        }

        // Draw scaled heatmap
        ctx.imageSmoothingEnabled = true;
        ctx.drawImage(tempCanvas, drawX, drawY, drawWidth, drawHeight);

        // Draw element positions as green dots
        if (fieldData.element_positions && fieldData.x_coords && fieldData.y_coords) {
            const xMin = fieldData.x_coords[0];
            const xMax = fieldData.x_coords[fieldData.x_coords.length - 1];
            const yMin = fieldData.y_coords[0];
            const yMax = fieldData.y_coords[fieldData.y_coords.length - 1];
            const xRange = xMax - xMin || 1;
            const yRange = yMax - yMin || 1;

            ctx.fillStyle = '#00ff00';
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;

            fieldData.element_positions.forEach(pos => {
                const [ex, ey] = pos;
                const px = drawX + ((ex - xMin) / xRange) * drawWidth;
                const py = drawY + ((ey - yMin) / yRange) * drawHeight;

                ctx.beginPath();
                ctx.arc(px, py, 5, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();
            });
        }
    }, [fieldData, getColor]);

    useEffect(() => {
        drawField();

        const handleResize = () => drawField();
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

            {isLoading && (
                <div className="loading-overlay">
                    <div className="loading-spinner" />
                    <span className="loading-text">Computing...</span>
                </div>
            )}

            {!fieldData && !isLoading && (
                <div className="viz-placeholder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
                        <rect x="3" y="3" width="18" height="18" rx="2" />
                        <circle cx="12" cy="12" r="4" />
                    </svg>
                    <p>Interference map</p>
                </div>
            )}
        </>
    );
};

export default BeamVisualization;
