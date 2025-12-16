import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from io import BytesIO
import base64
from typing import List, Tuple, Dict, Optional, Union
import json

# Set matplotlib style
plt.style.use('seaborn-v0_8-darkgrid')

def plot_beam_pattern(magnitude: np.ndarray, 
                     X: np.ndarray, 
                     Y: np.ndarray,
                     title: str = "Beam Pattern",
                     colorbar_label: str = "Normalized Magnitude (dB)",
                     include_contours: bool = True) -> str:
    """
    Create 2D plot of beam pattern and return as base64 encoded string.
    
    Args:
        magnitude: Beam pattern magnitude (2D array)
        X: X coordinates (2D array)
        Y: Y coordinates (2D array)
        title: Plot title
        colorbar_label: Label for colorbar
        include_contours: Whether to include contour lines
    
    Returns:
        Base64 encoded PNG image string
    """
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Convert to dB for better visualization
    magnitude_db = 10 * np.log10(magnitude + 1e-10)  # Add small value to avoid log(0)
    
    # Create custom colormap (blue to red)
    colors = [(0, 0, 0.5), (0, 0, 1), (0, 1, 1), (1, 1, 0), (1, 0, 0)]
    cmap = LinearSegmentedColormap.from_list('beam_cmap', colors, N=256)
    
    # Plot beam pattern
    im = ax.contourf(X, Y, magnitude_db, 
                     levels=100, 
                     cmap=cmap, 
                     alpha=0.9,
                     vmin=magnitude_db.min(),
                     vmax=magnitude_db.max())
    
    # Add contour lines
    if include_contours:
        contour_levels = np.linspace(magnitude_db.min(), magnitude_db.max(), 20)
        ax.contour(X, Y, magnitude_db, 
                  levels=contour_levels,
                  colors='white', 
                  linewidths=0.5, 
                  alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label(colorbar_label, fontsize=12)
    
    # Mark array position
    ax.plot(0, 0, 'k*', markersize=15, label='Array Center')
    
    # Plot settings
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('X (meters)', fontsize=12)
    ax.set_ylabel('Y (meters)', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axis('equal')
    ax.legend(loc='upper right')
    
    # Add text with min/max values
    text_str = f"Max: {magnitude.max():.2f}\nMin: {magnitude.min():.2e}"
    ax.text(0.02, 0.98, text_str, 
            transform=ax.transAxes, 
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Convert to base64
    img_data = _fig_to_base64(fig)
    plt.close(fig)
    
    return img_data

def plot_interference_map(interference: np.ndarray,
                         X: np.ndarray,
                         Y: np.ndarray,
                         title: str = "Interference Map",
                         source_positions: List[List[float]] = None) -> str:
    """
    Create interference map plot.
    
    Args:
        interference: Interference values (2D array)
        X: X coordinates (2D array)
        Y: Y coordinates (2D array)
        title: Plot title
        source_positions: List of source positions to plot
    
    Returns:
        Base64 encoded PNG image string
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Use log scale for better visualization
    interference_log = np.log10(interference + 1e-10)
    
    # Plot interference
    im = ax.contourf(X, Y, interference_log, 
                     levels=100, 
                     cmap='plasma', 
                     alpha=0.9)
    
    # Add contour lines
    contour_levels = np.linspace(interference_log.min(), interference_log.max(), 10)
    ax.contour(X, Y, interference_log, 
               levels=contour_levels,
               colors='white', 
               linewidths=0.5, 
               alpha=0.5)
    
    # Mark sources if provided
    if source_positions:
        for i, (x, y) in enumerate(source_positions):
            if len(source_positions) > 1:
                label = f'Source {i+1}'
            else:
                label = 'Source'
            
            ax.plot(x, y, 'yo', markersize=10, markeredgecolor='black', 
                   label=label, alpha=0.8)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Interference (log scale)', fontsize=12)
    
    # Plot settings
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('X (meters)', fontsize=12)
    ax.set_ylabel('Y (meters)', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axis('equal')
    
    if source_positions:
        ax.legend(loc='upper right')
    
    plt.tight_layout()
    
    # Convert to base64
    img_data = _fig_to_base64(fig)
    plt.close(fig)
    
    return img_data

def plot_array_geometry(array_positions: List[np.ndarray],
                       title: str = "Array Geometry",
                       show_labels: bool = True) -> str:
    """
    Create plot showing array element positions.
    
    Args:
        array_positions: List of arrays containing element positions
        title: Plot title
        show_labels: Whether to show array labels
    
    Returns:
        Base64 encoded PNG image string
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Define colors for different arrays
    colors = plt.cm.Set1(np.linspace(0, 1, len(array_positions)))
    
    for i, positions in enumerate(array_positions):
        if positions is None or len(positions) == 0:
            continue
        
        # Plot element positions
        ax.scatter(positions[:, 0], positions[:, 1],
                  color=colors[i], s=100, alpha=0.7,
                  edgecolors='black', linewidth=1,
                  label=f'Array {i+1}' if show_labels else None,
                  zorder=3)
        
        # Connect elements with lines for visualization
        if len(positions) > 1:
            # Sort positions for better visualization
            sorted_positions = positions[np.argsort(positions[:, 0])]
            ax.plot(sorted_positions[:, 0], sorted_positions[:, 1],
                   color=colors[i], alpha=0.3, linewidth=2,
                   zorder=2)
    
    # Plot array center
    ax.plot(0, 0, 'k*', markersize=15, label='Origin', zorder=4)
    
    # Plot settings
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('X (meters)', fontsize=12)
    ax.set_ylabel('Y (meters)', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axis('equal')
    
    if show_labels:
        ax.legend(loc='best')
    
    # Add coordinate system arrows
    ax.arrow(0, 0, 1, 0, head_width=0.1, head_length=0.2, fc='black', ec='black', alpha=0.5)
    ax.arrow(0, 0, 0, 1, head_width=0.1, head_length=0.2, fc='black', ec='black', alpha=0.5)
    ax.text(1.2, 0, 'X', fontsize=12, fontweight='bold')
    ax.text(0, 1.2, 'Y', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    
    # Convert to base64
    img_data = _fig_to_base64(fig)
    plt.close(fig)
    
    return img_data

def generate_3d_plot(magnitude: np.ndarray,
                    X: np.ndarray,
                    Y: np.ndarray,
                    title: str = "3D Beam Pattern") -> Dict:
    """
    Generate 3D plot of beam pattern.
    
    Args:
        magnitude: Beam pattern magnitude (2D array)
        X: X coordinates (2D array)
        Y: Y coordinates (2D array)
        title: Plot title
    
    Returns:
        Dictionary containing plotly figure as JSON
    """
    # Convert to dB for better visualization
    magnitude_db = 10 * np.log10(magnitude + 1e-10)
    
    # Create 3D surface plot
    fig = go.Figure(data=[
        go.Surface(
            z=magnitude_db,
            x=X,
            y=Y,
            colorscale='Viridis',
            opacity=0.9,
            contours={
                "z": {
                    "show": True,
                    "usecolormap": True,
                    "highlightcolor": "limegreen",
                    "project": {"z": True}
                }
            },
            name='Beam Pattern'
        )
    ])
    
    # Update layout
    fig.update_layout(
        title={
            'text': title,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=20, family="Arial")
        },
        scene=dict(
            xaxis_title='X (meters)',
            yaxis_title='Y (meters)',
            zaxis_title='Magnitude (dB)',
            aspectratio=dict(x=1, y=1, z=0.7),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        width=900,
        height=700,
        margin=dict(l=0, r=0, b=0, t=50),
        showlegend=False
    )
    
    # Convert to JSON for transmission
    fig_json = json.loads(fig.to_json())
    
    return {
        'plotly_json': fig_json,
        'html': fig.to_html(full_html=False, include_plotlyjs='cdn')
    }

def plot_radiation_pattern(magnitude: np.ndarray,
                          angles: np.ndarray,
                          title: str = "Radiation Pattern",
                          polar: bool = True) -> str:
    """
    Plot radiation pattern (polar or cartesian).
    
    Args:
        magnitude: Magnitude values (1D array)
        angles: Angles in degrees (1D array)
        title: Plot title
        polar: Whether to use polar plot
    
    Returns:
        Base64 encoded PNG image string
    """
    if polar:
        fig = plt.figure(figsize=(8, 8))
        ax = plt.subplot(111, projection='polar')
        
        # Convert to radians
        theta = np.radians(angles)
        
        # Plot
        ax.plot(theta, magnitude, 'b-', linewidth=2, alpha=0.8)
        ax.fill_between(theta, 0, magnitude, alpha=0.3, color='blue')
        
        # Set direction of theta
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        
        # Grid
        ax.grid(True, alpha=0.5)
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot
        ax.plot(angles, magnitude, 'b-', linewidth=2, alpha=0.8)
        ax.fill_between(angles, 0, magnitude, alpha=0.3, color='blue')
        
        # Grid and labels
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlabel('Angle (degrees)', fontsize=12)
        ax.set_ylabel('Magnitude', fontsize=12)
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlim([angles.min(), angles.max()])
    
    plt.tight_layout()
    
    # Convert to base64
    img_data = _fig_to_base64(fig)
    plt.close(fig)
    
    return img_data

def plot_comparison(patterns: List[Dict],
                   titles: List[str],
                   main_title: str = "Beam Pattern Comparison") -> str:
    """
    Create comparison plot of multiple beam patterns.
    
    Args:
        patterns: List of dictionaries containing 'magnitude', 'X', 'Y'
        titles: List of titles for each subplot
        main_title: Main plot title
    
    Returns:
        Base64 encoded PNG image string
    """
    n_patterns = len(patterns)
    
    # Determine grid layout
    n_cols = min(2, n_patterns)
    n_rows = (n_patterns + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(6*n_cols, 5*n_rows))
    
    if n_rows == 1 and n_cols == 1:
        axes = np.array([axes])
    elif n_rows == 1 or n_cols == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()
    
    for i in range(n_rows * n_cols):
        if i < n_patterns:
            ax = axes[i]
            pattern = patterns[i]
            
            # Convert to dB
            magnitude_db = 10 * np.log10(pattern['magnitude'] + 1e-10)
            
            # Plot
            im = ax.contourf(pattern['X'], pattern['Y'], magnitude_db,
                           levels=50, cmap='viridis', alpha=0.9)
            
            # Title
            ax.set_title(titles[i] if i < len(titles) else f'Pattern {i+1}',
                        fontsize=14, fontweight='bold')
            
            # Labels
            ax.set_xlabel('X (m)', fontsize=10)
            ax.set_ylabel('Y (m)', fontsize=10)
            ax.grid(True, alpha=0.3)
            ax.axis('equal')
            
            # Add colorbar
            plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        else:
            axes[i].axis('off')
    
    # Main title
    plt.suptitle(main_title, fontsize=18, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    # Convert to base64
    img_data = _fig_to_base64(fig)
    plt.close(fig)
    
    return img_data

def plot_steering_animation(frames: List[Dict],
                           title: str = "Beam Steering Animation") -> str:
    """
    Create animation of beam steering.
    
    Args:
        frames: List of beam patterns at different steering angles
        title: Animation title
    
    Returns:
        Base64 encoded GIF image string
    """
    from matplotlib.animation import FuncAnimation, PillowWriter
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Initialize plot
    frame_data = frames[0]
    magnitude_db = 10 * np.log10(frame_data['magnitude'] + 1e-10)
    
    # First frame
    im = ax.contourf(frame_data['X'], frame_data['Y'], magnitude_db,
                    levels=50, cmap='viridis', alpha=0.9)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Magnitude (dB)', fontsize=12)
    
    # Title with angle
    title_text = ax.text(0.5, 1.05, f'{title} - Angle: {frame_data.get("angle", 0):.1f}°',
                        transform=ax.transAxes, ha='center', fontsize=14, fontweight='bold')
    
    # Labels and grid
    ax.set_xlabel('X (m)', fontsize=12)
    ax.set_ylabel('Y (m)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.axis('equal')
    
    def update(frame_idx):
        """Update function for animation"""
        frame_data = frames[frame_idx]
        magnitude_db = 10 * np.log10(frame_data['magnitude'] + 1e-10)
        
        # Clear axis
        ax.clear()
        
        # Redraw plot
        im = ax.contourf(frame_data['X'], frame_data['Y'], magnitude_db,
                        levels=50, cmap='viridis', alpha=0.9)
        
        # Update title
        title_text.set_text(f'{title} - Angle: {frame_data.get("angle", 0):.1f}°')
        
        # Redraw labels
        ax.set_xlabel('X (m)', fontsize=12)
        ax.set_ylabel('Y (m)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
        
        return im, title_text
    
    # Create animation
    anim = FuncAnimation(fig, update, frames=len(frames), 
                        interval=200, blit=False, repeat=True)
    
    # Save to BytesIO as GIF
    buffer = BytesIO()
    writer = PillowWriter(fps=5)
    anim.save(buffer, writer=writer, format='gif')
    buffer.seek(0)
    
    # Convert to base64
    gif_data = base64.b64encode(buffer.read()).decode()
    
    plt.close(fig)
    
    return f"data:image/gif;base64,{gif_data}"

def plot_parameter_sweep(results: List[Dict],
                        parameter_name: str,
                        title: str = "Parameter Sweep Analysis") -> str:
    """
    Plot results of parameter sweep analysis.
    
    Args:
        results: List of results from parameter sweep
        parameter_name: Name of parameter that was varied
        title: Plot title
    
    Returns:
        Base64 encoded PNG image string
    """
    # Extract data
    parameters = [r['parameter'] for r in results]
    metrics = {}
    
    # Collect all available metrics
    for r in results:
        for key, value in r.get('metrics', {}).items():
            if key not in metrics:
                metrics[key] = []
            metrics[key].append(value)
    
    # Create subplots
    n_metrics = len(metrics)
    fig, axes = plt.subplots(n_metrics, 1, figsize=(10, 4*n_metrics))
    
    if n_metrics == 1:
        axes = [axes]
    
    for i, (metric_name, values) in enumerate(metrics.items()):
        ax = axes[i]
        
        # Plot metric
        ax.plot(parameters, values, 'b-o', linewidth=2, markersize=8)
        
        # Fill area
        ax.fill_between(parameters, values, alpha=0.3, color='blue')
        
        # Find optimal value
        if metric_name in ['directivity', 'gain']:
            # Higher is better
            opt_idx = np.argmax(values)
        else:
            # Lower is better (e.g., beamwidth)
            opt_idx = np.argmin(values)
        
        # Mark optimal point
        ax.plot(parameters[opt_idx], values[opt_idx], 'r*', 
                markersize=15, label=f'Optimal: {parameters[opt_idx]}')
        
        # Labels and grid
        ax.set_xlabel(parameter_name, fontsize=12)
        ax.set_ylabel(metric_name, fontsize=12)
        ax.set_title(f'{metric_name} vs {parameter_name}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend()
    
    # Main title
    plt.suptitle(title, fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    # Convert to base64
    img_data = _fig_to_base64(fig)
    plt.close(fig)
    
    return img_data

def plot_beamforming_demo(array_positions: np.ndarray,
                         beam_pattern: np.ndarray,
                         X: np.ndarray,
                         Y: np.ndarray,
                         steering_angle: float = 0.0) -> Dict:
    """
    Create comprehensive beamforming demonstration plot.
    
    Args:
        array_positions: Array element positions
        beam_pattern: Beam pattern magnitude
        X: X coordinates
        Y: Y coordinates
        steering_angle: Current steering angle
    
    Returns:
        Dictionary containing multiple visualizations
    """
    visualizations = {}
    
    # 1. Beam pattern
    beam_plot = plot_beam_pattern(beam_pattern, X, Y, 
                                 title=f"Beam Pattern - {steering_angle:.1f}° Steering")
    visualizations['beam_pattern'] = beam_plot
    
    # 2. 3D plot
    from .plotting_utils import generate_3d_plot
    three_d_plot = generate_3d_plot(beam_pattern, X, Y,
                                   title=f"3D Beam Pattern - {steering_angle:.1f}°")
    visualizations['3d_plot'] = three_d_plot
    
    # 3. Array geometry
    array_plot = plot_array_geometry([array_positions],
                                    title="Array Geometry")
    visualizations['array_geometry'] = array_plot
    
    # 4. Radiation pattern (polar)
    # Extract cross-section at y=0
    center_idx = beam_pattern.shape[0] // 2
    cross_section = beam_pattern[center_idx, :]
    angles = np.linspace(-90, 90, len(cross_section))
    
    radiation_plot = plot_radiation_pattern(cross_section, angles,
                                           title=f"Radiation Pattern - {steering_angle:.1f}°",
                                           polar=False)
    visualizations['radiation_pattern'] = radiation_plot
    
    return visualizations

def _fig_to_base64(fig) -> str:
    """
    Convert matplotlib figure to base64 encoded string.
    
    Args:
        fig: Matplotlib figure
    
    Returns:
        Base64 encoded PNG string
    """
    buffer = BytesIO()
    fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    buffer.seek(0)
    
    img_data = base64.b64encode(buffer.read()).decode()
    return f"data:image/png;base64,{img_data}"

def plot_to_base64(plot_func, *args, **kwargs) -> str:
    """
    Wrapper function to convert any plotting function to base64.
    
    Args:
        plot_func: Plotting function to call
        *args, **kwargs: Arguments for plotting function
    
    Returns:
        Base64 encoded image string
    """
    import warnings
    warnings.filterwarnings('ignore')
    
    try:
        # If function returns base64 directly
        result = plot_func(*args, **kwargs)
        if isinstance(result, str) and result.startswith('data:image'):
            return result
        else:
            # Assume it returns a figure
            fig = result
            img_data = _fig_to_base64(fig)
            plt.close(fig)
            return img_data
    except Exception as e:
        # Return error image
        return _create_error_plot(str(e))

def _create_error_plot(error_message: str) -> str:
    """Create an error plot when plotting fails"""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.text(0.5, 0.5, f'Plotting Error:\n{error_message}',
            ha='center', va='center', fontsize=12, color='red',
            transform=ax.transAxes, wrap=True)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    img_data = _fig_to_base64(fig)
    plt.close(fig)
    return img_dataimport numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from io import BytesIO
import base64
from typing import List, Tuple, Dict, Optional, Union
import json

# Set matplotlib style
plt.style.use('seaborn-v0_8-darkgrid')

def plot_beam_pattern(magnitude: np.ndarray, 
                     X: np.ndarray, 
                     Y: np.ndarray,
                     title: str = "Beam Pattern",
                     colorbar_label: str = "Normalized Magnitude (dB)",
                     include_contours: bool = True) -> str:
    """
    Create 2D plot of beam pattern and return as base64 encoded string.
    
    Args:
        magnitude: Beam pattern magnitude (2D array)
        X: X coordinates (2D array)
        Y: Y coordinates (2D array)
        title: Plot title
        colorbar_label: Label for colorbar
        include_contours: Whether to include contour lines
    
    Returns:
        Base64 encoded PNG image string
    """
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Convert to dB for better visualization
    magnitude_db = 10 * np.log10(magnitude + 1e-10)  # Add small value to avoid log(0)
    
    # Create custom colormap (blue to red)
    colors = [(0, 0, 0.5), (0, 0, 1), (0, 1, 1), (1, 1, 0), (1, 0, 0)]
    cmap = LinearSegmentedColormap.from_list('beam_cmap', colors, N=256)
    
    # Plot beam pattern
    im = ax.contourf(X, Y, magnitude_db, 
                     levels=100, 
                     cmap=cmap, 
                     alpha=0.9,
                     vmin=magnitude_db.min(),
                     vmax=magnitude_db.max())
    
    # Add contour lines
    if include_contours:
        contour_levels = np.linspace(magnitude_db.min(), magnitude_db.max(), 20)
        ax.contour(X, Y, magnitude_db, 
                  levels=contour_levels,
                  colors='white', 
                  linewidths=0.5, 
                  alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label(colorbar_label, fontsize=12)
    
    # Mark array position
    ax.plot(0, 0, 'k*', markersize=15, label='Array Center')
    
    # Plot settings
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('X (meters)', fontsize=12)
    ax.set_ylabel('Y (meters)', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axis('equal')
    ax.legend(loc='upper right')
    
    # Add text with min/max values
    text_str = f"Max: {magnitude.max():.2f}\nMin: {magnitude.min():.2e}"
    ax.text(0.02, 0.98, text_str, 
            transform=ax.transAxes, 
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Convert to base64
    img_data = _fig_to_base64(fig)
    plt.close(fig)
    
    return img_data

def plot_interference_map(interference: np.ndarray,
                         X: np.ndarray,
                         Y: np.ndarray,
                         title: str = "Interference Map",
                         source_positions: List[List[float]] = None) -> str:
    """
    Create interference map plot.
    
    Args:
        interference: Interference values (2D array)
        X: X coordinates (2D array)
        Y: Y coordinates (2D array)
        title: Plot title
        source_positions: List of source positions to plot
    
    Returns:
        Base64 encoded PNG image string
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Use log scale for better visualization
    interference_log = np.log10(interference + 1e-10)
    
    # Plot interference
    im = ax.contourf(X, Y, interference_log, 
                     levels=100, 
                     cmap='plasma', 
                     alpha=0.9)
    
    # Add contour lines
    contour_levels = np.linspace(interference_log.min(), interference_log.max(), 10)
    ax.contour(X, Y, interference_log, 
               levels=contour_levels,
               colors='white', 
               linewidths=0.5, 
               alpha=0.5)
    
    # Mark sources if provided
    if source_positions:
        for i, (x, y) in enumerate(source_positions):
            if len(source_positions) > 1:
                label = f'Source {i+1}'
            else:
                label = 'Source'
            
            ax.plot(x, y, 'yo', markersize=10, markeredgecolor='black', 
                   label=label, alpha=0.8)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Interference (log scale)', fontsize=12)
    
    # Plot settings
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('X (meters)', fontsize=12)
    ax.set_ylabel('Y (meters)', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axis('equal')
    
    if source_positions:
        ax.legend(loc='upper right')
    
    plt.tight_layout()
    
    # Convert to base64
    img_data = _fig_to_base64(fig)
    plt.close(fig)
    
    return img_data

def plot_array_geometry(array_positions: List[np.ndarray],
                       title: str = "Array Geometry",
                       show_labels: bool = True) -> str:
    """
    Create plot showing array element positions.
    
    Args:
        array_positions: List of arrays containing element positions
        title: Plot title
        show_labels: Whether to show array labels
    
    Returns:
        Base64 encoded PNG image string
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Define colors for different arrays
    colors = plt.cm.Set1(np.linspace(0, 1, len(array_positions)))
    
    for i, positions in enumerate(array_positions):
        if positions is None or len(positions) == 0:
            continue
        
        # Plot element positions
        ax.scatter(positions[:, 0], positions[:, 1],
                  color=colors[i], s=100, alpha=0.7,
                  edgecolors='black', linewidth=1,
                  label=f'Array {i+1}' if show_labels else None,
                  zorder=3)
        
        # Connect elements with lines for visualization
        if len(positions) > 1:
            # Sort positions for better visualization
            sorted_positions = positions[np.argsort(positions[:, 0])]
            ax.plot(sorted_positions[:, 0], sorted_positions[:, 1],
                   color=colors[i], alpha=0.3, linewidth=2,
                   zorder=2)
    
    # Plot array center
    ax.plot(0, 0, 'k*', markersize=15, label='Origin', zorder=4)
    
    # Plot settings
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('X (meters)', fontsize=12)
    ax.set_ylabel('Y (meters)', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axis('equal')
    
    if show_labels:
        ax.legend(loc='best')
    
    # Add coordinate system arrows
    ax.arrow(0, 0, 1, 0, head_width=0.1, head_length=0.2, fc='black', ec='black', alpha=0.5)
    ax.arrow(0, 0, 0, 1, head_width=0.1, head_length=0.2, fc='black', ec='black', alpha=0.5)
    ax.text(1.2, 0, 'X', fontsize=12, fontweight='bold')
    ax.text(0, 1.2, 'Y', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    
    # Convert to base64
    img_data = _fig_to_base64(fig)
    plt.close(fig)
    
    return img_data

def generate_3d_plot(magnitude: np.ndarray,
                    X: np.ndarray,
                    Y: np.ndarray,
                    title: str = "3D Beam Pattern") -> Dict:
    """
    Generate 3D plot of beam pattern.
    
    Args:
        magnitude: Beam pattern magnitude (2D array)
        X: X coordinates (2D array)
        Y: Y coordinates (2D array)
        title: Plot title
    
    Returns:
        Dictionary containing plotly figure as JSON
    """
    # Convert to dB for better visualization
    magnitude_db = 10 * np.log10(magnitude + 1e-10)
    
    # Create 3D surface plot
    fig = go.Figure(data=[
        go.Surface(
            z=magnitude_db,
            x=X,
            y=Y,
            colorscale='Viridis',
            opacity=0.9,
            contours={
                "z": {
                    "show": True,
                    "usecolormap": True,
                    "highlightcolor": "limegreen",
                    "project": {"z": True}
                }
            },
            name='Beam Pattern'
        )
    ])
    
    # Update layout
    fig.update_layout(
        title={
            'text': title,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=20, family="Arial")
        },
        scene=dict(
            xaxis_title='X (meters)',
            yaxis_title='Y (meters)',
            zaxis_title='Magnitude (dB)',
            aspectratio=dict(x=1, y=1, z=0.7),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        width=900,
        height=700,
        margin=dict(l=0, r=0, b=0, t=50),
        showlegend=False
    )
    
    # Convert to JSON for transmission
    fig_json = json.loads(fig.to_json())
    
    return {
        'plotly_json': fig_json,
        'html': fig.to_html(full_html=False, include_plotlyjs='cdn')
    }

def plot_radiation_pattern(magnitude: np.ndarray,
                          angles: np.ndarray,
                          title: str = "Radiation Pattern",
                          polar: bool = True) -> str:
    """
    Plot radiation pattern (polar or cartesian).
    
    Args:
        magnitude: Magnitude values (1D array)
        angles: Angles in degrees (1D array)
        title: Plot title
        polar: Whether to use polar plot
    
    Returns:
        Base64 encoded PNG image string
    """
    if polar:
        fig = plt.figure(figsize=(8, 8))
        ax = plt.subplot(111, projection='polar')
        
        # Convert to radians
        theta = np.radians(angles)
        
        # Plot
        ax.plot(theta, magnitude, 'b-', linewidth=2, alpha=0.8)
        ax.fill_between(theta, 0, magnitude, alpha=0.3, color='blue')
        
        # Set direction of theta
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        
        # Grid
        ax.grid(True, alpha=0.5)
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot
        ax.plot(angles, magnitude, 'b-', linewidth=2, alpha=0.8)
        ax.fill_between(angles, 0, magnitude, alpha=0.3, color='blue')
        
        # Grid and labels
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlabel('Angle (degrees)', fontsize=12)
        ax.set_ylabel('Magnitude', fontsize=12)
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlim([angles.min(), angles.max()])
    
    plt.tight_layout()
    
    # Convert to base64
    img_data = _fig_to_base64(fig)
    plt.close(fig)
    
    return img_data

def plot_comparison(patterns: List[Dict],
                   titles: List[str],
                   main_title: str = "Beam Pattern Comparison") -> str:
    """
    Create comparison plot of multiple beam patterns.
    
    Args:
        patterns: List of dictionaries containing 'magnitude', 'X', 'Y'
        titles: List of titles for each subplot
        main_title: Main plot title
    
    Returns:
        Base64 encoded PNG image string
    """
    n_patterns = len(patterns)
    
    # Determine grid layout
    n_cols = min(2, n_patterns)
    n_rows = (n_patterns + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(6*n_cols, 5*n_rows))
    
    if n_rows == 1 and n_cols == 1:
        axes = np.array([axes])
    elif n_rows == 1 or n_cols == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()
    
    for i in range(n_rows * n_cols):
        if i < n_patterns:
            ax = axes[i]
            pattern = patterns[i]
            
            # Convert to dB
            magnitude_db = 10 * np.log10(pattern['magnitude'] + 1e-10)
            
            # Plot
            im = ax.contourf(pattern['X'], pattern['Y'], magnitude_db,
                           levels=50, cmap='viridis', alpha=0.9)
            
            # Title
            ax.set_title(titles[i] if i < len(titles) else f'Pattern {i+1}',
                        fontsize=14, fontweight='bold')
            
            # Labels
            ax.set_xlabel('X (m)', fontsize=10)
            ax.set_ylabel('Y (m)', fontsize=10)
            ax.grid(True, alpha=0.3)
            ax.axis('equal')
            
            # Add colorbar
            plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        else:
            axes[i].axis('off')
    
    # Main title
    plt.suptitle(main_title, fontsize=18, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    # Convert to base64
    img_data = _fig_to_base64(fig)
    plt.close(fig)
    
    return img_data

def plot_steering_animation(frames: List[Dict],
                           title: str = "Beam Steering Animation") -> str:
    """
    Create animation of beam steering.
    
    Args:
        frames: List of beam patterns at different steering angles
        title: Animation title
    
    Returns:
        Base64 encoded GIF image string
    """
    from matplotlib.animation import FuncAnimation, PillowWriter
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Initialize plot
    frame_data = frames[0]
    magnitude_db = 10 * np.log10(frame_data['magnitude'] + 1e-10)
    
    # First frame
    im = ax.contourf(frame_data['X'], frame_data['Y'], magnitude_db,
                    levels=50, cmap='viridis', alpha=0.9)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Magnitude (dB)', fontsize=12)
    
    # Title with angle
    title_text = ax.text(0.5, 1.05, f'{title} - Angle: {frame_data.get("angle", 0):.1f}°',
                        transform=ax.transAxes, ha='center', fontsize=14, fontweight='bold')
    
    # Labels and grid
    ax.set_xlabel('X (m)', fontsize=12)
    ax.set_ylabel('Y (m)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.axis('equal')
    
    def update(frame_idx):
        """Update function for animation"""
        frame_data = frames[frame_idx]
        magnitude_db = 10 * np.log10(frame_data['magnitude'] + 1e-10)
        
        # Clear axis
        ax.clear()
        
        # Redraw plot
        im = ax.contourf(frame_data['X'], frame_data['Y'], magnitude_db,
                        levels=50, cmap='viridis', alpha=0.9)
        
        # Update title
        title_text.set_text(f'{title} - Angle: {frame_data.get("angle", 0):.1f}°')
        
        # Redraw labels
        ax.set_xlabel('X (m)', fontsize=12)
        ax.set_ylabel('Y (m)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
        
        return im, title_text
    
    # Create animation
    anim = FuncAnimation(fig, update, frames=len(frames), 
                        interval=200, blit=False, repeat=True)
    
    # Save to BytesIO as GIF
    buffer = BytesIO()
    writer = PillowWriter(fps=5)
    anim.save(buffer, writer=writer, format='gif')
    buffer.seek(0)
    
    # Convert to base64
    gif_data = base64.b64encode(buffer.read()).decode()
    
    plt.close(fig)
    
    return f"data:image/gif;base64,{gif_data}"

def plot_parameter_sweep(results: List[Dict],
                        parameter_name: str,
                        title: str = "Parameter Sweep Analysis") -> str:
    """
    Plot results of parameter sweep analysis.
    
    Args:
        results: List of results from parameter sweep
        parameter_name: Name of parameter that was varied
        title: Plot title
    
    Returns:
        Base64 encoded PNG image string
    """
    # Extract data
    parameters = [r['parameter'] for r in results]
    metrics = {}
    
    # Collect all available metrics
    for r in results:
        for key, value in r.get('metrics', {}).items():
            if key not in metrics:
                metrics[key] = []
            metrics[key].append(value)
    
    # Create subplots
    n_metrics = len(metrics)
    fig, axes = plt.subplots(n_metrics, 1, figsize=(10, 4*n_metrics))
    
    if n_metrics == 1:
        axes = [axes]
    
    for i, (metric_name, values) in enumerate(metrics.items()):
        ax = axes[i]
        
        # Plot metric
        ax.plot(parameters, values, 'b-o', linewidth=2, markersize=8)
        
        # Fill area
        ax.fill_between(parameters, values, alpha=0.3, color='blue')
        
        # Find optimal value
        if metric_name in ['directivity', 'gain']:
            # Higher is better
            opt_idx = np.argmax(values)
        else:
            # Lower is better (e.g., beamwidth)
            opt_idx = np.argmin(values)
        
        # Mark optimal point
        ax.plot(parameters[opt_idx], values[opt_idx], 'r*', 
                markersize=15, label=f'Optimal: {parameters[opt_idx]}')
        
        # Labels and grid
        ax.set_xlabel(parameter_name, fontsize=12)
        ax.set_ylabel(metric_name, fontsize=12)
        ax.set_title(f'{metric_name} vs {parameter_name}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend()
    
    # Main title
    plt.suptitle(title, fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    # Convert to base64
    img_data = _fig_to_base64(fig)
    plt.close(fig)
    
    return img_data

def plot_beamforming_demo(array_positions: np.ndarray,
                         beam_pattern: np.ndarray,
                         X: np.ndarray,
                         Y: np.ndarray,
                         steering_angle: float = 0.0) -> Dict:
    """
    Create comprehensive beamforming demonstration plot.
    
    Args:
        array_positions: Array element positions
        beam_pattern: Beam pattern magnitude
        X: X coordinates
        Y: Y coordinates
        steering_angle: Current steering angle
    
    Returns:
        Dictionary containing multiple visualizations
    """
    visualizations = {}
    
    # 1. Beam pattern
    beam_plot = plot_beam_pattern(beam_pattern, X, Y, 
                                 title=f"Beam Pattern - {steering_angle:.1f}° Steering")
    visualizations['beam_pattern'] = beam_plot
    
    # 2. 3D plot
    from .plotting_utils import generate_3d_plot
    three_d_plot = generate_3d_plot(beam_pattern, X, Y,
                                   title=f"3D Beam Pattern - {steering_angle:.1f}°")
    visualizations['3d_plot'] = three_d_plot
    
    # 3. Array geometry
    array_plot = plot_array_geometry([array_positions],
                                    title="Array Geometry")
    visualizations['array_geometry'] = array_plot
    
    # 4. Radiation pattern (polar)
    # Extract cross-section at y=0
    center_idx = beam_pattern.shape[0] // 2
    cross_section = beam_pattern[center_idx, :]
    angles = np.linspace(-90, 90, len(cross_section))
    
    radiation_plot = plot_radiation_pattern(cross_section, angles,
                                           title=f"Radiation Pattern - {steering_angle:.1f}°",
                                           polar=False)
    visualizations['radiation_pattern'] = radiation_plot
    
    return visualizations

def _fig_to_base64(fig) -> str:
    """
    Convert matplotlib figure to base64 encoded string.
    
    Args:
        fig: Matplotlib figure
    
    Returns:
        Base64 encoded PNG string
    """
    buffer = BytesIO()
    fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    buffer.seek(0)
    
    img_data = base64.b64encode(buffer.read()).decode()
    return f"data:image/png;base64,{img_data}"

def plot_to_base64(plot_func, *args, **kwargs) -> str:
    """
    Wrapper function to convert any plotting function to base64.
    
    Args:
        plot_func: Plotting function to call
        *args, **kwargs: Arguments for plotting function
    
    Returns:
        Base64 encoded image string
    """
    import warnings
    warnings.filterwarnings('ignore')
    
    try:
        # If function returns base64 directly
        result = plot_func(*args, **kwargs)
        if isinstance(result, str) and result.startswith('data:image'):
            return result
        else:
            # Assume it returns a figure
            fig = result
            img_data = _fig_to_base64(fig)
            plt.close(fig)
            return img_data
    except Exception as e:
        # Return error image
        return _create_error_plot(str(e))

def _create_error_plot(error_message: str) -> str:
    """Create an error plot when plotting fails"""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.text(0.5, 0.5, f'Plotting Error:\n{error_message}',
            ha='center', va='center', fontsize=12, color='red',
            transform=ax.transAxes, wrap=True)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    img_data = _fig_to_base64(fig)
    plt.close(fig)
    return img_data