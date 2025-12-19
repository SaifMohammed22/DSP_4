// Main JavaScript for Beamforming Simulator

class BeamformingApp {
    constructor() {
        this.apiBase = 'http://localhost:5000/api';
        this.currentState = {
            num_elements: 16,
            frequency: 2.4e9,
            element_spacing: 0.5,
            beam_angle: 0,
            array_type: 'linear',
            mode: 'transmitter',
            grid_size: 400,
            grid_range: 20
        };
        
        this.isUpdating = false;
        this.initializeEventListeners();
        this.loadScenarios();
        this.updateVisualization();
    }
    
    initializeEventListeners() {
        // Mode selection
        document.getElementById('mode-select').addEventListener('change', (e) => {
            this.currentState.mode = e.target.value;
            this.updateVisualization();
        });
        
        // Scenario selection
        document.getElementById('scenario-select').addEventListener('change', (e) => {
            if (e.target.value) {
                this.loadScenario(e.target.value);
            }
        });
        
        // Number of elements
        document.getElementById('num-elements').addEventListener('input', (e) => {
            this.currentState.num_elements = parseInt(e.target.value);
            document.getElementById('num-elements-value').textContent = e.target.value;
        });
        
        // Element spacing
        document.getElementById('element-spacing').addEventListener('input', (e) => {
            this.currentState.element_spacing = parseFloat(e.target.value);
            document.getElementById('element-spacing-value').textContent = e.target.value;
        });
        
        // Frequency
        document.getElementById('frequency').addEventListener('input', (e) => {
            this.updateFrequency();
        });
        
        document.getElementById('frequency-unit').addEventListener('change', () => {
            this.updateFrequency();
        });
        
        // Array geometry
        document.getElementById('array-geometry').addEventListener('change', (e) => {
            this.currentState.array_type = e.target.value;
        });
        
        // Beam angle
        document.getElementById('beam-angle').addEventListener('input', (e) => {
            this.currentState.beam_angle = parseInt(e.target.value);
            document.getElementById('beam-angle-value').textContent = e.target.value + '°';
        });
        
        // Update button
        document.getElementById('update-btn').addEventListener('click', () => {
            this.updateVisualization();
        });
        
        // Reset button
        document.getElementById('reset-btn').addEventListener('click', () => {
            this.resetToDefaults();
        });
    }
    
    updateFrequency() {
        const freqValue = parseFloat(document.getElementById('frequency').value);
        const freqUnit = parseFloat(document.getElementById('frequency-unit').value);
        this.currentState.frequency = freqValue * freqUnit / 10;
        
        const unitText = freqUnit === 1e6 ? 'MHz' : 'GHz';
        document.getElementById('frequency-value').textContent = `${freqValue} ${unitText}`;
    }
    
    async loadScenarios() {
        try {
            const response = await fetch(`${this.apiBase}/scenarios`);
            const data = await response.json();
            
            if (data.success) {
                const select = document.getElementById('scenario-select');
                // Keep the default option
                select.innerHTML = '<option value="">Select Scenario</option>';
                
                data.scenarios.forEach(scenario => {
                    const option = document.createElement('option');
                    option.value = scenario.name;
                    option.textContent = scenario.name;
                    select.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading scenarios:', error);
        }
    }
    
    async loadScenario(scenarioName) {
        try {
            const response = await fetch(`${this.apiBase}/scenario/${encodeURIComponent(scenarioName)}`);
            const data = await response.json();
            
            if (data.success) {
                const scenario = data.scenario;
                
                // Update UI controls
                document.getElementById('num-elements').value = scenario.num_elements;
                document.getElementById('num-elements-value').textContent = scenario.num_elements;
                
                document.getElementById('element-spacing').value = scenario.element_spacing || 0.5;
                document.getElementById('element-spacing-value').textContent = scenario.element_spacing || 0.5;
                
                // Update frequency with appropriate unit
                if (scenario.frequency >= 1e9) {
                    document.getElementById('frequency-unit').value = '1e9';
                    document.getElementById('frequency').value = scenario.frequency / 1e8;
                } else {
                    document.getElementById('frequency-unit').value = '1e6';
                    document.getElementById('frequency').value = scenario.frequency / 1e5;
                }
                this.updateFrequency();
                
                document.getElementById('array-geometry').value = scenario.array_type.toLowerCase();
                document.getElementById('mode-select').value = scenario.mode || 'transmitter';
                
                document.getElementById('beam-angle').value = scenario.beam_angle || 0;
                document.getElementById('beam-angle-value').textContent = (scenario.beam_angle || 0) + '°';
                
                // Update state
                this.currentState = {
                    num_elements: scenario.num_elements,
                    frequency: scenario.frequency,
                    element_spacing: scenario.element_spacing || 0.5,
                    beam_angle: scenario.beam_angle || 0,
                    array_type: scenario.array_type.toLowerCase(),
                    mode: scenario.mode || 'transmitter',
                    grid_size: 400,
                    grid_range: scenario.grid_range || 20
                };
                
                // Show description
                const descDiv = document.getElementById('scenario-description');
                descDiv.innerHTML = `
                    <strong>Description:</strong> ${scenario.description || ''}<br>
                    <strong>Application:</strong> ${scenario.application || ''}
                `;
                
                // Update visualization
                this.updateVisualization();
            }
        } catch (error) {
            console.error('Error loading scenario:', error);
        }
    }
    
    resetToDefaults() {
        this.currentState = {
            num_elements: 16,
            frequency: 2.4e9,
            element_spacing: 0.5,
            beam_angle: 0,
            array_type: 'linear',
            mode: 'transmitter',
            grid_size: 400,
            grid_range: 20
        };
        
        // Reset UI
        document.getElementById('num-elements').value = 16;
        document.getElementById('num-elements-value').textContent = '16';
        document.getElementById('element-spacing').value = 0.5;
        document.getElementById('element-spacing-value').textContent = '0.5';
        document.getElementById('frequency').value = 24;
        document.getElementById('frequency-unit').value = '1e9';
        this.updateFrequency();
        document.getElementById('array-geometry').value = 'linear';
        document.getElementById('mode-select').value = 'transmitter';
        document.getElementById('beam-angle').value = 0;
        document.getElementById('beam-angle-value').textContent = '0°';
        document.getElementById('scenario-select').value = '';
        document.getElementById('scenario-description').innerHTML = '';
        
        this.updateVisualization();
    }
    
    async updateVisualization() {
        if (this.isUpdating) return;
        this.isUpdating = true;
        
        // Show loading indicators
        document.getElementById('loading-interference').classList.add('active');
        document.getElementById('loading-beam').classList.add('active');
        
        try {
            // Update all visualizations in parallel
            await Promise.all([
                this.updateArrayElements(),
                this.updateInterferenceMap(),
                this.updateBeamProfile()
            ]);
        } catch (error) {
            console.error('Error updating visualization:', error);
            alert('Error updating visualization. Please check console for details.');
        } finally {
            // Hide loading indicators
            document.getElementById('loading-interference').classList.remove('active');
            document.getElementById('loading-beam').classList.remove('active');
            this.isUpdating = false;
        }
    }
    
    async updateArrayElements() {
        try {
            const response = await fetch(`${this.apiBase}/compute_array_positions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.currentState)
            });
            
            const data = await response.json();
            
            if (data.success) {
                const trace = {
                    x: data.data.x_positions,
                    y: data.data.y_positions,
                    mode: 'markers',
                    type: 'scatter',
                    marker: {
                        size: 12,
                        color: '#ef4444',
                        line: { color: '#fca5a5', width: 2 }
                    },
                    name: 'Array Elements'
                };
                
                const layout = {
                    paper_bgcolor: '#2e3240',
                    plot_bgcolor: '#2e3240',
                    font: { color: '#e5e7eb' },
                    xaxis: {
                        title: 'X Position (λ)',
                        gridcolor: '#374151',
                        zerolinecolor: '#4b5563'
                    },
                    yaxis: {
                        title: 'Y Position (λ)',
                        gridcolor: '#374151',
                        zerolinecolor: '#4b5563',
                        scaleanchor: 'x'
                    },
                    margin: { l: 50, r: 20, t: 20, b: 50 },
                    hovermode: 'closest'
                };
                
                Plotly.newPlot('array-elements-plot', [trace], layout, {
                    responsive: true,
                    displayModeBar: false
                });
            }
        } catch (error) {
            console.error('Error updating array elements:', error);
        }
    }
    
    async updateInterferenceMap() {
        try {
            const response = await fetch(`${this.apiBase}/compute_interference`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.currentState)
            });
            
            const data = await response.json();
            
            if (data.success) {
                const trace = {
                    z: data.data.interference,
                    x: data.data.x_grid[0],
                    y: data.data.y_grid.map(row => row[0]),
                    type: 'heatmap',
                    colorscale: 'Viridis',
                    colorbar: {
                        title: 'Intensity',
                        titleside: 'right',
                        tickmode: 'linear',
                        tick0: 0,
                        dtick: 0.2
                    }
                };
                
                // Add array element markers
                const positions = data.data.positions;
                const markerTrace = {
                    x: positions.map(p => p[0]),
                    y: positions.map(p => p[1]),
                    mode: 'markers',
                    type: 'scatter',
                    marker: {
                        size: 10,
                        color: '#ef4444',
                        symbol: 'circle',
                        line: { color: 'white', width: 2 }
                    },
                    name: 'Array Elements',
                    showlegend: false
                };
                
                const layout = {
                    paper_bgcolor: '#2e3240',
                    plot_bgcolor: '#2e3240',
                    font: { color: '#e5e7eb' },
                    xaxis: {
                        title: 'X Position (λ)',
                        gridcolor: '#374151'
                    },
                    yaxis: {
                        title: 'Y Position (λ)',
                        gridcolor: '#374151',
                        scaleanchor: 'x'
                    },
                    margin: { l: 60, r: 100, t: 20, b: 60 }
                };
                
                Plotly.newPlot('interference-map', [trace, markerTrace], layout, {
                    responsive: true,
                    displayModeBar: true,
                    modeBarButtonsToRemove: ['select2d', 'lasso2d']
                });
            }
        } catch (error) {
            console.error('Error updating interference map:', error);
        }
    }
    
    async updateBeamProfile() {
        try {
            const response = await fetch(`${this.apiBase}/compute_beam_profile`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.currentState)
            });
            
            const data = await response.json();
            
            if (data.success) {
                const trace = {
                    r: data.data.magnitude,
                    theta: data.data.angles,
                    type: 'scatterpolar',
                    mode: 'lines',
                    line: {
                        color: '#22d3ee',
                        width: 3
                    },
                    fill: 'toself',
                    fillcolor: 'rgba(34, 211, 238, 0.1)',
                    name: 'Beam Pattern'
                };
                
                const layout = {
                    paper_bgcolor: '#2e3240',
                    plot_bgcolor: '#2e3240',
                    font: { color: '#e5e7eb' },
                    polar: {
                        bgcolor: '#2e3240',
                        radialaxis: {
                            visible: true,
                            range: [0, Math.max(...data.data.magnitude) * 1.1],
                            gridcolor: '#374151',
                            tickfont: { color: '#9ca3af' }
                        },
                        angularaxis: {
                            direction: 'clockwise',
                            rotation: 90,
                            gridcolor: '#374151',
                            tickfont: { color: '#e5e7eb' },
                            tickmode: 'linear',
                            tick0: 0,
                            dtick: 15
                        }
                    },
                    margin: { l: 80, r: 80, t: 40, b: 80 },
                    showlegend: false
                };
                
                Plotly.newPlot('beam-profile', [trace], layout, {
                    responsive: true,
                    displayModeBar: true,
                    modeBarButtonsToRemove: ['select2d', 'lasso2d']
                });
            }
        } catch (error) {
            console.error('Error updating beam profile:', error);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new BeamformingApp();
});