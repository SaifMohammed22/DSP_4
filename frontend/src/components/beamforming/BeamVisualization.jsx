import React, { useRef, useEffect, useCallback } from 'react';

const BeamVisualization = ({ fieldData, isLoading }) => {
    const canvasRef = useRef(null);
    const [viewMode, setViewMode] = React.useState('intensity'); // Default to intensity for clearer beam

    // Diverging Red-Blue for interference
    const getInterferenceColor = useCallback((value) => {
        const v = Math.max(0, Math.min(1, value));
        // Diverging: blue at 0, black/dark at 0.5, red at 1
        if (v < 0.5) {
            // Map 0 -> 0.5 to Blue -> Dark
            const factor = v * 2;
            return [0, 0, Math.floor(255 * (1 - factor))];
        } else {
            // Map 0.5 -> 1 to Dark -> Red
            const factor = (v - 0.5) * 2;
            return [Math.floor(255 * factor), 0, 0];
        }
    }, []);

    // Heat colormap for Intensity (Black -> Orange -> Yellow -> White)
    const getIntensityColor = useCallback((value) => {
        const v = Math.max(0, Math.min(1, value));

        let r = 0, g = 0, b = 0;

        if (v < 0.33) {
            // Black to Red
            r = Math.floor((v / 0.33) * 255);
        } else if (v < 0.66) {
            // Red to Orange/Yellow
            r = 255;
            g = Math.floor(((v - 0.33) / 0.33) * 200);
        } else {
            // Yellow to White
            r = 255;
            g = 200 + Math.floor(((v - 0.66) / 0.34) * 55);
            b = Math.floor(((v - 0.66) / 0.34) * 255);
        }

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

        ctx.fillStyle = '#0a0a0f';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const data = viewMode === 'interference' ? fieldData?.interference : fieldData?.intensity;
        if (!data || !Array.isArray(data) || data.length === 0) return;

        const rows = data.length;
        const cols = data[0]?.length || 0;
        if (cols === 0) return;

        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = cols;
        tempCanvas.height = rows;
        const tempCtx = tempCanvas.getContext('2d');
        if (!tempCtx) return;

        const imageData = tempCtx.createImageData(cols, rows);

        for (let i = 0; i < rows; i++) {
            for (let j = 0; j < cols; j++) {
                const val = data[i][j];
                const [r, g, b] = viewMode === 'interference' ? getInterferenceColor(val) : getIntensityColor(val);
                const idx = (i * cols + j) * 4;
                imageData.data[idx] = r;
                imageData.data[idx + 1] = g;
                imageData.data[idx + 2] = b;
                imageData.data[idx + 3] = 255;
            }
        }

        tempCtx.putImageData(imageData, 0, 0);

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

        ctx.imageSmoothingEnabled = true;
        ctx.drawImage(tempCanvas, drawX, drawY, drawWidth, drawHeight);

        // Draw element positions
        if (fieldData.element_positions && fieldData.x_coords && fieldData.y_coords) {
            const xMin = fieldData.x_coords[0];
            const xMax = fieldData.x_coords[fieldData.x_coords.length - 1];
            const yMin = fieldData.y_coords[0];
            const yMax = fieldData.y_coords[fieldData.y_coords.length - 1];
            const xRange = xMax - xMin || 1;
            const yRange = yMax - yMin || 1;

            ctx.fillStyle = '#10b981'; // Emerald
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 1;

            fieldData.element_positions.forEach(pos => {
                const [ex, ey] = pos;
                const px = drawX + ((ex - xMin) / xRange) * drawWidth;
                const py = drawY + ((ey - yMin) / yRange) * drawHeight;

                ctx.beginPath();
                ctx.arc(px, py, 3, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();
            });
        }
    }, [fieldData, viewMode, getInterferenceColor, getIntensityColor]);

    useEffect(() => {
        drawField();
        const handleResize = () => drawField();
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, [drawField]);

    return (
        <div className="viz-container-inner">
            <div className="viz-controls">
                <button
                    className={viewMode === 'intensity' ? 'active' : ''}
                    onClick={() => setViewMode('intensity')}
                >
                    Beam Intensity
                </button>
                <button
                    className={viewMode === 'interference' ? 'active' : ''}
                    onClick={() => setViewMode('interference')}
                >
                    Wave Phase
                </button>
            </div>

            <canvas ref={canvasRef} className="viz-canvas" />

            <div className={`color-scale ${viewMode}`}>
                <div className="color-gradient" />
                <div className="scale-labels">
                    <span>Low</span>
                    <span>High</span>
                </div>
            </div>

            {isLoading && (
                <div className="loading-overlay">
                    <div className="loading-spinner" />
                </div>
            )}

            {!fieldData && !isLoading && (
                <div className="viz-placeholder">
                    <p>Interference map</p>
                </div>
            )}
        </div>
    );
};

export default BeamVisualization;
