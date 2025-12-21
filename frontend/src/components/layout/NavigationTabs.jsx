import React from 'react'

// Navigation tabs component
const NavigationTabs = ({ activeTab, onTabChange }) => {
    return (
        <nav className="navigation-tabs">
            <button
                className={`nav-tab ${activeTab === 'mixer' ? 'active' : ''}`}
                onClick={() => onTabChange('mixer')}
            >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="tab-icon">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                    <line x1="3" y1="9" x2="21" y2="9" />
                    <line x1="9" y1="21" x2="9" y2="9" />
                </svg>
                FT Magnitude/Phase Mixer
            </button>
            <button
                className={`nav-tab ${activeTab === 'beamforming' ? 'active' : ''}`}
                onClick={() => onTabChange('beamforming')}
            >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="tab-icon">
                    <circle cx="12" cy="12" r="10" />
                    <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
                </svg>
                Beamforming Simulator
            </button>
        </nav>
    )
}

export default NavigationTabs
