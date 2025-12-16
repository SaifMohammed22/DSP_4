// WebSocket Client - Handles communication with backend
class WebSocketClient {
    constructor(app) {
        this.app = app;
        this.socket = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        
        // Event callbacks
        this.callbacks = {
            onConnect: [],
            onDisconnect: [],
            onSimulationProgress: [],
            onSimulationComplete: [],
            onParameterUpdate: [],
            onError: []
        };
    }
    
    async connect() {
        return new Promise((resolve, reject) => {
            try {
                const url = this.app.config.backendUrl;
                console.log(`Connecting to WebSocket server at ${url}...`);
                
                this.socket = io(url, {
                    path: this.app.config.socketPath,
                    transports: ['websocket', 'polling'],
                    reconnection: true,
                    reconnectionAttempts: this.maxReconnectAttempts,
                    reconnectionDelay: this.reconnectDelay,
                    timeout: 10000
                });
                
                // Setup event handlers
                this.setupEventHandlers();
                
                // Set connection timeout
                const connectionTimeout = setTimeout(() => {
                    if (!this.connected) {
                        this.handleDisconnect();
                        reject(new Error('Connection timeout'));
                    }
                }, 5000);
                
                // Store resolve for when connection is established
                this.connectionResolve = (value) => {
                    clearTimeout(connectionTimeout);
                    resolve(value);
                };
                
                this.connectionReject = (error) => {
                    clearTimeout(connectionTimeout);
                    reject(error);
                };
                
            } catch (error) {
                console.error('Failed to create WebSocket connection:', error);
                reject(error);
            }
        });
    }
    
    setupEventHandlers() {
        if (!this.socket) return;
        
        // Connection events
        this.socket.on('connect', () => this.handleConnect());
        this.socket.on('disconnect', (reason) => this.handleDisconnect(reason));
        this.socket.on('connect_error', (error) => this.handleConnectError(error));
        
        // Application events
        this.socket.on('connected', (data) => this.handleConnected(data));
        this.socket.on('beamforming_progress', (data) => this.handleSimulationProgress(data));
        this.socket.on('beamforming_result', (data) => this.handleSimulationComplete(data));
        this.socket.on('ft_mixer_progress', (data) => this.handleFTMixerProgress(data));
        this.socket.on('task_cancelled', (data) => this.handleTaskCancelled(data));
        this.socket.on('task_error', (data) => this.handleTaskError(data));
    }
    
    handleConnect() {
        console.log('WebSocket connected, waiting for server handshake...');
        this.app.updateConnectionStatus('connecting');
    }
    
    handleConnected(data) {
        console.log('Server handshake received:', data);
        this.connected = true;
        this.reconnectAttempts = 0;
        this.app.updateConnectionStatus('connected');
        
        // Notify callbacks
        this.emitCallback('onConnect', data);
        
        // Resolve connection promise
        if (this.connectionResolve) {
            this.connectionResolve(data);
            this.connectionResolve = null;
            this.connectionReject = null;
        }
        
        // Update UI
        this.app.showNotification('Connected to beamforming server', 'success');
    }
    
    handleDisconnect(reason) {
        console.log('WebSocket disconnected:', reason);
        this.connected = false;
        this.app.updateConnectionStatus('disconnected');
        
        // Notify callbacks
        this.emitCallback('onDisconnect', { reason });
        
        // Reject connection promise if still pending
        if (this.connectionReject) {
            this.connectionReject(new Error(`Disconnected: ${reason}`));
            this.connectionResolve = null;
            this.connectionReject = null;
        }
        
        // Attempt reconnect if not explicitly disconnected
        if (reason !== 'io client disconnect') {
            this.attemptReconnect();
        }
    }
    
    handleConnectError(error) {
        console.error('WebSocket connection error:', error);
        this.app.updateConnectionStatus('disconnected');
        
        // Notify callbacks
        this.emitCallback('onError', { type: 'connection', error });
        
        // Reject connection promise if still pending
        if (this.connectionReject) {
            this.connectionReject(error);
            this.connectionResolve = null;
            this.connectionReject = null;
        }
    }
    
    handleSimulationProgress(data) {
        console.log('Simulation progress:', data);
        
        // Update app progress
        this.app.onSimulationProgress(data.progress, data.message);
        
        // Notify callbacks
        this.emitCallback('onSimulationProgress', data);
    }
    
    handleSimulationComplete(data) {
        console.log('Simulation complete:', data);
        
        // Update app with results
        this.app.onSimulationComplete(data.result);
        
        // Notify callbacks
        this.emitCallback('onSimulationComplete', data);
    }
    
    handleFTMixerProgress(data) {
        console.log('FT Mixer progress:', data);
        // Handle FT mixer progress if needed
    }
    
    handleTaskCancelled(data) {
        console.log('Task cancelled:', data);
        this.app.showNotification('Simulation cancelled', 'warning');
    }
    
    handleTaskError(data) {
        console.error('Task error:', data);
        this.app.showError('Simulation Error', data.error);
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('Max reconnection attempts reached');
            this.app.showNotification('Failed to reconnect to server', 'error');
            return;
        }
        
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        
        console.log(`Attempting reconnect in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        setTimeout(() => {
            if (!this.connected) {
                console.log('Attempting reconnection...');
                this.socket.connect();
            }
        }, delay);
    }
    
    // Public API methods
    isConnected() {
        return this.connected;
    }
    
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.connected = false;
            this.app.updateConnectionStatus('disconnected');
        }
    }
    
    sendParameterUpdate(parameter, value) {
        if (!this.connected) {
            console.warn('Cannot send parameter update: not connected');
            return;
        }
        
        const data = {
            parameter,
            value,
            timestamp: Date.now()
        };
        
        this.socket.emit('parameter_update', data);
    }
    
    startSimulation(simulationData) {
        if (!this.connected) {
            console.warn('Cannot start simulation: not connected');
            this.app.showNotification('Not connected to server', 'error');
            return;
        }
        
        const data = {
            ...simulationData,
            task_id: `sim_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            timestamp: Date.now()
        };
        
        this.socket.emit('start_simulation', data);
        console.log('Simulation started:', data.task_id);
    }
    
    async loadScenario(scenarioName) {
        if (!this.connected) {
            console.warn('Cannot load scenario: not connected');
            return;
        }
        
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Scenario load timeout'));
            }, 5000);
            
            const handler = (data) => {
                if (data.scenario === scenarioName) {
                    clearTimeout(timeout);
                    this.socket.off('scenario_loaded', handler);
                    resolve(data);
                }
            };
            
            this.socket.on('scenario_loaded', handler);
            this.socket.emit('load_scenario', { scenario: scenarioName });
        });
    }
    
    cancelTask(taskId) {
        if (!this.connected) return false;
        
        this.socket.emit('cancel_task', { task_id: taskId });
        return true;
    }
    
    // Callback management
    on(event, callback) {
        if (this.callbacks[event]) {
            this.callbacks[event].push(callback);
        }
    }
    
    off(event, callback) {
        if (this.callbacks[event]) {
            const index = this.callbacks[event].indexOf(callback);
            if (index > -1) {
                this.callbacks[event].splice(index, 1);
            }
        }
    }
    
    emitCallback(event, data) {
        if (this.callbacks[event]) {
            this.callbacks[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in ${event} callback:`, error);
                }
            });
        }
    }
    
    // Utility methods
    getLatency() {
        if (!this.connected) return null;
        
        const start = Date.now();
        return new Promise((resolve) => {
            this.socket.emit('ping', { timestamp: start }, () => {
                const latency = Date.now() - start;
                resolve(latency);
            });
        });
    }
}