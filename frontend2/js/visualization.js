// Visualization Manager - Handles all plotting and visualization
class Visualization {
    constructor(app) {
        this.app = app;
        this.plots = new Map();
        this.currentData = null;
        
        // Color scales
        this.colorScales = {
            beamPattern: [
                [0, 'rgb(0, 0, 128)'],     // Dark blue
                [0.25, 'rgb(0, 0, 255)'],   // Blue
                [0.5, 'rgb(0, 255, 255)'],  // Cyan
                [0.75, 'rgb(255, 255, 0)'], // Yellow
                [1, 'rgb(255, 0, 0)']       // Red
            ],
            interference: 'Viridis',
            arrayGeometry: 'Set1'
        };
    }
    
    async init() {
        console.log('Initializing visualizations...');
        
        try {
            // Initialize Plotly plots
            await this.initPlots();
            
            // Set up event listeners for visualization controls
            this.setupEventListeners();
            
            // Create initial placeholder visualizations
            await this.createPlaceholderVisualizations();
            
            console.log('Visualizations initialized');
            
        } catch (error) {
            console.error('Failed to initialize visualizations:', error);
        }
    }
    
    async initPlots() {
        // Initialize interference map
        this.initInterferenceMap();
        
        // Initialize beam profile
        this.initBeamProfile();
        
        // Initialize array geometry
        this.initArrayGeometry();
        
        // Initialize 3D pattern
        this.init3DPattern();
    }
    
    initInterferenceMap() {
        const element = document.getElementById('interference-map');
        
        const layout = {
            title: {
                text: 'Constructive/Destructive Interference',
                font: { size: 14, color: '#f1f5f9' }
            },
            xaxis: {
                title: 'X Position (m)',
                gridcolor: '#475569',
                zerolinecolor: '#475569',
                linecolor: '#475569',
                tickcolor: '#475569',
                tickfont: { color: '#94a3b8' },
                titlefont: { color: '#cbd5e1' }
            },
            yaxis: {
                title: 'Y Position (m)',
                gridcolor: '#475569',
                zerolinecolor: '#475569',
                linecolor: '#475569',
                tickcolor: '#475569',
                tickfont: { color: '#94a3b8' },
                titlefont: { color: '#cbd5e1' }
            },
            plot_bgcolor: '#0f172a',
            paper_bgcolor: '#1e293b',
            margin: { t: 40, r: 20, b: 40, l: 50 },
            colorway: ['#ef4444', '#94a3b8', '#10b981'], // Red, Gray, Green
            showlegend: false
        };
        
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'select2d', 'lasso2d', 'autoScale2d'],
            modeBarButtonsToAdd: ['drawline', 'drawopenpath', 'eraseshape']
        };
        
        this.plots.set('interference', {
            element,
            layout,
            config,
            data: []
        });
    }
    
    initBeamProfile() {
        const element = document.getElementById('beam-profile');
        
        const layout = {
            title: {
                text: 'Beam Profile',
                font: { size: 14, color: '#f1f5f9' }
            },
            xaxis: {
                title: 'Angle (degrees)',
                gridcolor: '#475569',
                zerolinecolor: '#475569',
                linecolor: '#475569',
                tickcolor: '#475569',
                tickfont: { color: '#94a3b8' },
                titlefont: { color: '#cbd5e1' },
                range: [-90, 90]
            },
            yaxis: {
                title: 'Magnitude (dB)',
                gridcolor: '#475569',
                zerolinecolor: '#475569',
                linecolor: '#475569',
                tickcolor: '#475569',
                tickfont: { color: '#94a3b8' },
                titlefont: { color: '#cbd5e1' }
            },
            plot_bgcolor: '#0f172a',
            paper_bgcolor: '#1e293b',
            margin: { t: 40, r: 20, b: 40, l: 50 },
            showlegend: true
        };
        
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false
        };
        
        this.plots.set('beamProfile', {
            element,
            layout,
            config,
            data: []
        });
    }
    
    initArrayGeometry() {
        const element = document.getElementById('array-geometry');
        
        const layout = {
            title: {
                text: 'Array Geometry',
                font: { size: 14, color: '#f1f5f9' }
            },
            xaxis: {
                title: 'X Position (m)',
                gridcolor: '#475569',
                zerolinecolor: '#475569',
                linecolor: '#475569',
                tickcolor: '#475569',
                tickfont: { color: '#94a3b8' },
                titlefont: { color: '#cbd5e1' },
                scaleanchor: 'y',
                scaleratio: 1
            },
            yaxis: {
                title: 'Y Position (m)',
                gridcolor: '#475569',
                zerolinecolor: '#475569',
                linecolor: '#475569',
                tickcolor: '#475569',
                tickfont: { color: '#94a3b8' },
                titlefont: { color: '#cbd5e1' }
            },
            plot_bgcolor: '#0f172a',
            paper_bgcolor: '#1e293b',
            margin: { t: 40, r: 20, b: 40, l: 50 },
            showlegend: false
        };
        
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false
        };
        
        this.plots.set('arrayGeometry', {
            element,
            layout,
            config,
            data: []
        });
    }
    
    init3DPattern() {
        const element = document.getElementById('3d-pattern');
        
        const layout = {
            title: {
                text: '3D Beam Pattern',
                font: { size: 14, color: '#f1f5f9' }
            },
            scene: {
                xaxis: {
                    title: 'X (m)',
                    backgroundcolor: '#0f172a',
                    gridcolor: '#475569',
                    showbackground: true,
                    zerolinecolor: '#475569'
                },
                yaxis: {
                    title: 'Y (m)',
                    backgroundcolor: '#0f172a',
                    gridcolor: '#475569',
                    showbackground: true,
                    zerolinecolor: '#475569'
                },
                zaxis: {
                    title: 'Magnitude (dB)',
                    backgroundcolor: '#0f172a',
                    gridcolor: '#475569',
                    showbackground: true,
                    zerolinecolor: '#475569'
                },
                camera: {
                    eye: { x: 1.5, y: 1.5, z: 1.5 }
                },
                aspectratio: { x: 1, y: 1, z: 0.7 }
            },
            paper_bgcolor: '#1e293b',
            margin: { t: 40, r: 20, b: 40, l: 0 }
        };
        
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false
        };
        
        this.plots.set('3dPattern', {
            element,
            layout,
            config,
            data: []
        });
    }
    
    setupEventListeners() {
        // Map export button
        document.getElementById('map-export').addEventListener('click', () => {
            this.exportPlot('interference');
        });
        
        // Fullscreen button
        document.getElementById('map-fullscreen').addEventListener('click', () => {
            this.toggleFullscreen('interference');
        });
        
        // Profile type selector
        document.getElementById('profile-type').addEventListener('change', (e) => {
            this.updateBeamProfileType(e.target.value);
        });
        
        // 3D rotation button
        document.getElementById('rotate-3d').addEventListener('click', () => {
            this.rotate3DView();
        });
        
        // Show labels button
        document.getElementById('show-labels').addEventListener('click', (e) => {
            e.currentTarget.classList.toggle('active');
            this.toggleArrayLabels();
        });
    }
    
    async createPlaceholderVisualizations() {
        // Create placeholder data
        const placeholderData = {
            beamPattern: this.createPlaceholderBeamPattern(),
            interferenceMap: this.createPlaceholderInterferenceMap(),
            arrayGeometry: this.createPlaceholderArrayGeometry()
        };
        
        this.currentData = placeholderData;
        
        // Update all visualizations
        this.updateInterferenceMap(placeholderData.interferenceMap);
        this.updateBeamProfile(placeholderData.beamPattern);
        this.updateArrayGeometry(placeholderData.arrayGeometry);
        this.update3DPattern(placeholderData.beamPattern);
    }
    
    createPlaceholderBeamPattern() {
        const gridSize = 200;
        const gridRange = 10;
        
        // Create grid
        const X = this.createGrid(gridSize, gridRange);
        const Y = this.createGrid(gridSize, gridRange);
        
        // Create beam pattern (main lobe at 0,0)
        const magnitude = this.createZeroGrid(gridSize, gridSize);
        const centerX = gridSize / 2;
        const centerY = gridSize / 2;
        
        for (let i = 0; i < gridSize; i++) {
            for (let j = 0; j < gridSize; j++) {
                const dx = (i - centerX) / centerX;
                const dy = (j - centerY) / centerY;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                // Main lobe
                magnitude[i][j] = Math.exp(-distance * distance * 10);
                
                // Add some side lobes
                magnitude[i][j] += 0.3 * Math.exp(-Math.pow(distance - 0.3, 2) * 50);
                magnitude[i][j] += 0.1 * Math.exp(-Math.pow(distance - 0.6, 2) * 30);
            }
        }
        
        // Normalize
        const maxVal = Math.max(...magnitude.flat());
        const normalized = magnitude.map(row => row.map(val => val / maxVal));
        
        return {
            magnitude: normalized,
            X: X.mesh,
            Y: Y.mesh,
            wavelength: 0.125, // 2.4 GHz wavelength
            gridSize,
            gridRange
        };
    }
    
    createPlaceholderInterferenceMap() {
        const gridSize = 200;
        const gridRange = 10;
        
        const X = this.createGrid(gridSize, gridRange);
        const Y = this.createGrid(gridSize, gridRange);
        
        const interference = this.createZeroGrid(gridSize, gridSize);
        
        // Add constructive interference at center
        for (let i = 0; i < gridSize; i++) {
            for (let j = 0; j < gridSize; j++) {
                const x = X.mesh[i][j];
                const y = Y.mesh[i][j];
                
                // Main constructive region
                const r1 = Math.sqrt(x * x + y * y);
                interference[i][j] += Math.exp(-r1 * r1 * 2);
                
                // Destructive regions
                const r2 = Math.sqrt(Math.pow(x - 3, 2) + Math.pow(y - 3, 2));
                interference[i][j] -= 0.5 * Math.exp(-r2 * r2 * 3);
                
                const r3 = Math.sqrt(Math.pow(x + 3, 2) + Math.pow(y + 3, 2));
                interference[i][j] -= 0.5 * Math.exp(-r3 * r3 * 3);
                
                // Add some noise
                interference[i][j] += 0.1 * Math.random();
            }
        }
        
        return {
            interference,
            X: X.mesh,
            Y: Y.mesh,
            sources: [[0.1, 0.0]],
            gridSize,
            gridRange
        };
    }
    
    createPlaceholderArrayGeometry() {
        // Create a linear array of 8 elements
        const positions = [];
        const numElements = 8;
        const spacing = 0.5 * 0.125; // λ/2 spacing
        
        for (let i = 0; i < numElements; i++) {
            const x = (i - (numElements - 1) / 2) * spacing;
            positions.push([x, 0]);
        }
        
        return {
            positions,
            type: 'linear',
            numElements,
            spacing: 0.5
        };
    }
    
    createGrid(size, range) {
        const linspace = Array.from({ length: size }, (_, i) => 
            -range + (2 * range * i) / (size - 1)
        );
        
        const mesh = [];
        for (let i = 0; i < size; i++) {
            mesh[i] = [];
            for (let j = 0; j < size; j++) {
                mesh[i][j] = linspace[j];
            }
        }
        
        return {
            linspace,
            mesh
        };
    }
    
    createZeroGrid(rows, cols) {
        return Array.from({ length: rows }, () => new Array(cols).fill(0));
    }
    
    // Public methods to update visualizations
    updateBeamPattern(beamPatternData) {
        if (!beamPatternData) return;
        
        this.currentData.beamPattern = beamPatternData;
        
        // Update 2D beam pattern in interference map
        this.updateInterferenceMapWithBeamPattern(beamPatternData);
        
        // Update beam profile
        this.updateBeamProfile(beamPatternData);
        
        // Update 3D pattern
        this.update3DPattern(beamPatternData);
    }
    
    updateInterferenceMap(interferenceData) {
        if (!interferenceData) return;
        
        this.currentData.interferenceMap = interferenceData;
        this.updateInterferenceMapPlot(interferenceData);
    }
    
    updateArrayGeometry(arrayGeometryData) {
        if (!arrayGeometryData) return;
        
        this.currentData.arrayGeometry = arrayGeometryData;
        this.updateArrayGeometryPlot(arrayGeometryData);
    }
    
    updateInterferenceMapWithBeamPattern(beamPatternData) {
        if (!beamPatternData || !this.currentData.interferenceMap) return;
        
        const { magnitude, X, Y } = beamPatternData;
        const { interference, sources } = this.currentData.interferenceMap;
        
        // Combine beam pattern with interference
        const combined = this.combineBeamAndInterference(magnitude, interference);
        
        this.updateInterferenceMapPlot({
            interference: combined,
            X,
            Y,
            sources,
            gridSize: beamPatternData.gridSize,
            gridRange: beamPatternData.gridRange
        });
    }
    
    combineBeamAndInterference(beamPattern, interference) {
        const rows = beamPattern.length;
        const cols = beamPattern[0].length;
        const combined = this.createZeroGrid(rows, cols);
        
        for (let i = 0; i < rows; i++) {
            for (let j = 0; j < cols; j++) {
                // Simple combination: beam pattern modulates interference
                combined[i][j] = beamPattern[i][j] * (interference[i][j] + 1);
            }
        }
        
        return combined;
    }
    
    updateInterferenceMapPlot(data) {
        const plot = this.plots.get('interference');
        if (!plot || !data) return;
        
        const { interference, X, Y, sources } = data;
        
        // Convert to dB for better visualization
        const interferenceDb = interference.map(row => 
            row.map(val => 10 * Math.log10(Math.max(val, 1e-10)))
        );
        
        // Create heatmap trace
        const heatmapTrace = {
            z: interferenceDb,
            x: X[0], // First row for x values
            y: Y.map(row => row[0]), // First column for y values
            type: 'heatmap',
            colorscale: this.colorScales.interference,
            showscale: true,
            colorbar: {
                title: 'Interference (dB)',
                titleside: 'right',
                tickfont: { color: '#94a3b8' },
                titlefont: { color: '#cbd5e1' }
            },
            hoverinfo: 'x+y+z',
            hovertemplate: 'X: %{x:.2f}m<br>Y: %{y:.2f}m<br>Int: %{z:.2f}dB<extra></extra>'
        };
        
        // Create source markers trace
        const sourceTrace = {
            x: sources.map(s => s[0]),
            y: sources.map(s => s[1]),
            mode: 'markers',
            type: 'scatter',
            marker: {
                size: 12,
                color: '#fbbf24',
                symbol: 'circle',
                line: { color: '#ffffff', width: 2 }
            },
            name: 'Sources',
            hoverinfo: 'x+y+name',
            hovertemplate: 'Source<br>X: %{x:.2f}m<br>Y: %{y:.2f}m<extra></extra>'
        };
        
        // Update plot
        Plotly.react(plot.element, [heatmapTrace, sourceTrace], plot.layout, plot.config);
    }
    
    updateBeamProfile(beamPatternData) {
        const plot = this.plots.get('beamProfile');
        if (!plot || !beamPatternData) return;
        
        const { magnitude, gridSize } = beamPatternData;
        const centerRow = Math.floor(gridSize / 2);
        
        // Extract horizontal and vertical cuts
        const horizontalCut = magnitude[centerRow];
        const verticalCut = magnitude.map(row => row[centerRow]);
        
        const angles = Array.from({ length: gridSize }, (_, i) => 
            -90 + (180 * i) / (gridSize - 1)
        );
        
        // Convert to dB
        const horizontalDb = horizontalCut.map(val => 10 * Math.log10(Math.max(val, 1e-10)));
        const verticalDb = verticalCut.map(val => 10 * Math.log10(Math.max(val, 1e-10)));
        
        // Get profile type
        const profileType = document.getElementById('profile-type').value;
        
        let traces = [];
        
        if (profileType === 'magnitude' || profileType === 'both') {
            traces.push({
                x: angles,
                y: horizontalDb,
                mode: 'lines',
                name: 'Horizontal (y=0)',
                line: { color: '#3b82f6', width: 2 }
            });
        }
        
        if (profileType === 'both') {
            traces.push({
                x: angles,
                y: verticalDb,
                mode: 'lines',
                name: 'Vertical (x=0)',
                line: { color: '#10b981', width: 2, dash: 'dash' }
            });
        }
        
        if (profileType === 'phase') {
            // Placeholder for phase data
            const phase = angles.map(angle => Math.sin(angle * Math.PI / 90));
            
            traces.push({
                x: angles,
                y: phase,
                mode: 'lines',
                name: 'Phase',
                line: { color: '#8b5cf6', width: 2 }
            });
        }
        
        Plotly.react(plot.element, traces, plot.layout, plot.config);
    }
    
    updateBeamProfileType(type) {
        if (this.currentData.beamPattern) {
            this.updateBeamProfile(this.currentData.beamPattern);
        }
    }
    
    updateArrayGeometryPlot(arrayGeometryData) {
        const plot = this.plots.get('arrayGeometry');
        if (!plot || !arrayGeometryData) return;
        
        const { positions, type, numElements } = arrayGeometryData;
        
        // Extract x and y coordinates
        const x = positions.map(p => p[0]);
        const y = positions.map(p => p[1]);
        
        // Create element markers
        const elementTrace = {
            x,
            y,
            mode: 'markers+text',
            type: 'scatter',
            marker: {
                size: 12,
                color: '#3b82f6',
                symbol: 'circle',
                line: { color: '#ffffff', width: 2 }
            },
            text: Array.from({ length: numElements }, (_, i) => `E${i + 1}`),
            textposition: 'top center',
            textfont: { color: '#94a3b8', size: 10 },
            name: 'Array Elements',
            hoverinfo: 'x+y+text',
            hovertemplate: 'Element %{text}<br>X: %{x:.2f}m<br>Y: %{y:.2f}m<extra></extra>'
        };
        
        // Connect elements with lines for linear arrays
        let lineTrace = null;
        if (type === 'linear') {
            // Sort by x coordinate for proper line drawing
            const sortedIndices = x.map((_, i) => i).sort((a, b) => x[a] - x[b]);
            const sortedX = sortedIndices.map(i => x[i]);
            const sortedY = sortedIndices.map(i => y[i]);
            
            lineTrace = {
                x: sortedX,
                y: sortedY,
                mode: 'lines',
                type: 'scatter',
                line: { color: '#94a3b8', width: 1, dash: 'dash' },
                opacity: 0.5,
                showlegend: false,
                hoverinfo: 'skip'
            };
        }
        
        // Add array center marker
        const centerTrace = {
            x: [0],
            y: [0],
            mode: 'markers',
            type: 'scatter',
            marker: {
                size: 16,
                color: '#ef4444',
                symbol: 'cross'
            },
            name: 'Array Center',
            hoverinfo: 'name',
            hovertemplate: 'Array Center<extra></extra>'
        };
        
        const traces = [elementTrace, centerTrace];
        if (lineTrace) traces.splice(1, 0, lineTrace);
        
        Plotly.react(plot.element, traces, plot.layout, plot.config);
    }
    
    toggleArrayLabels() {
        const plot = this.plots.get('arrayGeometry');
        if (!plot || !this.currentData.arrayGeometry) return;
        
        // Toggle text visibility in the trace
        const updatedLayout = { ...plot.layout };
        const traces = plot.data || [];
        
        if (traces.length > 0) {
            traces[0].mode = traces[0].mode.includes('text') ? 'markers' : 'markers+text';
            Plotly.react(plot.element, traces, updatedLayout, plot.config);
        }
    }
    
    update3DPattern(beamPatternData) {
        const plot = this.plots.get('3dPattern');
        if (!plot || !beamPatternData) return;
        
        const { magnitude, X, Y } = beamPatternData;
        
        // Convert to dB for 3D visualization
        const magnitudeDb = magnitude.map(row => 
            row.map(val => 10 * Math.log10(Math.max(val, 1e-10)))
        );
        
        const surfaceTrace = {
            z: magnitudeDb,
            x: X[0],
            y: Y.map(row => row[0]),
            type: 'surface',
            colorscale: 'Viridis',
            opacity: 0.9,
            contours: {
                z: {
                    show: true,
                    usecolormap: true,
                    highlightcolor: '#10b981',
                    project: { z: true }
                }
            },
            hoverinfo: 'x+y+z',
            hovertemplate: 'X: %{x:.2f}m<br>Y: %{y:.2f}m<br>Mag: %{z:.2f}dB<extra></extra>'
        };
        
        Plotly.react(plot.element, [surfaceTrace], plot.layout, plot.config);
    }
    
    rotate3DView() {
        const plot = this.plots.get('3dPattern');
        if (!plot) return;
        
        // Animate camera rotation
        const frames = [];
        const numFrames = 36;
        
        for (let i = 0; i < numFrames; i++) {
            const angle = (2 * Math.PI * i) / numFrames;
            frames.push({
                data: plot.data,
                layout: {
                    scene: {
                        camera: {
                            eye: {
                                x: 1.5 * Math.cos(angle),
                                y: 1.5 * Math.sin(angle),
                                z: 1.5
                            }
                        }
                    }
                }
            });
        }
        
        Plotly.animate(plot.element, frames, {
            frame: { duration: 50, redraw: true },
            transition: { duration: 0 }
        });
    }
    
    updateRealtime() {
        if (!this.currentData.beamPattern) return;
        
        // Add small random variations for realtime effect
        const { magnitude, X, Y } = this.currentData.beamPattern;
        const variedMagnitude = magnitude.map(row => 
            row.map(val => val * (0.95 + 0.1 * Math.random()))
        );
        
        this.updateBeamPattern({
            ...this.currentData.beamPattern,
            magnitude: variedMagnitude
        });
    }
    
    reset() {
        this.currentData = null;
        this.createPlaceholderVisualizations();
    }
    
    exportPlot(plotName) {
        const plot = this.plots.get(plotName === 'interference' ? 'interference' : 
                                  plotName === 'profile' ? 'beamProfile' : 
                                  plotName === 'array' ? 'arrayGeometry' : '3dPattern');
        
        if (!plot) return;
        
        Plotly.downloadImage(plot.element, {
            format: 'png',
            width: 1200,
            height: 800,
            filename: `beamforming_${plotName}_${Date.now()}`
        });
    }
    
    toggleFullscreen(plotName) {
        const plot = this.plots.get(plotName === 'interference' ? 'interference' : 
                                  plotName === 'profile' ? 'beamProfile' : 
                                  plotName === 'array' ? 'arrayGeometry' : '3dPattern');
        
        if (!plot) return;
        
        Plotly.relayout(plot.element, {
            width: window.innerWidth,
            height: window.innerHeight
        });
        
        // Toggle fullscreen class
        plot.element.classList.toggle('fullscreen');
        
        if (plot.element.classList.contains('fullscreen')) {
            plot.element.style.position = 'fixed';
            plot.element.style.top = '0';
            plot.element.style.left = '0';
            plot.element.style.width = '100vw';
            plot.element.style.height = '100vh';
            plot.element.style.zIndex = '1000';
        } else {
            plot.element.style.position = '';
            plot.element.style.top = '';
            plot.element.style.left = '';
            plot.element.style.width = '';
            plot.element.style.height = '';
            plot.element.style.zIndex = '';
        }
    }
}