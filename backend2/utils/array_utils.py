import numpy as np
from typing import List, Tuple, Dict, Optional
from enum import Enum

class ArrayGeometry(Enum):
    LINEAR = "linear"
    CURVED = "curved"
    CIRCULAR = "circular"
    RECTANGULAR = "rectangular"
    SPIRAL = "spiral"
    RANDOM = "random"

def generate_array_positions(geometry: ArrayGeometry, 
                           num_elements: int, 
                           spacing: float = 0.5,
                           curvature: float = 0.0,
                           orientation: float = 0.0) -> np.ndarray:
    """
    Generate element positions for different array geometries.
    
    Args:
        geometry: Type of array geometry
        num_elements: Number of array elements
        spacing: Element spacing in wavelengths
        curvature: Curvature parameter for curved arrays
        orientation: Array orientation in degrees
    
    Returns:
        Array of element positions (num_elements x 2)
    """
    positions = None
    
    if geometry == ArrayGeometry.LINEAR:
        positions = _generate_linear_positions(num_elements, spacing)
    elif geometry == ArrayGeometry.CURVED:
        positions = _generate_curved_positions(num_elements, spacing, curvature)
    elif geometry == ArrayGeometry.CIRCULAR:
        positions = _generate_circular_positions(num_elements, spacing)
    elif geometry == ArrayGeometry.RECTANGULAR:
        positions = _generate_rectangular_positions(num_elements, spacing)
    elif geometry == ArrayGeometry.SPIRAL:
        positions = _generate_spiral_positions(num_elements, spacing)
    elif geometry == ArrayGeometry.RANDOM:
        positions = _generate_random_positions(num_elements, spacing)
    else:
        positions = _generate_linear_positions(num_elements, spacing)
    
    # Apply orientation
    if orientation != 0:
        positions = _apply_rotation(positions, orientation)
    
    return positions

def _generate_linear_positions(num_elements: int, spacing: float) -> np.ndarray:
    """Generate positions for linear array"""
    positions = np.zeros((num_elements, 2))
    for i in range(num_elements):
        positions[i, 0] = (i - (num_elements - 1) / 2) * spacing
    return positions

def _generate_curved_positions(num_elements: int, spacing: float, curvature: float) -> np.ndarray:
    """Generate positions for curved array"""
    if curvature == 0:
        return _generate_linear_positions(num_elements, spacing)
    
    radius = 1.0 / curvature
    arc_length = (num_elements - 1) * spacing
    angle = arc_length / radius
    
    positions = np.zeros((num_elements, 2))
    angles = np.linspace(-angle/2, angle/2, num_elements)
    
    for i, theta in enumerate(angles):
        positions[i, 0] = radius * np.sin(theta)
        positions[i, 1] = radius * (1 - np.cos(theta))
    
    return positions

def _generate_circular_positions(num_elements: int, spacing: float) -> np.ndarray:
    """Generate positions for circular array"""
    radius = spacing * num_elements / (2 * np.pi)
    angles = np.linspace(0, 2 * np.pi, num_elements, endpoint=False)
    
    positions = np.zeros((num_elements, 2))
    positions[:, 0] = radius * np.cos(angles)
    positions[:, 1] = radius * np.sin(angles)
    
    return positions

def _generate_rectangular_positions(num_elements: int, spacing: float) -> np.ndarray:
    """Generate positions for rectangular array"""
    # Try to make it as square as possible
    rows = int(np.sqrt(num_elements))
    cols = int(np.ceil(num_elements / rows))
    
    positions = np.zeros((num_elements, 2))
    idx = 0
    
    for i in range(rows):
        for j in range(cols):
            if idx >= num_elements:
                break
            positions[idx, 0] = (j - (cols - 1) / 2) * spacing
            positions[idx, 1] = (i - (rows - 1) / 2) * spacing
            idx += 1
    
    return positions[:num_elements]

def _generate_spiral_positions(num_elements: int, spacing: float) -> np.ndarray:
    """Generate positions for spiral array"""
    positions = np.zeros((num_elements, 2))
    
    for i in range(num_elements):
        angle = i * 2 * np.pi / (num_elements / 2)
        radius = spacing * i / (2 * np.pi)
        positions[i, 0] = radius * np.cos(angle)
        positions[i, 1] = radius * np.sin(angle)
    
    # Center the spiral
    positions -= np.mean(positions, axis=0)
    
    return positions

def _generate_random_positions(num_elements: int, spacing: float) -> np.ndarray:
    """Generate random positions with minimum spacing"""
    positions = np.zeros((num_elements, 2))
    
    for i in range(num_elements):
        attempts = 0
        while attempts < 100:
            # Random position within bounds
            x = np.random.uniform(-spacing * num_elements/2, spacing * num_elements/2)
            y = np.random.uniform(-spacing * num_elements/2, spacing * num_elements/2)
            
            # Check minimum distance from other elements
            if i == 0:
                positions[i] = [x, y]
                break
            else:
                distances = np.sqrt(np.sum((positions[:i] - [x, y])**2, axis=1))
                if np.all(distances > spacing * 0.5):
                    positions[i] = [x, y]
                    break
            
            attempts += 1
        
        if attempts == 100:
            # Fallback to grid position
            positions[i] = [(i % int(np.sqrt(num_elements)) - int(np.sqrt(num_elements))/2) * spacing,
                          (i // int(np.sqrt(num_elements)) - int(np.sqrt(num_elements))/2) * spacing]
    
    return positions

def _apply_rotation(positions: np.ndarray, angle_deg: float) -> np.ndarray:
    """Rotate array positions by given angle"""
    angle_rad = np.radians(angle_deg)
    rotation_matrix = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad)],
        [np.sin(angle_rad), np.cos(angle_rad)]
    ])
    
    return positions @ rotation_matrix.T

def calculate_steering_delays(positions: np.ndarray, 
                            steering_angle: float, 
                            wavelength: float,
                            propagation_speed: float = 3e8) -> np.ndarray:
    """
    Calculate time delays for beam steering.
    
    Args:
        positions: Array element positions (num_elements x 2)
        steering_angle: Desired steering angle in degrees
        wavelength: Signal wavelength
        propagation_speed: Wave propagation speed
    
    Returns:
        Array of time delays for each element
    """
    steering_rad = np.radians(steering_angle)
    
    # Calculate phase shifts
    phase_shifts = (positions[:, 0] * np.sin(steering_rad) + 
                   positions[:, 1] * np.cos(steering_rad)) / wavelength
    
    # Convert to time delays
    delays = phase_shifts * wavelength / propagation_speed
    
    # Normalize to remove negative delays
    delays -= np.min(delays)
    
    return delays

def calculate_array_factor(positions: np.ndarray,
                         frequencies: List[float],
                         steering_angle: float = 0.0,
                         weights: Optional[np.ndarray] = None) -> callable:
    """
    Calculate array factor function for given array.
    
    Args:
        positions: Element positions
        frequencies: List of operating frequencies
        steering_angle: Beam steering angle
        weights: Element weights (amplitudes)
    
    Returns:
        Function that calculates array factor at given angles
    """
    if weights is None:
        weights = np.ones(len(positions))
    
    def array_factor(theta: np.ndarray, phi: np.ndarray = 0.0) -> np.ndarray:
        """
        Calculate array factor at given direction.
        
        Args:
            theta: Elevation angle (radians)
            phi: Azimuth angle (radians)
        
        Returns:
            Array factor magnitude
        """
        theta = np.asarray(theta)
        phi = np.asarray(phi)
        
        # Initialize result
        result = np.zeros_like(theta, dtype=complex)
        
        # Calculate for each frequency
        for freq in frequencies:
            wavelength = 3e8 / freq
            
            # Calculate steering vector
            steering_vector = np.exp(1j * 2 * np.pi / wavelength *
                                   (positions[:, 0] * np.sin(theta) * np.cos(phi) +
                                    positions[:, 1] * np.sin(theta) * np.sin(phi)))
            
            # Apply weights and sum
            result += np.sum(weights * steering_vector, axis=1)
        
        return np.abs(result)
    
    return array_factor

def calculate_beamwidth(array_factor: callable, 
                       frequency: float,
                       main_lobe_direction: float = 0.0) -> Dict:
    """
    Calculate beamwidth parameters.
    
    Args:
        array_factor: Array factor function
        frequency: Operating frequency
        main_lobe_direction: Direction of main lobe (radians)
    
    Returns:
        Dictionary with beamwidth parameters
    """
    # Sample angles around main lobe
    angles = np.linspace(-np.pi/2, np.pi/2, 1000)
    
    # Calculate array factor
    af_values = array_factor(angles)
    
    # Find main lobe
    main_lobe_idx = np.argmax(af_values)
    main_lobe_value = af_values[main_lobe_idx]
    
    # Find -3dB points
    half_power = main_lobe_value / np.sqrt(2)
    
    left_idx = np.where(af_values[:main_lobe_idx] <= half_power)[0]
    right_idx = np.where(af_values[main_lobe_idx:] <= half_power)[0]
    
    if len(left_idx) > 0:
        left_angle = angles[left_idx[-1]]
    else:
        left_angle = angles[0]
    
    if len(right_idx) > 0:
        right_angle = angles[main_lobe_idx + right_idx[0]]
    else:
        right_angle = angles[-1]
    
    # Calculate beamwidth
    beamwidth = np.abs(right_angle - left_angle)
    
    # Convert to degrees
    beamwidth_deg = np.degrees(beamwidth)
    left_angle_deg = np.degrees(left_angle)
    right_angle_deg = np.degrees(right_angle)
    
    return {
        'beamwidth_rad': float(beamwidth),
        'beamwidth_deg': float(beamwidth_deg),
        'left_angle_deg': float(left_angle_deg),
        'right_angle_deg': float(right_angle_deg),
        'main_lobe_direction_deg': float(np.degrees(main_lobe_direction)),
        'main_lobe_gain': float(main_lobe_value)
    }

def calculate_sidelobe_levels(array_factor: callable, 
                            frequency: float) -> Dict:
    """
    Calculate sidelobe levels.
    
    Args:
        array_factor: Array factor function
        frequency: Operating frequency
    
    Returns:
        Dictionary with sidelobe information
    """
    angles = np.linspace(-np.pi, np.pi, 2000)
    af_values = array_factor(angles)
    
    # Find peaks (sidelobes)
    from scipy.signal import find_peaks
    peaks, properties = find_peaks(af_values, height=0.1)
    
    # Sort peaks by height
    peak_heights = af_values[peaks]
    sorted_indices = np.argsort(peak_heights)[::-1]
    
    # Main lobe is the highest peak
    main_lobe_height = peak_heights[sorted_indices[0]]
    
    sidelobes = []
    for idx in sorted_indices[1:6]:  # Top 5 sidelobes
        sidelobes.append({
            'angle_deg': float(np.degrees(angles[peaks[idx]])),
            'level_db': float(20 * np.log10(peak_heights[idx] / main_lobe_height)),
            'relative_power': float(peak_heights[idx] / main_lobe_height)
        })
    
    # Calculate peak sidelobe level (PSL)
    if len(sidelobes) > 0:
        psl = max(sl['level_db'] for sl in sidelobes)
    else:
        psl = -np.inf
    
    return {
        'peak_sidelobe_level_db': float(psl),
        'sidelobes': sidelobes,
        'main_lobe_level_db': 0.0
    }

def optimize_array_weights(positions: np.ndarray,
                         frequency: float,
                         steering_angle: float = 0.0,
                         method: str = 'uniform') -> np.ndarray:
    """
    Optimize array weights for given criteria.
    
    Args:
        positions: Element positions
        frequency: Operating frequency
        steering_angle: Desired steering angle
        method: Optimization method ('uniform', 'chebyshev', 'taylor')
    
    Returns:
        Optimized weights
    """
    num_elements = len(positions)
    
    if method == 'uniform':
        return np.ones(num_elements)
    
    elif method == 'chebyshev':
        # Chebyshev window for sidelobe control
        from scipy.signal import chebwin
        return chebwin(num_elements, at=40)  # 40dB sidelobe attenuation
    
    elif method == 'taylor':
        # Taylor window
        from scipy.signal import taylor
        return taylor(num_elements, nbar=4, sll=30)
    
    elif method == 'hamming':
        return np.hamming(num_elements)
    
    elif method == 'hanning':
        return np.hanning(num_elements)
    
    else:
        return np.ones(num_elements)

def calculate_grating_lobes(positions: np.ndarray,
                          frequency: float,
                          steering_angle: float = 0.0) -> List[Dict]:
    """
    Calculate grating lobe locations.
    
    Args:
        positions: Element positions
        frequency: Operating frequency
        steering_angle: Steering angle
    
    Returns:
        List of grating lobe locations
    """
    wavelength = 3e8 / frequency
    steering_rad = np.radians(steering_angle)
    
    # For linear arrays along x-axis
    if np.all(positions[:, 1] == 0):  # Linear array
        dx = np.diff(np.sort(positions[:, 0]))
        if len(dx) > 0:
            avg_spacing = np.mean(dx)
            
            grating_lobes = []
            n = 1
            while True:
                # Grating lobe condition
                sin_theta_gl = np.sin(steering_rad) + n * wavelength / avg_spacing
                
                if abs(sin_theta_gl) > 1:
                    break
                
                theta_gl = np.degrees(np.arcsin(sin_theta_gl))
                grating_lobes.append({
                    'order': n,
                    'angle_deg': theta_gl,
                    'sin_angle': sin_theta_gl
                })
                
                n += 1
            
            return grating_lobes
    
    return []

def calculate_mutual_coupling(positions: np.ndarray,
                            frequency: float,
                            element_type: str = 'dipole') -> np.ndarray:
    """
    Estimate mutual coupling matrix.
    
    Args:
        positions: Element positions
        frequency: Operating frequency
        element_type: Type of antenna element
    
    Returns:
        Coupling matrix (num_elements x num_elements)
    """
    num_elements = len(positions)
    wavelength = 3e8 / frequency
    coupling_matrix = np.eye(num_elements, dtype=complex)
    
    for i in range(num_elements):
        for j in range(i+1, num_elements):
            distance = np.linalg.norm(positions[i] - positions[j])
            
            if distance == 0:
                continue
            
            # Simple coupling model based on distance
            phase = 2 * np.pi * distance / wavelength
            magnitude = 1 / (1 + (distance / wavelength)**2)
            
            coupling = magnitude * np.exp(-1j * phase)
            coupling_matrix[i, j] = coupling
            coupling_matrix[j, i] = coupling  # Symmetric
    
    return coupling_matrix

def analyze_array_performance(positions: np.ndarray,
                            frequency: float,
                            steering_angle: float = 0.0,
                            weights: Optional[np.ndarray] = None) -> Dict:
    """
    Comprehensive array performance analysis.
    
    Args:
        positions: Element positions
        frequency: Operating frequency
        steering_angle: Steering angle
        weights: Element weights
    
    Returns:
        Dictionary with performance metrics
    """
    if weights is None:
        weights = np.ones(len(positions))
    
    # Create array factor function
    array_factor = calculate_array_factor(positions, [frequency], steering_angle, weights)
    
    # Calculate beamwidth
    beamwidth_data = calculate_beamwidth(array_factor, frequency, np.radians(steering_angle))
    
    # Calculate sidelobe levels
    sidelobe_data = calculate_sidelobe_levels(array_factor, frequency)
    
    # Calculate directivity
    # Simple approximation: directivity ≈ 4π / beamwidth (for uniform array)
    beamwidth_rad = beamwidth_data['beamwidth_rad']
    if beamwidth_rad > 0:
        directivity = 4 * np.pi / (beamwidth_rad * beamwidth_rad)
    else:
        directivity = 1.0
    
    # Calculate efficiency
    total_power = np.sum(np.abs(weights)**2)
    if len(weights) > 0:
        efficiency = np.abs(np.sum(weights))**2 / (len(weights) * total_power)
    else:
        efficiency = 1.0
    
    # Calculate grating lobes
    grating_lobes = calculate_grating_lobes(positions, frequency, steering_angle)
    
    # Estimate mutual coupling
    coupling_matrix = calculate_mutual_coupling(positions, frequency)
    
    return {
        'beamwidth': beamwidth_data,
        'sidelobes': sidelobe_data,
        'directivity_db': float(10 * np.log10(directivity)),
        'efficiency': float(efficiency),
        'grating_lobes': grating_lobes,
        'coupling_matrix': coupling_matrix.tolist(),
        'num_elements': len(positions),
        'array_aperture': float(np.max(positions[:, 0]) - np.min(positions[:, 0])),
        'element_spacing': float(np.mean(np.diff(np.sort(positions[:, 0])))) if len(positions) > 1 else 0.0
    }