import React from 'react';

const ScenarioSelector = ({
    scenarios,
    activeScenario,
    onSelect,
    isLoading
}) => {
    // Icons for different scenario types
    const getScenarioIcon = (scenarioId) => {
        switch (scenarioId) {
            case '5g_mimo':
                return (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M5 12.55a11 11 0 0 1 14.08 0" />
                        <path d="M1.42 9a16 16 0 0 1 21.16 0" />
                        <path d="M8.53 16.11a6 6 0 0 1 6.95 0" />
                        <circle cx="12" cy="20" r="1" />
                    </svg>
                );
            case 'ultrasound_imaging':
                return (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
                    </svg>
                );
            case 'tumor_ablation':
                return (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="10" />
                        <circle cx="12" cy="12" r="6" />
                        <circle cx="12" cy="12" r="2" />
                    </svg>
                );
            default:
                return (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polygon points="12 2 2 7 12 12 22 7 12 2" />
                        <polyline points="2 17 12 22 22 17" />
                        <polyline points="2 12 12 17 22 12" />
                    </svg>
                );
        }
    };

    return (
        <div className="control-section">
            <div className="section-header">
                <h3>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polygon points="12 2 2 7 12 12 22 7 12 2" />
                        <polyline points="2 17 12 22 22 17" />
                        <polyline points="2 12 12 17 22 12" />
                    </svg>
                    Preset Scenarios
                </h3>
                <span className="section-badge">
                    {scenarios.length} available
                </span>
            </div>
            <div className="section-content">
                <div className="scenario-grid">
                    {scenarios.map((scenario) => (
                        <button
                            key={scenario.id}
                            className={`scenario-card ${activeScenario === scenario.id ? 'active' : ''}`}
                            onClick={() => onSelect(scenario.id)}
                            disabled={isLoading}
                        >
                            <div className="scenario-icon">
                                {getScenarioIcon(scenario.id)}
                            </div>
                            <div className="scenario-info">
                                <div className="scenario-name">{scenario.name}</div>
                                <div className="scenario-desc">{scenario.description}</div>
                            </div>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ScenarioSelector;
