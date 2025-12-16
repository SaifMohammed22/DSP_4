import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq, fftshift
from typing import List, Tuple, Dict, Optional
import math

def generate_signal(signal_type: str = 'sine',
                   frequency: float = 1e9,
                   sampling_rate: float = 10e9,
                   duration: float = 1e-6,
                   amplitude: float = 1.0,
                   phase: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate various types of signals.
    
    Args:
        signal_type: Type of signal ('sine', 'chirp', 'pulse', 'noise')
        frequency: Center frequency in Hz
        sampling_rate: Sampling rate in Hz
        duration: Signal duration in seconds
        amplitude: Signal amplitude
        phase: Initial phase in radians
    
    Returns:
        Time array and signal array
    """
    num_samples = int(sampling_rate * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    
    if signal_type == 'sine':
        # Sine wave
        s = amplitude * np.sin(2 * np.pi * frequency * t + phase)
    
    elif signal_type == 'chirp':
        # Linear chirp
        bandwidth = frequency * 0.1  # 10% bandwidth
        s = amplitude * signal.chirp(t, 
                                    frequency - bandwidth/2, 
                                    duration, 
                                    frequency + bandwidth/2)
    
    elif signal_type == 'pulse':
        # Gaussian pulse
        pulse_width = 1 / (frequency * 10)
        s = amplitude * np.exp(-(t - duration/2)**2 / (2 * pulse_width**2)) * \
            np.sin(2 * np.pi * frequency * t + phase)
    
    elif signal_type == 'noise':
        # White noise
        s = amplitude * np.random.normal(0, 1, num_samples)
    
    else:
        s = amplitude * np.sin(2 * np.pi * frequency * t + phase)
    
    return t, s

def apply_delay(signal_array: np.ndarray,
                delay: float,
                sampling_rate: float) -> np.ndarray:
    """
    Apply time delay to signal using frequency domain processing.
    
    Args:
        signal_array: Input signal
        delay: Time delay in seconds
        sampling_rate: Sampling rate in Hz
    
    Returns:
        Delayed signal
    """
    n = len(signal_array)
    
    # FFT of signal
    s_fft = fft(signal_array)
    
    # Frequency vector
    freqs = fftfreq(n, 1/sampling_rate)
    
    # Apply phase shift for delay
    phase_shift = np.exp(-2j * np.pi * freqs * delay)
    s_delayed_fft = s_fft * phase_shift
    
    # Inverse FFT
    s_delayed = np.real(ifft(s_delayed_fft))
    
    return s_delayed

def apply_phase_shift(signal_array: np.ndarray,
                     phase_shift: float) -> np.ndarray:
    """
    Apply phase shift to complex signal.
    
    Args:
        signal_array: Complex signal array
        phase_shift: Phase shift in radians
    
    Returns:
        Phase-shifted signal
    """
    return signal_array * np.exp(1j * phase_shift)

def calculate_spectrum(signal_array: np.ndarray,
                      sampling_rate: float,
                      window: str = 'hann') -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate power spectrum of signal.
    
    Args:
        signal_array: Input signal
        sampling_rate: Sampling rate in Hz
        window: Window function type
    
    Returns:
        Frequency array and power spectrum
    """
    n = len(signal_array)
    
    # Apply window
    if window == 'hann':
        win = np.hanning(n)
    elif window == 'hamming':
        win = np.hamming(n)
    elif window == 'blackman':
        win = np.blackman(n)
    else:
        win = np.ones(n)
    
    windowed = signal_array * win
    
    # Calculate FFT
    s_fft = fft(windowed)
    freqs = fftfreq(n, 1/sampling_rate)
    
    # Calculate power spectrum
    power = np.abs(s_fft)**2 / n
    
    # Shift zero frequency to center
    freqs_shifted = fftshift(freqs)
    power_shifted = fftshift(power)
    
    return freqs_shifted, power_shifted

def calculate_snr(signal_array: np.ndarray,
                 noise_power: Optional[float] = None) -> float:
    """
    Calculate Signal-to-Noise Ratio.
    
    Args:
        signal_array: Signal array
        noise_power: Optional noise power
    
    Returns:
        SNR in dB
    """
    signal_power = np.mean(np.abs(signal_array)**2)
    
    if noise_power is None:
        # Estimate noise from signal
        noise_power = np.var(signal_array)
    
    if noise_power == 0:
        return float('inf')
    
    snr_linear = signal_power / noise_power
    snr_db = 10 * np.log10(snr_linear)
    
    return snr_db

def add_noise(signal_array: np.ndarray,
             snr_db: float = 20.0,
             noise_type: str = 'gaussian') -> np.ndarray:
    """
    Add noise to signal with specified SNR.
    
    Args:
        signal_array: Input signal
        snr_db: Desired SNR in dB
        noise_type: Type of noise
    
    Returns:
        Noisy signal
    """
    signal_power = np.mean(np.abs(signal_array)**2)
    
    # Calculate noise power for desired SNR
    snr_linear = 10**(snr_db / 10)
    noise_power = signal_power / snr_linear
    
    # Generate noise
    if noise_type == 'gaussian':
        noise = np.random.normal(0, np.sqrt(noise_power), len(signal_array))
    elif noise_type == 'uniform':
        noise = np.random.uniform(-np.sqrt(3 * noise_power), 
                                 np.sqrt(3 * noise_power), 
                                 len(signal_array))
    elif noise_type == 'rayleigh':
        noise = np.random.rayleigh(np.sqrt(noise_power/2), len(signal_array))
    else:
        noise = np.random.normal(0, np.sqrt(noise_power), len(signal_array))
    
    return signal_array + noise

def apply_filter(signal_array: np.ndarray,
                filter_type: str,
                cutoff_freq: float,
                sampling_rate: float,
                order: int = 4) -> np.ndarray:
    """
    Apply digital filter to signal.
    
    Args:
        signal_array: Input signal
        filter_type: Type of filter ('lowpass', 'highpass', 'bandpass')
        cutoff_freq: Cutoff frequency
        sampling_rate: Sampling rate
        order: Filter order
    
    Returns:
        Filtered signal
    """
    nyquist = 0.5 * sampling_rate
    normal_cutoff = cutoff_freq / nyquist
    
    if filter_type == 'lowpass':
        b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    elif filter_type == 'highpass':
        b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    elif filter_type == 'bandpass':
        if isinstance(cutoff_freq, (list, tuple)) and len(cutoff_freq) == 2:
            low = cutoff_freq[0] / nyquist
            high = cutoff_freq[1] / nyquist
            b, a = signal.butter(order, [low, high], btype='band')
        else:
            raise ValueError("Bandpass filter requires two cutoff frequencies")
    else:
        raise ValueError(f"Unknown filter type: {filter_type}")
    
    filtered = signal.filtfilt(b, a, signal_array)
    return filtered

def calculate_correlation(signal1: np.ndarray,
                         signal2: np.ndarray) -> np.ndarray:
    """
    Calculate cross-correlation between two signals.
    
    Args:
        signal1: First signal
        signal2: Second signal
    
    Returns:
        Cross-correlation array
    """
    correlation = signal.correlate(signal1, signal2, mode='full', method='auto')
    return correlation

def calculate_convolution(signal1: np.ndarray,
                         signal2: np.ndarray) -> np.ndarray:
    """
    Calculate convolution of two signals.
    
    Args:
        signal1: First signal
        signal2: Second signal
    
    Returns:
        Convolution result
    """
    convolution = signal.convolve(signal1, signal2, mode='full')
    return convolution

def estimate_direction_of_arrival(signals: np.ndarray,
                                positions: np.ndarray,
                                frequency: float,
                                method: str = 'music') -> Dict:
    """
    Estimate Direction of Arrival using various methods.
    
    Args:
        signals: Array of signals from each element (num_elements x num_samples)
        positions: Element positions
        frequency: Signal frequency
        method: DOA estimation method
    
    Returns:
        DOA estimation results
    """
    num_elements, num_samples = signals.shape
    
    # Calculate correlation matrix
    R = np.zeros((num_elements, num_elements), dtype=complex)
    for i in range(num_elements):
        for j in range(num_elements):
            R[i, j] = np.mean(signals[i] * np.conj(signals[j]))
    
    # Eigenvalue decomposition
    eigenvalues, eigenvectors = np.linalg.eig(R)
    
    # Sort eigenvalues
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    if method == 'music':
        # MUSIC algorithm
        num_sources = 1  # Assume single source
        noise_subspace = eigenvectors[:, num_sources:]
        
        # Scan angles
        angles = np.linspace(-90, 90, 361)
        spectrum = np.zeros(len(angles))
        
        wavelength = 3e8 / frequency
        
        for i, angle in enumerate(np.radians(angles)):
            # Steering vector
            steering_vector = np.exp(-2j * np.pi / wavelength *
                                   (positions[:, 0] * np.sin(angle) +
                                    positions[:, 1] * np.cos(angle)))
            
            # MUSIC spectrum
            spectrum[i] = 1 / np.abs(steering_vector.conj() @ 
                                   noise_subspace @ 
                                   noise_subspace.conj().T @ 
                                   steering_vector)
        
        # Find peaks
        peak_idx = signal.find_peaks(spectrum, height=np.mean(spectrum))[0]
        doa_angles = angles[peak_idx]
        
        return {
            'angles': angles.tolist(),
            'spectrum': spectrum.tolist(),
            'estimated_doa': doa_angles.tolist()[:3],  # Top 3 estimates
            'method': 'music',
            'eigenvalues': eigenvalues.tolist()
        }
    
    elif method == 'beamforming':
        # Conventional beamforming
        angles = np.linspace(-90, 90, 361)
        spectrum = np.zeros(len(angles))
        
        wavelength = 3e8 / frequency
        
        for i, angle in enumerate(np.radians(angles)):
            # Steering vector
            steering_vector = np.exp(-2j * np.pi / wavelength *
                                   (positions[:, 0] * np.sin(angle) +
                                    positions[:, 1] * np.cos(angle)))
            
            # Bartlett spectrum
            spectrum[i] = np.abs(steering_vector.conj() @ R @ steering_vector)
        
        # Find peak
        peak_idx = np.argmax(spectrum)
        doa_angle = angles[peak_idx]
        
        return {
            'angles': angles.tolist(),
            'spectrum': spectrum.tolist(),
            'estimated_doa': [float(doa_angle)],
            'method': 'beamforming'
        }
    
    else:
        raise ValueError(f"Unknown DOA method: {method}")

def calculate_beamforming_weights(positions: np.ndarray,
                                frequency: float,
                                steering_angle: float,
                                method: str = 'conventional') -> np.ndarray:
    """
    Calculate beamforming weights.
    
    Args:
        positions: Element positions
        frequency: Signal frequency
        steering_angle: Desired steering angle
        method: Weight calculation method
    
    Returns:
        Complex weights for each element
    """
    num_elements = len(positions)
    wavelength = 3e8 / frequency
    steering_rad = np.radians(steering_angle)
    
    if method == 'conventional':
        # Conventional beamforming (delay-and-sum)
        weights = np.ones(num_elements, dtype=complex)
        
        for i, pos in enumerate(positions):
            phase = 2 * np.pi / wavelength * (pos[0] * np.sin(steering_rad) +
                                            pos[1] * np.cos(steering_rad))
            weights[i] = np.exp(-1j * phase)
    
    elif method == 'mvdr':
        # Minimum Variance Distortionless Response
        # Simplified implementation
        steering_vector = np.exp(1j * 2 * np.pi / wavelength *
                               (positions[:, 0] * np.sin(steering_rad) +
                                positions[:, 1] * np.cos(steering_rad)))
        
        # Assume identity interference matrix for simplicity
        R_inv = np.eye(num_elements)
        
        weights = (R_inv @ steering_vector) / \
                 (steering_vector.conj() @ R_inv @ steering_vector)
    
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return weights

def simulate_propagation_channel(distance: float,
                               frequency: float,
                               environment: str = 'free_space') -> Dict:
    """
    Simulate signal propagation through channel.
    
    Args:
        distance: Propagation distance
        frequency: Signal frequency
        environment: Propagation environment
    
    Returns:
        Channel parameters
    """
    wavelength = 3e8 / frequency
    
    if environment == 'free_space':
        # Free space path loss
        path_loss = (wavelength / (4 * np.pi * distance))**2
        phase_shift = 2 * np.pi * distance / wavelength
    
    elif environment == 'urban':
        # Urban environment with additional loss
        path_loss = (wavelength / (4 * np.pi * distance))**2 * \
                   (distance / 1000)**-3.5  # Additional urban loss
        phase_shift = 2 * np.pi * distance / wavelength
    
    elif environment == 'multipath':
        # Multipath with Rician fading
        K = 10  # Rician K-factor
        direct_path = np.sqrt(K/(K+1))
        scattered_path = np.sqrt(1/(2*(K+1))) * \
                        (np.random.randn() + 1j * np.random.randn())
        
        channel = direct_path + scattered_path
        path_loss = np.abs(channel)**2 * (wavelength / (4 * np.pi * distance))**2
        phase_shift = np.angle(channel) + 2 * np.pi * distance / wavelength
    
    else:
        path_loss = (wavelength / (4 * np.pi * distance))**2
        phase_shift = 2 * np.pi * distance / wavelength
    
    return {
        'path_loss_db': float(10 * np.log10(path_loss)),
        'path_loss_linear': float(path_loss),
        'phase_shift_rad': float(phase_shift),
        'delay': float(distance / 3e8),
        'distance': float(distance),
        'wavelength': float(wavelength)
    }