import React from 'react'
import ComponentMixerControls from './controls/ComponentMixerControls.jsx'
import RegionMixerControls from './controls/RegionMixerControls.jsx'
import OutputControls from './controls/OutputControls.jsx'

const MixerSidebar = ({
    settings,
    onSettingsChange,
    onMix,
    isProcessing,
    images,
    unifiedRoi,
    onRoiChange
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
                    unifiedRoi={unifiedRoi}
                    onRoiChange={onRoiChange}
                />

                <OutputControls
                    outputPort={settings.outputPort}
                    onOutputPortChange={(port) => onSettingsChange({ ...settings, outputPort: port })}
                />

                <div className="mixer-status">
                    {isProcessing ? (
                        <div className="status-syncing">
                            <span className="spinner-small"></span>
                            Updating...
                        </div>
                    ) : (
                        <div className="status-synced">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="sync-icon">
                                <polyline points="20 6 9 17 4 12" />
                            </svg>
                            Live Update Active
                        </div>
                    )}
                </div>
            </div>
        </aside>
    )
}

export default MixerSidebar
