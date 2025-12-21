import React, { useRef, useEffect, useCallback } from 'react';

const BeamProfile = ({ fieldData, isLoading }) => {
    const canvasRef = useRef(null);

    const drawProfile = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const container = canvas.parentElement;
        if (container) {
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Clear
        ctx.fillStyle = '#0a0a0f';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Check for beam profile data
        const profile = fieldData?.beam_profile;
        if (!profile?.angles || !profile?.intensity) return;

        const { angles, intensity } = profile;
        if (angles.length === 0) return;

        // Center and radius for polar plot
        const centerX = canvas.width / 2;
        const centerY = canvas.height - 40;  // Near bottom
        const maxRadius = Math.min(canvas.width / 2 - 40, canvas.height - 80);

        // Draw grid circles
        ctx.strokeStyle = '#1e1e28';
        ctx.lineWidth = 1;

        for (let r = 0.25; r <= 1; r += 0.25) {
            ctx.beginPath();
            ctx.arc(centerX, centerY, maxRadius * r, Math.PI, 0);
            ctx.stroke();
        }

        // Draw angle lines
        for (let deg = -90; deg <= 90; deg += 30) {
            const rad = (deg * Math.PI) / 180;
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(
                centerX + maxRadius * Math.cos(rad - Math.PI / 2),
                centerY + maxRadius * Math.sin(rad - Math.PI / 2)
            );
            ctx.stroke();
        }

        // Draw baseline
        ctx.beginPath();
        ctx.moveTo(centerX - maxRadius, centerY);
        ctx.lineTo(centerX + maxRadius, centerY);
        ctx.stroke();

        // Draw angle labels
        ctx.fillStyle = '#808090';
        ctx.font = '11px system-ui';
        ctx.textAlign = 'center';

        [-90, -60, -30, 0, 30, 60, 90].forEach(deg => {
            const rad = (deg * Math.PI) / 180;
            const labelRadius = maxRadius + 18;
            const x = centerX + labelRadius * Math.cos(rad - Math.PI / 2);
            const y = centerY + labelRadius * Math.sin(rad - Math.PI / 2);
            ctx.fillText(`${deg}°`, x, y + 4);
        });

        // Draw beam pattern
        ctx.beginPath();
        ctx.strokeStyle = '#6366f1';
        ctx.lineWidth = 2;

        let firstPoint = true;
        for (let i = 0; i < angles.length; i++) {
            const deg = angles[i];
            // Only show front hemisphere (-90 to 90)
            if (deg < -90 || deg > 90) continue;

            const rad = (deg * Math.PI) / 180;
            const r = intensity[i] * maxRadius;

            const x = centerX + r * Math.cos(rad - Math.PI / 2);
            const y = centerY + r * Math.sin(rad - Math.PI / 2);

            if (firstPoint) {
                ctx.moveTo(x, y);
                firstPoint = false;
            } else {
                ctx.lineTo(x, y);
            }
        }
        ctx.stroke();

        // Fill under curve
        ctx.lineTo(centerX, centerY);
        ctx.closePath();

        const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, maxRadius);
        gradient.addColorStop(0, 'rgba(99, 102, 241, 0.3)');
        gradient.addColorStop(1, 'rgba(99, 102, 241, 0.05)');
        ctx.fillStyle = gradient;
        ctx.fill();

        // Draw center point
        ctx.beginPath();
        ctx.fillStyle = '#6366f1';
        ctx.arc(centerX, centerY, 4, 0, Math.PI * 2);
        ctx.fill();

    }, [fieldData]);

    useEffect(() => {
        drawProfile();

        const handleResize = () => drawProfile();
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, [drawProfile]);

    return (
        <>
            <canvas ref={canvasRef} className="viz-canvas" />

            {isLoading && (
                <div className="loading-overlay">
                    <div className="loading-spinner" />
                    <span className="loading-text">Computing...</span>
                </div>
            )}

            {!fieldData?.beam_profile && !isLoading && (
                <div className="viz-placeholder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
                        <circle cx="12" cy="12" r="10" />
                        <path d="M12 2a10 10 0 0 1 0 20" />
                    </svg>
                    <p>Beam profile</p>
                </div>
            )}
        </>
    );
};

export default BeamProfile;
