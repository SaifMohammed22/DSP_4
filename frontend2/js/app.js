// Main Application Entry Point
class BeamformingApp {
    constructor() {
        this.config = {
            backendUrl: 'http://localhost:5000',
            socketPath: '/socket.io',
            realtimeUpdate: true,
            updateInterval: 100, // ms
            maxArrays: 10
        };
        
        this.state = {
            currentMode: 'transmission',
            parameters: {
                frequency: 2.4e9,
                phaseShift: 0,
                txPosition: { x: 0.1, y: 0.0 },
                arrayGeometry: 'linear',
                curvature: 0.0,
                numElements: 8,
                elementSpacing: 0.5,
                steeringAngle: 0,
                propagationSpeed: 3e8
            },
            arrays: [
                {
                    id: 'array-1',
                    name: 'Array 1',
                    type: 'linear',
                    numElements: 8,
                    spacing: 0.5,
                    position: { x: 0, y: 0 },
                    orientation: 0,
                    active: true
                }
            ],
            activeScenario: '5g',
            simulationRunning: false,
            realtimeMode: false,
            connectionStatus: 'disconnected'
        };
        
        this.components = {
            uiControls: null,
            visualization: null,
            beamformingEngine: null,
            websocketClient: null
        };
        
        this.init();
    }
    
    async init() {
        console.log('Initializing Beamforming Simulator...');
        
        try {
            // Initialize components
            this.components.uiControls = new UIControls(this);
            this.components.visualization = new Visualization(this);
            this.components.beamformingEngine = new BeamformingEngine(this);
            this.components.websocketClient = new WebSocketClient(this);
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Connect to backend
            await this.components.websocketClient.connect();
            
            // Load initial scenario
            await this.loadScenario('5g');
            
            // Initialize visualization
            await this.components.visualization.init();
            
            console.log('Beamforming Simulator initialized successfully');
            
            // Start update loop
            this.startUpdateLoop();
            
        } catch (error) {
            console.error('Failed to initialize application:', error);
            this.showError('Initialization Error', error.message);
        }
    }
    
    setupEventListeners() {
        // Mode selection
        document.querySelectorAll('.mode-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const mode = e.currentTarget.dataset.mode;
                this.setMode(mode);
            });
        });
        
        // Parameter sliders
        document.querySelectorAll('.parameter-slider').forEach(slider => {
            slider.addEventListener('input', (e) => {
                this.handleParameterChange(e.target.id, parseFloat(e.target.value));
            });
        });
        
        // Vector controls
        document.querySelectorAll('.vector-control').forEach(input => {
            input.addEventListener('change', (e) => {
                const id = e.target.id;
                const value = parseFloat(e.target.value);
                
                if (id.includes('tx-pos')) {
                    const axis = id.includes('x') ? 'x' : 'y';
                    this.updateParameter('txPosition', { ...this.state.parameters.txPosition, [axis]: value });
                }
            });
        });
        
        // Geometry buttons
        document.querySelectorAll('.geom-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const geometry = e.currentTarget.dataset.geometry;
                this.updateParameter('arrayGeometry', geometry);
                
                // Update UI
                document.querySelectorAll('.geom-btn').forEach(b => b.classList.remove('active'));
                e.currentTarget.classList.add('active');
                
                // Show/hide curvature control
                const curvatureControl = document.getElementById('curvature-control');
                curvatureControl.style.display = geometry === 'curved' ? 'flex' : 'none';
            });
        });
        
        // Scenario buttons
        document.querySelectorAll('.scenario-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const scenario = e.currentTarget.dataset.scenario;
                await this.loadScenario(scenario);
            });
        });
        
        // Control buttons
        document.getElementById('simulate-btn').addEventListener('click', () => {
            this.runSimulation();
        });
        
        document.getElementById('reset-btn').addEventListener('click', () => {
            this.resetParameters();
        });
        
        document.getElementById('realtime-toggle').addEventListener('click', () => {
            this.toggleRealtimeMode();
        });
        
        document.getElementById('add-array-btn').addEventListener('click', () => {
            this.addArray();
        });
        
        // Visualization tabs
        document.querySelectorAll('.viz-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const vizType = e.currentTarget.dataset.viz;
                this.setActiveVisualization(vizType);
            });
        });
    }
    
    setMode(mode) {
        this.state.currentMode = mode;
        
        // Update UI
        document.querySelectorAll('.mode-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.mode === mode);
        });
        
        // Update parameter visibility based on mode
        this.updateModeSpecificControls();
        
        console.log(`Mode changed to: ${mode}`);
    }
    
    updateModeSpecificControls() {
        // This would show/hide controls based on mode
        // For now, just log it
        console.log(`Updating controls for ${this.state.currentMode} mode`);
    }
    
    handleParameterChange(parameterId, value) {
        const parameterMap = {
            'frequency-slider': 'frequency',
            'phase-slider': 'phaseShift',
            'curvature-slider': 'curvature',
            'elements-slider': 'numElements',
            'spacing-slider': 'elementSpacing'
        };
        
        const parameterName = parameterMap[parameterId];
        if (parameterName) {
            this.updateParameter(parameterName, value);
            
            // Update value display
            this.updateValueDisplay(parameterId, value);
        }
    }
    
    updateParameter(name, value) {
        // Update state
        this.state.parameters[name] = value;
        
        // If realtime mode is on, trigger immediate update
        if (this.state.realtimeMode && !this.state.simulationRunning) {
            this.scheduleUpdate();
        }
        
        // Update backend if connected
        if (this.components.websocketClient.isConnected()) {
            this.components.websocketClient.sendParameterUpdate(name, value);
        }
    }
    
    updateValueDisplay(elementId, value) {
        const displayMap = {
            'frequency-slider': (v) => `${(v / 1e9).toFixed(2)} GHz`,
            'phase-slider': (v) => `${v.toFixed(0)}°`,
            'curvature-slider': (v) => v.toFixed(2),
            'elements-slider': (v) => v.toString(),
            'spacing-slider': (v) => v.toFixed(2)
        };
        
        const displayFn = displayMap[elementId];
        if (displayFn) {
            const displayElement = document.getElementById(elementId.replace('-slider', '-value'));
            if (displayElement) {
                displayElement.textContent = displayFn(value);
            }
        }
    }
    
    async loadScenario(scenarioName) {
        console.log(`Loading scenario: ${scenarioName}`);
        
        this.showProgress(0, `Loading ${scenarioName} scenario...`);
        
        try {
            // Update UI
            document.querySelectorAll('.scenario-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.scenario === scenarioName);
            });
            
            this.state.activeScenario = scenarioName;
            
            // Update scenario info
            const scenarioInfo = {
                '5g': {
                    title: '5G Base Station Scenario',
                    description: 'Frequency: 3.5 GHz, Elements: 32, Linear Array'
                },
                'ultrasound': {
                    title: 'Medical Ultrasound Scenario',
                    description: 'Frequency: 5 MHz, Elements: 64, Curved Array'
                },
                'tumor-ablation': {
                    title: 'Tumor Ablation Scenario',
                    description: 'Frequency: 1 MHz, Elements: 256, Circular Array'
                },
                'radar': {
                    title: 'Radar System Scenario',
                    description: 'Frequency: 10 GHz, Elements: 16, Linear Array'
                }
            };
            
            const info = scenarioInfo[scenarioName];
            const infoElement = document.getElementById('scenario-info');
            infoElement.innerHTML = `
                <h4>${info.title}</h4>
                <p>${info.description}</p>
            `;
            
            // Load scenario parameters from backend
            if (this.components.websocketClient.isConnected()) {
                await this.components.websocketClient.loadScenario(scenarioName);
            }
            
            this.showProgress(100, 'Scenario loaded successfully');
            
            setTimeout(() => {
                this.hideProgress();
            }, 1000);
            
        } catch (error) {
            console.error('Failed to load scenario:', error);
            this.showError('Scenario Load Error', error.message);
        }
    }
    
    async runSimulation() {
        if (this.state.simulationRunning) return;
        
        console.log('Starting simulation...');
        
        this.state.simulationRunning = true;
        const simulateBtn = document.getElementById('simulate-btn');
        simulateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';
        simulateBtn.disabled = true;
        
        this.showProgress(0, 'Initializing simulation...');
        
        try {
            // Send simulation request to backend
            const simulationData = {
                parameters: this.state.parameters,
                arrays: this.state.arrays,
                scenario: this.state.activeScenario,
                mode: this.state.currentMode
            };
            
            // Use WebSocket for real-time updates
            if (this.components.websocketClient.isConnected()) {
                this.components.websocketClient.startSimulation(simulationData);
            } else {
                // Fallback to HTTP request
                await this.components.beamformingEngine.runSimulation(simulationData);
            }
            
        } catch (error) {
            console.error('Simulation failed:', error);
            this.showError('Simulation Error', error.message);
            this.resetSimulationState();
        }
    }
    
    onSimulationProgress(progress, message) {
        this.showProgress(progress, message);
    }
    
    onSimulationComplete(results) {
        console.log('Simulation completed:', results);
        
        // Update visualizations
        this.components.visualization.updateBeamPattern(results.beamPattern);
        this.components.visualization.updateInterferenceMap(results.interferenceMap);
        this.components.visualization.updateArrayGeometry(results.arrayGeometry);
        
        this.showProgress(100, 'Simulation completed successfully');
        
        setTimeout(() => {
            this.resetSimulationState();
            this.hideProgress();
        }, 1000);
    }
    
    resetSimulationState() {
        this.state.simulationRunning = false;
        const simulateBtn = document.getElementById('simulate-btn');
        simulateBtn.innerHTML = '<i class="fas fa-play"></i> Run Simulation';
        simulateBtn.disabled = false;
    }
    
    resetParameters() {
        console.log('Resetting parameters...');
        
        // Reset to default values
        this.state.parameters = {
            frequency: 2.4e9,
            phaseShift: 0,
            txPosition: { x: 0.1, y: 0.0 },
            arrayGeometry: 'linear',
            curvature: 0.0,
            numElements: 8,
            elementSpacing: 0.5,
            steeringAngle: 0,
            propagationSpeed: 3e8
        };
        
        // Reset UI controls
        this.components.uiControls.resetControls();
        
        // Reset visualizations
        this.components.visualization.reset();
        
        console.log('Parameters reset to defaults');
    }
    
    toggleRealtimeMode() {
        this.state.realtimeMode = !this.state.realtimeMode;
        const realtimeBtn = document.getElementById('realtime-toggle');
        
        if (this.state.realtimeMode) {
            realtimeBtn.classList.add('active');
            realtimeBtn.innerHTML = '<i class="fas fa-bolt"></i> Realtime ON';
            console.log('Realtime mode enabled');
        } else {
            realtimeBtn.classList.remove('active');
            realtimeBtn.innerHTML = '<i class="fas fa-bolt"></i> Realtime';
            console.log('Realtime mode disabled');
        }
    }
    
    addArray() {
        if (this.state.arrays.length >= this.config.maxArrays) {
            this.showNotification('Maximum number of arrays reached', 'warning');
            return;
        }
        
        const arrayId = `array-${this.state.arrays.length + 1}`;
        const newArray = {
            id: arrayId,
            name: `Array ${this.state.arrays.length + 1}`,
            type: 'linear',
            numElements: 8,
            spacing: 0.5,
            position: { x: this.state.arrays.length * 2, y: 0 },
            orientation: 0,
            active: false
        };
        
        this.state.arrays.push(newArray);
        
        // Update UI
        this.updateArraysList();
        
        console.log(`Added new array: ${arrayId}`);
    }
    
    updateArraysList() {
        const arraysList = document.getElementById('arrays-list');
        arraysList.innerHTML = '';
        
        this.state.arrays.forEach(array => {
            const arrayElement = document.createElement('div');
            arrayElement.className = `array-item ${array.active ? 'active' : ''}`;
            arrayElement.dataset.arrayId = array.id;
            
            arrayElement.innerHTML = `
                <div class="array-header">
                    <i class="fas fa-satellite"></i>
                    <span>${array.name}</span>
                    <button class="array-remove" data-array-id="${array.id}">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="array-properties">
                    <span>${array.type.charAt(0).toUpperCase() + array.type.slice(1)}, ${array.numElements} elements, λ${array.spacing} spacing</span>
                </div>
            `;
            
            // Add event listeners
            arrayElement.addEventListener('click', (e) => {
                if (!e.target.closest('.array-remove')) {
                    this.setActiveArray(array.id);
                }
            });
            
            const removeBtn = arrayElement.querySelector('.array-remove');
            removeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.removeArray(array.id);
            });
            
            arraysList.appendChild(arrayElement);
        });
    }
    
    setActiveArray(arrayId) {
        this.state.arrays.forEach(array => {
            array.active = array.id === arrayId;
        });
        
        this.updateArraysList();
        
        // Update visualizations for the active array
        const activeArray = this.state.arrays.find(a => a.active);
        if (activeArray) {
            this.components.visualization.updateArrayGeometry(activeArray);
        }
    }
    
    removeArray(arrayId) {
        if (this.state.arrays.length <= 1) {
            this.showNotification('Cannot remove the last array', 'warning');
            return;
        }
        
        this.state.arrays = this.state.arrays.filter(array => array.id !== arrayId);
        
        // If we removed the active array, activate the first one
        if (!this.state.arrays.some(array => array.active)) {
            this.state.arrays[0].active = true;
        }
        
        this.updateArraysList();
        
        console.log(`Removed array: ${arrayId}`);
    }
    
    setActiveVisualization(vizType) {
        // Update tabs
        document.querySelectorAll('.viz-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.viz === vizType);
        });
        
        // Show/hide panels
        document.querySelectorAll('.viz-panel').forEach(panel => {
            panel.classList.toggle('active', panel.id === `${vizType}-panel`);
        });
        
        console.log(`Switched to ${vizType} visualization`);
    }
    
    showProgress(percent, message) {
        const progressFill = document.getElementById('progress-fill');
        const progressPercent = document.getElementById('progress-percent');
        const progressMessage = document.getElementById('progress-message');
        const progressSection = document.getElementById('progress-section');
        
        progressFill.style.width = `${percent}%`;
        progressPercent.textContent = `${percent}%`;
        progressMessage.textContent = message;
        progressSection.style.display = 'block';
    }
    
    hideProgress() {
        const progressSection = document.getElementById('progress-section');
        progressSection.style.display = 'none';
    }
    
    showError(title, message) {
        // Create error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.innerHTML = `
            <div class="alert-icon">
                <i class="fas fa-exclamation-circle"></i>
            </div>
            <div class="alert-content">
                <div class="alert-title">${title}</div>
                <div class="alert-message">${message}</div>
            </div>
        `;
        
        // Add to top of left panel
        const leftPanel = document.querySelector('.left-panel');
        leftPanel.insertBefore(errorDiv, leftPanel.firstChild);
        
        // Remove after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
    
    showNotification(message, type = 'info') {
        // Implementation for toast notifications
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
    
    updateConnectionStatus(status) {
        this.state.connectionStatus = status;
        const statusElement = document.getElementById('connection-status');
        
        switch (status) {
            case 'connected':
                statusElement.className = 'status-connected';
                statusElement.innerHTML = '<i class="fas fa-circle"></i> Connected to Server';
                break;
            case 'connecting':
                statusElement.className = 'status-warning';
                statusElement.innerHTML = '<i class="fas fa-circle"></i> Connecting...';
                break;
            case 'disconnected':
                statusElement.className = 'status-error';
                statusElement.innerHTML = '<i class="fas fa-circle"></i> Disconnected';
                break;
        }
    }
    
    startUpdateLoop() {
        let lastUpdate = 0;
        
        const update = (timestamp) => {
            const delta = timestamp - lastUpdate;
            
            if (delta >= this.config.updateInterval) {
                // Update FPS counter
                this.updateFPSCounter(1000 / delta);
                
                // Update visualizations if realtime mode is on
                if (this.state.realtimeMode && !this.state.simulationRunning) {
                    this.components.visualization.updateRealtime();
                }
                
                lastUpdate = timestamp;
            }
            
            requestAnimationFrame(update);
        };
        
        requestAnimationFrame(update);
    }
    
    updateFPSCounter(fps) {
        const fpsElement = document.getElementById('fps-counter');
        fpsElement.textContent = `${Math.round(fps)} FPS`;
    }
    
    scheduleUpdate() {
        // Debounce updates to prevent too frequent requests
        if (this._updateTimeout) {
            clearTimeout(this._updateTimeout);
        }
        
        this._updateTimeout = setTimeout(() => {
            if (this.components.websocketClient.isConnected()) {
                this.components.websocketClient.sendParameterUpdate('batch', this.state.parameters);
            }
        }, 300);
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new BeamformingApp();
});