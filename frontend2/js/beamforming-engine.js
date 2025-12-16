// Beamforming Engine - Handles beamforming calculations and signal processing
class BeamformingEngine {
    constructor(app) {
        this.app = app;
        this.cache = new Map();
        this.worker = null;
        
        // Initialize calculation methods
        this.methods = {
            conventional: this.conventionalBeamforming.bind(this),
            mvdr: this.mvdrBeamforming.bind(this),
            music: this.musicAlgorithm.bind(this)
        };
    }
    
    async runSimulation(simulationData) {
        console.log('Running beamforming simulation...');
        
        try {
            // Validate input
            this.validateSimulationData(simulationData);
            
            // Calculate beam pattern
            const beamPattern = await this.calculateBeamPattern(simulationData);
            
            // Calculate interference map
            const interferenceMap = await this.calculateInterferenceMap(simulationData);
            
            // Calculate array geometry
            const arrayGeometry = this.calculateArrayGeometry(simulationData.arrays);
            
            // Combine results
            const results = {
                beamPattern,
                interferenceMap,
                arrayGeometry,
                parameters: simulationData.parameters,
                timestamp: Date.now()
            };
            
            // Cache results
            this.cacheResults(simulationData, results);
            
            return results;
            
        } catch (error) {
            console.error('Beamforming simulation failed:', error);
            throw error;
        }
    }
    
    validateSimulationData(data) {
        const { parameters, arrays } = data;
        
        // Validate frequency
        if (parameters.frequency <= 0 || parameters.frequency > 100e9) {
            throw new Error('Frequency must be between 1 Hz and 100 GHz');
        }
        
        // Validate number of elements
        if (parameters.numElements < 2 || parameters.numElements > 256) {
            throw new Error('Number of elements must be between 2 and 256');
        }
        
        // Validate element spacing
        if (parameters.elementSpacing < 0.1 || parameters.elementSpacing > 2) {
            throw new Error('Element spacing must be between 0.1λ and 2λ');
        }
        
        // Validate arrays
        if (!arrays || arrays.length === 0) {
            throw new Error('At least one array must be specified');
        }
    }
    
    async calculateBeamPattern(simulationData) {
        const cacheKey = this.generateCacheKey('beamPattern', simulationData);
        
        // Check cache
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }
        
        const { parameters, arrays } = simulationData;
        const { frequency, numElements, elementSpacing, steeringAngle } = parameters;
        
        // Calculate wavelength
        const wavelength = parameters.propagationSpeed / frequency;
        
        // Create grid for beam pattern
        const gridSize = 200;
        const gridRange = 10; // meters
        const X = this.createGrid(gridSize, gridRange);
        const Y = this.createGrid(gridSize, gridRange);
        
        // Initialize beam pattern
        let totalPattern = this.createZeroGrid(gridSize, gridSize);
        
        // Calculate pattern for each array
        for (const array of arrays) {
            if (!array.active) continue;
            
            const arrayPattern = await this.calculateArrayPattern(
                array, parameters, X, Y, wavelength
            );
            
            // Combine patterns
            totalPattern = this.combinePatterns(totalPattern, arrayPattern);
        }
        
        // Normalize pattern
        totalPattern = this.normalizePattern(totalPattern);
        
        const result = {
            magnitude: totalPattern,
            X: X.mesh,
            Y: Y.mesh,
            wavelength,
            gridSize,
            gridRange
        };
        
        // Cache result
        this.cache.set(cacheKey, result);
        
        return result;
    }
    
    async calculateArrayPattern(array, parameters, X, Y, wavelength) {
        const { type, numElements, spacing, position, orientation } = array;
        const { steeringAngle, phaseShift } = parameters;
        
        // Calculate element positions
        const elementPositions = this.calculateElementPositions(
            type, numElements, spacing * wavelength, position, orientation
        );
        
        // Calculate steering vector
        const steeringVector = this.calculateSteeringVector(
            elementPositions, wavelength, steeringAngle, phaseShift
        );
        
        // Calculate array factor
        const arrayFactor = this.calculateArrayFactor(
            elementPositions, steeringVector, X, Y, wavelength
        );
        
        return arrayFactor;
    }
    
    calculateElementPositions(type, numElements, spacing, position, orientation) {
        const positions = [];
        const centerX = position.x;
        const centerY = position.y;
        const angleRad = (orientation * Math.PI) / 180;
        
        switch (type) {
            case 'linear':
                for (let i = 0; i < numElements; i++) {
                    const x = centerX + (i - (numElements - 1) / 2) * spacing;
                    const y = centerY;
                    
                    // Apply rotation
                    const rotatedX = x * Math.cos(angleRad) - y * Math.sin(angleRad);
                    const rotatedY = x * Math.sin(angleRad) + y * Math.cos(angleRad);
                    
                    positions.push([rotatedX, rotatedY]);
                }
                break;
                
            case 'curved':
                // Curved array (arc)
                const radius = spacing * numElements / Math.PI;
                const arcAngle = Math.PI / 3; // 60 degree arc
                
                for (let i = 0; i < numElements; i++) {
                    const theta = (i - (numElements - 1) / 2) * (arcAngle / (numElements - 1));
                    const x = centerX + radius * Math.sin(theta);
                    const y = centerY + radius * (1 - Math.cos(theta));
                    
                    positions.push([x, y]);
                }
                break;
                
            case 'circular':
                // Circular array
                const circleRadius = spacing * numElements / (2 * Math.PI);
                
                for (let i = 0; i < numElements; i++) {
                    const angle = (2 * Math.PI * i) / numElements;
                    const x = centerX + circleRadius * Math.cos(angle);
                    const y = centerY + circleRadius * Math.sin(angle);
                    
                    positions.push([x, y]);
                }
                break;
        }
        
        return positions;
    }
    
    calculateSteeringVector(elementPositions, wavelength, steeringAngle, phaseShift) {
        const steeringRad = (steeringAngle * Math.PI) / 180;
        const phaseShiftRad = (phaseShift * Math.PI) / 180;
        
        return elementPositions.map(([x, y]) => {
            const phase = (2 * Math.PI / wavelength) * (x * Math.sin(steeringRad) + y * Math.cos(steeringRad));
            return Math.cos(phase + phaseShiftRad) + 1j * Math.sin(phase + phaseShiftRad);
        });
    }
    
    calculateArrayFactor(elementPositions, steeringVector, X, Y, wavelength) {
        const gridSize = X.mesh.length;
        const arrayFactor = this.createZeroGrid(gridSize, gridSize);
        
        // Calculate array factor for each grid point
        for (let i = 0; i < gridSize; i++) {
            for (let j = 0; j < gridSize; j++) {
                let sum = 0;
                
                for (let k = 0; k < elementPositions.length; k++) {
                    const [x_k, y_k] = elementPositions[k];
                    const w_k = steeringVector[k];
                    
                    // Distance from element to grid point
                    const dx = X.mesh[i][j] - x_k;
                    const dy = Y.mesh[i][j] - y_k;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    
                    // Phase delay
                    const phase = (2 * Math.PI / wavelength) * distance;
                    
                    // Add contribution
                    sum += w_k * (Math.cos(phase) + 1j * Math.sin(phase));
                }
                
                arrayFactor[i][j] = Math.abs(sum);
            }
        }
        
        return arrayFactor;
    }
    
    async calculateInterferenceMap(simulationData) {
        const cacheKey = this.generateCacheKey('interference', simulationData);
        
        // Check cache
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }
        
        const { parameters } = simulationData;
        const { frequency } = parameters;
        const wavelength = parameters.propagationSpeed / frequency;
        
        // Create grid
        const gridSize = 200;
        const gridRange = 10;
        const X = this.createGrid(gridSize, gridRange);
        const Y = this.createGrid(gridSize, gridRange);
        
        // Initialize interference map
        const interference = this.createZeroGrid(gridSize, gridSize);
        
        // Add source interference
        const sourcePosition = [parameters.txPosition.x, parameters.txPosition.y];
        this.addSourceInterference(interference, X, Y, sourcePosition, wavelength);
        
        // Add random interference sources
        this.addRandomInterference(interference, X, Y, wavelength);
        
        const result = {
            interference,
            X: X.mesh,
            Y: Y.mesh,
            sources: [sourcePosition],
            gridSize,
            gridRange
        };
        
        // Cache result
        this.cache.set(cacheKey, result);
        
        return result;
    }
    
    addSourceInterference(interference, X, Y, sourcePosition, wavelength) {
        const gridSize = interference.length;
        const [sourceX, sourceY] = sourcePosition;
        
        for (let i = 0; i < gridSize; i++) {
            for (let j = 0; j < gridSize; j++) {
                const dx = X.mesh[i][j] - sourceX;
                const dy = Y.mesh[i][j] - sourceY;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                // Spherical wave propagation
                const amplitude = 1 / (1 + distance);
                const phase = (2 * Math.PI / wavelength) * distance;
                
                interference[i][j] += amplitude * Math.cos(phase);
            }
        }
    }
    
    addRandomInterference(interference, X, Y, wavelength) {
        const gridSize = interference.length;
        const numInterferers = 3;
        
        for (let n = 0; n < numInterferers; n++) {
            const sourceX = (Math.random() - 0.5) * 20;
            const sourceY = (Math.random() - 0.5) * 20;
            const amplitude = 0.3 + Math.random() * 0.7;
            
            for (let i = 0; i < gridSize; i++) {
                for (let j = 0; j < gridSize; j++) {
                    const dx = X.mesh[i][j] - sourceX;
                    const dy = Y.mesh[i][j] - sourceY;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    
                    const phase = (2 * Math.PI / wavelength) * distance;
                    interference[i][j] += amplitude * Math.cos(phase) / (1 + distance);
                }
            }
        }
    }
    
    calculateArrayGeometry(arrays) {
        const activeArray = arrays.find(array => array.active) || arrays[0];
        
        return {
            positions: this.calculateElementPositions(
                activeArray.type,
                activeArray.numElements,
                activeArray.spacing * (3e8 / 2.4e9), // Use wavelength at 2.4 GHz
                activeArray.position,
                activeArray.orientation
            ),
            type: activeArray.type,
            numElements: activeArray.numElements,
            spacing: activeArray.spacing
        };
    }
    
    // Utility methods
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
    
    combinePatterns(pattern1, pattern2) {
        const rows = pattern1.length;
        const cols = pattern1[0].length;
        const result = this.createZeroGrid(rows, cols);
        
        for (let i = 0; i < rows; i++) {
            for (let j = 0; j < cols; j++) {
                result[i][j] = pattern1[i][j] + pattern2[i][j];
            }
        }
        
        return result;
    }
    
    normalizePattern(pattern) {
        const maxVal = Math.max(...pattern.flat());
        if (maxVal === 0) return pattern;
        
        return pattern.map(row => row.map(val => val / maxVal));
    }
    
    generateCacheKey(type, data) {
        // Create a simple hash for caching
        const str = JSON.stringify({
            type,
            parameters: data.parameters,
            arrays: data.arrays,
            scenario: data.scenario
        });
        
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = ((hash << 5) - hash) + str.charCodeAt(i);
            hash |= 0; // Convert to 32bit integer
        }
        
        return hash.toString(16);
    }
    
    cacheResults(key, results) {
        // Limit cache size
        if (this.cache.size > 100) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        
        this.cache.set(key, results);
    }
    
    // Beamforming algorithms
    conventionalBeamforming(elementPositions, wavelength, steeringAngle) {
        // Conventional delay-and-sum beamforming
        const steeringRad = (steeringAngle * Math.PI) / 180;
        const weights = [];
        
        for (const [x, y] of elementPositions) {
            const phase = (2 * Math.PI / wavelength) * (x * Math.sin(steeringRad) + y * Math.cos(steeringRad));
            weights.push(Math.cos(phase) - 1j * Math.sin(phase)); // Negative for compensation
        }
        
        return weights;
    }
    
    mvdrBeamforming(elementPositions, wavelength, steeringAngle, interferenceMatrix) {
        // Minimum Variance Distortionless Response beamforming
        const steeringVector = this.calculateSteeringVector(elementPositions, wavelength, steeringAngle, 0);
        
        // Calculate MVDR weights
        // w = R^-1 * a / (a^H * R^-1 * a)
        
        // For simplicity, return conventional weights
        // In a real implementation, you would calculate the covariance matrix
        return steeringVector;
    }
    
    musicAlgorithm(elementPositions, signals, wavelength) {
        // MUSIC algorithm for DOA estimation
        // This is a simplified version
        
        // Calculate correlation matrix
        const numElements = elementPositions.length;
        const R = this.createZeroGrid(numElements, numElements);
        
        for (let i = 0; i < numElements; i++) {
            for (let j = 0; j < numElements; j++) {
                R[i][j] = signals[i] * Math.conj(signals[j]);
            }
        }
        
        // Return dummy spectrum
        return Array.from({ length: 181 }, (_, i) => Math.random());
    }
    
    // Helper for complex numbers
    get 1j() {
        return { re: 0, im: 1 };
    }
}

// Add complex number support
Math.conj = function(z) {
    if (typeof z === 'number') return z;
    return { re: z.re, im: -z.im };
};