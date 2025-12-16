// UI Controls Manager - Handles UI interactions and updates
class UIControls {
    constructor(app) {
        this.app = app;
        this.sliders = new Map();
        this.inputs = new Map();
        this.buttons = new Map();
        
        this.init();
    }
    
    init() {
        console.log('Initializing UI controls...');
        
        // Initialize all controls
        this.initSliders();
        this.initInputs();
        this.initButtons();
        this.initRealTimeUpdates();
        
        console.log('UI controls initialized');
    }
    
    initSliders() {
        // Frequency slider
        this.setupSlider('frequency-slider', (value) => {
            const ghz = value / 1e9;
            document.getElementById('freq-value').textContent = `${ghz.toFixed(2)} GHz`;
            this.app.handleParameterChange('frequency-slider', value);
        });
        
        // Phase shift slider
        this.setupSlider('phase-slider', (value) => {
            document.getElementById('phase-value').textContent = `${value}°`;
            this.app.handleParameterChange('phase-slider', value);
        });
        
        // Curvature slider
        this.setupSlider('curvature-slider', (value) => {
            document.getElementById('curvature-value').textContent = value.toFixed(2);
            this.app.handleParameterChange('curvature-slider', value);
        });
        
        // Elements slider
        this.setupSlider('elements-slider', (value) => {
            document.getElementById('elements-value').textContent = value;
            this.app.handleParameterChange('elements-slider', value);
        });
        
        // Spacing slider
        this.setupSlider('spacing-slider', (value) => {
            document.getElementById('spacing-value').textContent = value.toFixed(2);
            this.app.handleParameterChange('spacing-slider', value);
        });
    }
    
    setupSlider(sliderId, onChange) {
        const slider = document.getElementById(sliderId);
        if (!slider) return;
        
        this.sliders.set(sliderId, slider);
        
        // Set initial value
        const initialValue = parseFloat(slider.value);
        onChange(initialValue);
        
        // Add event listeners
        slider.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            onChange(value);
        });
        
        slider.addEventListener('change', (e) => {
            const value = parseFloat(e.target.value);
            onChange(value);
        });
    }
    
    initInputs() {
        // Transmitter position inputs
        this.setupInput('tx-pos-x', (value) => {
            this.updateTxPositionDisplay();
        });
        
        this.setupInput('tx-pos-y', (value) => {
            this.updateTxPositionDisplay();
        });
    }
    
    setupInput(inputId, onChange) {
        const input = document.getElementById(inputId);
        if (!input) return;
        
        this.inputs.set(inputId, input);
        
        input.addEventListener('change', (e) => {
            const value = parseFloat(e.target.value);
            onChange(value);
        });
        
        input.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            onChange(value);
        });
    }
    
    updateTxPositionDisplay() {
        const x = parseFloat(document.getElementById('tx-pos-x').value) || 0;
        const y = parseFloat(document.getElementById('tx-pos-y').value) || 0;
        document.getElementById('tx-pos-value').textContent = `(${x.toFixed(2)}, ${y.toFixed(2)})`;
    }
    
    initButtons() {
        // Simulation control buttons
        this.setupButton('simulate-btn', () => {
            this.app.runSimulation();
        });
        
        this.setupButton('reset-btn', () => {
            this.app.resetParameters();
        });
        
        this.setupButton('realtime-toggle', () => {
            this.app.toggleRealtimeMode();
        });
        
        this.setupButton('add-array-btn', () => {
            this.app.addArray();
        });
        
        // Export buttons
        this.setupButton('export-btn', () => {
            this.exportConfiguration();
        });
        
        // Help button
        this.setupButton('help-btn', () => {
            this.showHelp();
        });
    }
    
    setupButton(buttonId, onClick) {
        const button = document.getElementById(buttonId);
        if (!button) return;
        
        this.buttons.set(buttonId, button);
        button.addEventListener('click', onClick);
    }
    
    initRealTimeUpdates() {
        // Update UI in real-time based on parameter changes
        setInterval(() => {
            this.updatePerformanceMetrics();
        }, 1000);
    }
    
    updatePerformanceMetrics() {
        // Update CPU load (simulated)
        const cpuLoad = Math.floor(Math.random() * 30) + 5;
        document.getElementById('cpu-load').textContent = `${cpuLoad}%`;
        
        // Update latency
        if (this.app.components.websocketClient.isConnected()) {
            this.app.components.websocketClient.getLatency().then(latency => {
                if (latency) {
                    document.getElementById('sim-latency').textContent = `${latency}ms`;
                }
            });
        }
    }
    
    resetControls() {
        // Reset all sliders to default values
        const defaults = {
            'frequency-slider': 2.4e9,
            'phase-slider': 0,
            'curvature-slider': 0,
            'elements-slider': 8,
            'spacing-slider': 0.5
        };
        
        for (const [sliderId, defaultValue] of Object.entries(defaults)) {
            const slider = this.sliders.get(sliderId);
            if (slider) {
                slider.value = defaultValue;
                slider.dispatchEvent(new Event('input'));
            }
        }
        
        // Reset input fields
        document.getElementById('tx-pos-x').value = 0.1;
        document.getElementById('tx-pos-y').value = 0.0;
        this.updateTxPositionDisplay();
        
        // Reset geometry buttons
        document.querySelectorAll('.geom-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector('[data-geometry="linear"]').classList.add('active');
        
        // Reset curvature control visibility
        document.getElementById('curvature-control').style.display = 'none';
        
        // Reset scenario buttons
        document.querySelectorAll('.scenario-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector('[data-scenario="5g"]').classList.add('active');
        
        console.log('UI controls reset to defaults');
    }
    
    exportConfiguration() {
        const configuration = {
            appState: this.app.state,
            timestamp: new Date().toISOString(),
            version: '1.0.0'
        };
        
        const dataStr = JSON.stringify(configuration, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
        
        const exportFileDefaultName = `beamforming_config_${Date.now()}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
        
        this.app.showNotification('Configuration exported successfully', 'success');
    }
    
    showHelp() {
        // Create help modal
        const helpModal = document.createElement('div');
        helpModal.className = 'modal-overlay active';
        helpModal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <div class="modal-title">
                        <i class="fas fa-question-circle"></i>
                        Beamforming Simulator Help
                    </div>
                    <button class="modal-close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-content">
                    <div class="help-section">
                        <h3><i class="fas fa-cogs"></i> Getting Started</h3>
                        <p>This simulator allows you to visualize beamforming patterns for various array configurations.</p>
                        
                        <h3><i class="fas fa-sliders-h"></i> Parameters</h3>
                        <ul>
                            <li><strong>Frequency:</strong> Operating frequency of the system</li>
                            <li><strong>Phase Shift:</strong> Applied phase shift to array elements</li>
                            <li><strong>Transmitter Position:</strong> Location of signal source</li>
                            <li><strong>Array Geometry:</strong> Layout of array elements (Linear, Curved, Circular)</li>
                            <li><strong>Number of Elements:</strong> Total elements in the array</li>
                            <li><strong>Element Spacing:</strong> Distance between elements in wavelengths</li>
                        </ul>
                        
                        <h3><i class="fas fa-vial"></i> Scenarios</h3>
                        <ul>
                            <li><strong>5G Communication:</strong> Base station with high-frequency beamforming</li>
                            <li><strong>Medical Ultrasound:</strong> Curved array for imaging</li>
                            <li><strong>Tumor Ablation:</strong> Focused ultrasound therapy</li>
                            <li><strong>Radar System:</strong> Target detection and tracking</li>
                        </ul>
                        
                        <h3><i class="fas fa-eye"></i> Visualizations</h3>
                        <ul>
                            <li><strong>Interference Map:</strong> Shows constructive/destructive interference patterns</li>
                            <li><strong>Beam Profile:</strong> Cross-section of beam pattern</li>
                            <li><strong>Array Geometry:</strong> Visual representation of element positions</li>
                            <li><strong>3D Pattern:</strong> Three-dimensional beam pattern visualization</li>
                        </ul>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" id="close-help">Close</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(helpModal);
        
        // Add event listeners
        const closeBtn = helpModal.querySelector('.modal-close');
        const closeHelpBtn = helpModal.querySelector('#close-help');
        
        const closeModal = () => {
            helpModal.classList.remove('active');
            setTimeout(() => {
                helpModal.remove();
            }, 300);
        };
        
        closeBtn.addEventListener('click', closeModal);
        closeHelpBtn.addEventListener('click', closeModal);
        
        helpModal.addEventListener('click', (e) => {
            if (e.target === helpModal) {
                closeModal();
            }
        });
    }
    
    // Utility methods
    showLoading(buttonId) {
        const button = this.buttons.get(buttonId);
        if (button) {
            const originalText = button.innerHTML;
            button.dataset.originalText = originalText;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            button.disabled = true;
        }
    }
    
    hideLoading(buttonId) {
        const button = this.buttons.get(buttonId);
        if (button && button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
            button.disabled = false;
            delete button.dataset.originalText;
        }
    }
    
    updateParameterDisplay(parameter, value) {
        // Update specific parameter displays
        switch (parameter) {
            case 'frequency':
                const slider = this.sliders.get('frequency-slider');
                if (slider) {
                    slider.value = value;
                    slider.dispatchEvent(new Event('input'));
                }
                break;
            // Add more cases as needed
        }
    }
}