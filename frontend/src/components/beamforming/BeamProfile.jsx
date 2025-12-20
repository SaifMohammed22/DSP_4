import React, { useRef, useEffect, useCallback } from 'react';

const BeamProfile = ({
    fieldData,
    isLoading
}) => {
    const canvasRef = useRef(null);

    // Draw the beam profile
    const drawProfile = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Set canvas size to match container
        const container = canvas.parentElement;
        if (container) {
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
        }

        // Clear canvas
        ctx.fillStyle = '#0a0a0f';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Check if we have beam profile data
        if (fieldData?.beam_profile) {
            const { angles, intensity } = fieldData.beam_profile;
            drawProfileChart(ctx, canvas.width, canvas.height, intensity, angles);
        } else if (fieldData?.intensity && fieldData.intensity.length > 0) {
            // If no explicit beam_profile, create one from the intensity data
            // Take a horizontal slice at the center
            const rows = fieldData.intensity.length;
            const centerRow = Math.floor(rows / 2);
            const profileData = fieldData.intensity[centerRow];

            drawProfileChart(ctx, canvas.width, canvas.height, profileData);
        } else {
            // No data to display
            return;
        }
    }, [fieldData]);

    // Draw the profile chart
    const drawProfileChart = (
        ctx,
        width,
        height,
        data,
        angles
    ) => {
        const padding = { top: 30, right: 20, bottom: 40, left: 50 };
        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;

        // Find min and max
        let minVal = Infinity;
        let maxVal = -Infinity;
        for (const val of data) {
            if (val < minVal) minVal = val;
            if (val > maxVal) maxVal = val;
        }
        const range = maxVal - minVal || 1;

        // Draw grid
        ctx.strokeStyle = '#1e1e28';
        ctx.lineWidth = 1;

        // Horizontal grid lines
        for (let i = 0; i <= 4; i++) {
            const y = padding.top + (i / 4) * chartHeight;
            ctx.beginPath();
            ctx.moveTo(padding.left, y);
            ctx.lineTo(width - padding.right, y);
            ctx.stroke();
        }

        // Vertical grid lines
        for (let i = 0; i <= 6; i++) {
            const x = padding.left + (i / 6) * chartWidth;
            ctx.beginPath();
            ctx.moveTo(x, padding.top);
            ctx.lineTo(x, height - padding.bottom);
            ctx.stroke();
        }

        // Draw axes
        ctx.strokeStyle = '#3e3e4a';
        ctx.lineWidth = 1;

        // Y axis
        ctx.beginPath();
        ctx.moveTo(padding.left, padding.top);
        ctx.lineTo(padding.left, height - padding.bottom);
        ctx.stroke();

        // X axis
        ctx.beginPath();
        ctx.moveTo(padding.left, height - padding.bottom);
        ctx.lineTo(width - padding.right, height - padding.bottom);
        ctx.stroke();

        // Draw the profile line
        ctx.beginPath();
        ctx.strokeStyle = '#6366f1';
        ctx.lineWidth = 2;

        for (let i = 0; i < data.length; i++) {
            const x = padding.left + (i / (data.length - 1)) * chartWidth;
            const normalized = (data[i] - minVal) / range;
            const y = padding.top + (1 - normalized) * chartHeight;

            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }
        ctx.stroke();

        // Draw fill under the curve
        ctx.lineTo(padding.left + chartWidth, height - padding.bottom);
        ctx.lineTo(padding.left, height - padding.bottom);
        ctx.closePath();

        const gradient = ctx.createLinearGradient(0, padding.top, 0, height - padding.bottom);
        gradient.addColorStop(0, 'rgba(99, 102, 241, 0.3)');
        gradient.addColorStop(1, 'rgba(99, 102, 241, 0.05)');
        ctx.fillStyle = gradient;
        ctx.fill();

        // Draw labels
        ctx.fillStyle = '#8b8b99';
        ctx.font = '11px system-ui, -apple-system, sans-serif';
        ctx.textAlign = 'center';

        // X axis labels
        if (angles && angles.length > 0) {
            const xLabels = [
                angles[0].toFixed(0) + '°',
                angles[Math.floor(angles.length / 2)].toFixed(0) + '°',
                angles[angles.length - 1].toFixed(0) + '°'
            ];
            const xPositions = [0, 0.5, 1];

            xPositions.forEach((pos, i) => {
                const x = padding.left + pos * chartWidth;
                ctx.fillText(xLabels[i], x, height - padding.bottom + 20);
            });
        } else {
            // Use position indices
            const xLabels = ['0', Math.floor(data.length / 2).toString(), data.length.toString()];
            const xPositions = [0, 0.5, 1];

            xPositions.forEach((pos, i) => {
                const x = padding.left + pos * chartWidth;
                ctx.fillText(xLabels[i], x, height - padding.bottom + 20);
            });
        }

        // Y axis labels
        ctx.textAlign = 'right';
        for (let i = 0; i <= 4; i++) {
            const val = minVal + ((4 - i) / 4) * range;
            const y = padding.top + (i / 4) * chartHeight;
            ctx.fillText(val.toFixed(1), padding.left - 8, y + 4);
        }

        // Axis titles
        ctx.fillStyle = '#a0a0b0';
        ctx.font = '12px system-ui, -apple-system, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Position', width / 2, height - 8);

        ctx.save();
        ctx.translate(14, height / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.fillText('Intensity', 0, 0);
        ctx.restore();

        // Title
        ctx.fillStyle = '#e0e0e8';
        ctx.font = '13px system-ui, -apple-system, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Beam Profile (Center Slice)', width / 2, 18);
    };

    // Redraw on data change or resize
    useEffect(() => {
        drawProfile();

        const handleResize = () => {
            drawProfile();
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, [drawProfile]);

    return (
        <>
            <canvas ref={canvasRef} className="viz-canvas" />

            {/* Loading overlay */}
            {isLoading && (
                <div className="loading-overlay">
                    <div className="loading-spinner" />
                    <span className="loading-text">Computing profile...</span>
                </div>
            )}

            {/* Placeholder when no data */}
            {!fieldData && !isLoading && (
                <div className="viz-placeholder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
                        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                    </svg>
                    <p>Beam profile will appear here after computing</p>
                </div>
            )}
        </>
    );
};

export default BeamProfile;
