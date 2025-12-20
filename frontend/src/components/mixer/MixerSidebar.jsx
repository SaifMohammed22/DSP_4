import React from 'react'
import ComponentMixerControls from './controls/ComponentMixerControls.jsx'
import RegionMixerControls from './controls/RegionMixerControls.jsx'
import OutputControls from './controls/OutputControls.jsx'

const MixerSidebar = ({
    settings,
    onSettingsChange,
    onMix,
    isProcessing,
    images
}) => {
    return (
        <aside className="mixer-sidebar">
            <div className="sidebar-header">
                <h2>Mixer Controls</h2>
            </div>

            <div className="sidebar-content">
                <ComponentMixerControls
                    weights={settings.componentWeights}
                    selectedComponent={settings.selectedComponent}
                    onWeightsChange={(weights) => onSettingsChange({ ...settings, componentWeights: weights })}
                    onComponentChange={(component) => onSettingsChange({ ...settings, selectedComponent: component })}
                    images={images}
                />

                <RegionMixerControls
                    regionType={settings.regionType}
                    regionSize={settings.regionSize}
                    onRegionTypeChange={(type) => onSettingsChange({ ...settings, regionType: type })}
                    onRegionSizeChange={(size) => onSettingsChange({ ...settings, regionSize: size })}
                />

                <OutputControls
                    outputPort={settings.outputPort}
                    onOutputPortChange={(port) => onSettingsChange({ ...settings, outputPort: port })}
                />

                <button
                    className="mix-button"
                    onClick={onMix}
                    disabled={isProcessing || images.every(img => img.file === null)}
                >
                    {isProcessing ? (
                        <>
                            <span className="spinner"></span>
                            Processing...
                        </>
                    ) : (
                        <>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mix-icon">
                                <polygon points="5 3 19 12 5 21 5 3" />
                            </svg>
                            Mix Images
                        </>
                    )}
                </button>
            </div>
        </aside>
    )
}

export default MixerSidebar
