import React from 'react'

const OutputViewport = ({ label, imageUrl }) => {
    return (
        <div className="output-viewport">
            <div className="viewport-header">
                <span className="viewport-title">{label}</span>
            </div>
            <div className="viewport-content">
                {imageUrl ? (
                    <img src={imageUrl} alt={label} />
                ) : (
                    <div className="empty-output">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="empty-icon">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                            <circle cx="8.5" cy="8.5" r="1.5" />
                            <polyline points="21 15 16 10 5 21" />
                        </svg>
                        <p>Output will appear here</p>
                    </div>
                )}
            </div>
        </div>
    )
}

export default OutputViewport
