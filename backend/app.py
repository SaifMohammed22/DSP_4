from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import base64
import cv2
import numpy as np
from PIL import Image
import io
import threading

# Get the directory where app.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), 'frontend')

app = Flask(
    __name__,
    template_folder=os.path.join(FRONTEND_DIR, 'templates'),
    static_folder=os.path.join(FRONTEND_DIR, 'static')
)
CORS(app)  # Enable CORS for all routes
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure upload folder
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Store FFT data for each image slot (1-4)
# This stores the actual complex FFT data needed for mixing
image_fft_data = {}
image_original_data = {}  # Stores original uploaded images (before resize)
image_resized_data = {}   # Stores resized images (unified size)
current_mix_task = None
mix_lock = threading.Lock()
current_unified_size = None  # (height, width) - the smallest size among all images


def get_smallest_size():
    """Calculate the smallest size among all uploaded images"""
    if not image_original_data:
        return None
    
    min_height = float('inf')
    min_width = float('inf')
    
    for img_id, img in image_original_data.items():
        h, w = img.shape[:2]
        min_height = min(min_height, h)
        min_width = min(min_width, w)
    
    return (int(min_height), int(min_width))


def resize_image(img, target_size):
    """Resize image to target size (height, width)"""
    return cv2.resize(img, (target_size[1], target_size[0]), interpolation=cv2.INTER_AREA)


def reprocess_all_images():
    """Resize all images to the current unified size and recompute FFT"""
    global current_unified_size, image_resized_data, image_fft_data
    
    current_unified_size = get_smallest_size()
    if current_unified_size is None:
        return {}
    
    updated_images = {}
    
    for img_id, original_img in image_original_data.items():
        # Resize to unified size
        resized_img = resize_image(original_img, current_unified_size)
        image_resized_data[img_id] = resized_img
        
        # Recompute FFT
        f = np.fft.fft2(resized_img.astype(np.float64))
        fshift = np.fft.fftshift(f)
        
        image_fft_data[img_id] = {
            'fft_shifted': fshift,
            'magnitude': np.abs(fshift),
            'phase': np.angle(fshift),
            'real': np.real(fshift),
            'imaginary': np.imag(fshift),
            'shape': resized_img.shape
        }
        
        # Prepare display images
        magnitude = np.abs(fshift)
        phase = np.angle(fshift)
        real_part = np.real(fshift)
        imag_part = np.imag(fshift)
        
        magnitude_display = 20 * np.log(magnitude + 1)
        magnitude_display = cv2.normalize(magnitude_display, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        phase_display = cv2.normalize(phase, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        real_display = cv2.normalize(real_part, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        imag_display = cv2.normalize(imag_part, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        
        # Convert to base64
        _, img_buffer = cv2.imencode('.png', resized_img)
        _, mag_buffer = cv2.imencode('.png', magnitude_display)
        _, phase_buffer = cv2.imencode('.png', phase_display)
        _, real_buffer = cv2.imencode('.png', real_display)
        _, imag_buffer = cv2.imencode('.png', imag_display)
        
        updated_images[img_id] = {
            'image': base64.b64encode(img_buffer).decode('utf-8'),
            'magnitude': base64.b64encode(mag_buffer).decode('utf-8'),
            'phase': base64.b64encode(phase_buffer).decode('utf-8'),
            'real': base64.b64encode(real_buffer).decode('utf-8'),
            'imaginary': base64.b64encode(imag_buffer).decode('utf-8')
        }
    
    return updated_images


@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'FT Mixer API is running'})


@app.route('/upload', methods=['POST'])
def upload_image():
    """Handle image upload and convert to grayscale"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        image_id = request.form.get('imageId', '1')  # Get image slot ID
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read image
        image_bytes = file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray_img = img
        
        # Store original image data for this slot
        image_original_data[image_id] = gray_img.copy()
        
        # Reprocess all images to unify sizes
        updated_images = reprocess_all_images()
        
        # Get this image's data
        this_image_data = updated_images.get(image_id, {})
        
        return jsonify({
            'success': True,
            'image': this_image_data.get('image', ''),
            'width': current_unified_size[1] if current_unified_size else gray_img.shape[1],
            'height': current_unified_size[0] if current_unified_size else gray_img.shape[0],
            'magnitude': this_image_data.get('magnitude', ''),
            'phase': this_image_data.get('phase', ''),
            'real': this_image_data.get('real', ''),
            'imaginary': this_image_data.get('imaginary', ''),
            'updatedImages': updated_images  # Send all updated images to frontend
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/process_fft', methods=['POST'])
def process_fft():
    """Process FFT on server side and store for mixing"""
    try:
        data = request.json
        image_data = data.get('image')
        image_id = str(data.get('imageId', '1'))  # Get image slot ID
        
        # Decode base64 image
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        # Store original for this slot
        image_original_data[image_id] = img.copy()
        
        # Perform FFT 
        f = np.fft.fft2(img.astype(np.float64))
        fshift = np.fft.fftshift(f)
        
        # Store FFT data for mixing
        image_fft_data[image_id] = {
            'fft_shifted': fshift,
            'magnitude': np.abs(fshift),
            'phase': np.angle(fshift),
            'real': np.real(fshift),
            'imaginary': np.imag(fshift),
            'shape': img.shape
        }
        
        # Calculate components for display
        magnitude = np.abs(fshift)
        phase = np.angle(fshift)
        real = np.real(fshift)
        imaginary = np.imag(fshift)
        
        # Normalize for display
        magnitude_display = 20 * np.log(magnitude + 1)
        magnitude_display = cv2.normalize(magnitude_display, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        
        phase_display = cv2.normalize(phase, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        real_display = cv2.normalize(real, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        imaginary_display = cv2.normalize(imaginary, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        
        # Convert to base64
        _, mag_buffer = cv2.imencode('.png', magnitude_display)
        _, phase_buffer = cv2.imencode('.png', phase_display)
        _, real_buffer = cv2.imencode('.png', real_display)
        _, imag_buffer = cv2.imencode('.png', imaginary_display)
        
        return jsonify({
            'success': True,
            'magnitude': base64.b64encode(mag_buffer).decode('utf-8'),
            'phase': base64.b64encode(phase_buffer).decode('utf-8'),
            'real': base64.b64encode(real_buffer).decode('utf-8'),
            'imaginary': base64.b64encode(imag_buffer).decode('utf-8')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/mix_images', methods=['POST'])
def mix_images():
    """Mix images based on FT components with proper weighted average"""
    global current_mix_task
    
    try:
        data = request.json
        image_weights = {str(img['id']): img['weight'] for img in data.get('images', [])}
        component = data.get('component', 'magnitude')  # magnitude, phase, real, imaginary
        region_type = data.get('regionType', 'full')  # full, inner, outer
        region_size = data.get('regionSize', 0.5)  # 0-1 percentage
        
        # Cancel previous task if running
        with mix_lock:
            if current_mix_task and current_mix_task.is_alive():
                # In a real implementation, we'd have a cancellation flag
                pass
        
        # Get all available FFT data
        available_images = {k: v for k, v in image_fft_data.items() if k in image_weights}
        
        if not available_images:
            return jsonify({'error': 'No images available for mixing'}), 400
        
        # Get target shape (use first image's shape)
        first_key = list(available_images.keys())[0]
        target_shape = available_images[first_key]['shape']
        
        # Resize all FFT data to match if needed
        # For simplicity, we'll work with original shapes
        
        # Initialize result components
        if component in ['magnitude', 'phase']:
            # Magnitude/Phase mixing
            result_magnitude = np.zeros(target_shape, dtype=np.float64)
            result_phase = np.zeros(target_shape, dtype=np.float64)
            total_weight = 0
            
            for img_id, fft_data in available_images.items():
                weight = image_weights.get(img_id, 0)
                if weight > 0:
                    mag = fft_data['magnitude']
                    ph = fft_data['phase']
                    
                    # Resize if needed
                    if mag.shape != target_shape:
                        mag = cv2.resize(mag, (target_shape[1], target_shape[0]))
                        ph = cv2.resize(ph, (target_shape[1], target_shape[0]))
                    
                    # Apply region mask
                    mask = create_region_mask(target_shape, region_type, region_size)
                    
                    if component == 'magnitude':
                        result_magnitude += weight * mag * mask
                        # For magnitude mixing, we average phase
                        result_phase += weight * ph
                    else:  # phase
                        result_phase += weight * ph * mask
                        # For phase mixing, we average magnitude
                        result_magnitude += weight * mag
                    
                    total_weight += weight
            
            if total_weight > 0:
                result_magnitude /= total_weight
                result_phase /= total_weight
            
            # Reconstruct complex FFT
            result_fft = result_magnitude * np.exp(1j * result_phase)
            
        else:
            # Real/Imaginary mixing
            result_real = np.zeros(target_shape, dtype=np.float64)
            result_imag = np.zeros(target_shape, dtype=np.float64)
            total_weight = 0
            
            for img_id, fft_data in available_images.items():
                weight = image_weights.get(img_id, 0)
                if weight > 0:
                    real = fft_data['real']
                    imag = fft_data['imaginary']
                    
                    # Resize if needed
                    if real.shape != target_shape:
                        real = cv2.resize(real, (target_shape[1], target_shape[0]))
                        imag = cv2.resize(imag, (target_shape[1], target_shape[0]))
                    
                    # Apply region mask
                    mask = create_region_mask(target_shape, region_type, region_size)
                    
                    if component == 'real':
                        result_real += weight * real * mask
                        result_imag += weight * imag
                    else:  # imaginary
                        result_imag += weight * imag * mask
                        result_real += weight * real
                    
                    total_weight += weight
            
            if total_weight > 0:
                result_real /= total_weight
                result_imag /= total_weight
            
            # Reconstruct complex FFT
            result_fft = result_real + 1j * result_imag
        
        # Inverse FFT
        f_ishift = np.fft.ifftshift(result_fft)
        img_back = np.fft.ifft2(f_ishift)
        img_back = np.abs(img_back)
        
        # Normalize to 0-255
        img_back = cv2.normalize(img_back, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        
        # Convert to base64
        _, buffer = cv2.imencode('.png', img_back)
        result_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'result': result_base64
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def create_region_mask(shape, region_type, region_size):
    """Create a mask for inner/outer region selection"""
    rows, cols = shape
    crow, ccol = rows // 2, cols // 2
    
    if region_type == 'full':
        return np.ones(shape, dtype=np.float64)
    
    # Calculate region dimensions
    r_height = int(rows * region_size / 2)
    r_width = int(cols * region_size / 2)
    
    mask = np.zeros(shape, dtype=np.float64)
    
    if region_type == 'inner':
        # Inner region (low frequencies)
        mask[crow - r_height:crow + r_height, ccol - r_width:ccol + r_width] = 1
    else:  # outer
        # Outer region (high frequencies)
        mask[:] = 1
        mask[crow - r_height:crow + r_height, ccol - r_width:ccol + r_width] = 0
    
    return mask


@app.route('/adjust_brightness_contrast', methods=['POST'])
def adjust_brightness_contrast():
    """Adjust brightness and contrast of an image"""
    try:
        data = request.json
        image_data = data.get('image')
        brightness = data.get('brightness', 0)  # -100 to 100
        contrast = data.get('contrast', 0)  # -100 to 100
        
        # Decode base64 image
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        # Apply brightness and contrast
        # Contrast: alpha (1.0-3.0), Brightness: beta (0-100)
        alpha = 1 + (contrast / 100.0)  # Contrast control
        beta = brightness * 2.55  # Brightness control (scale to 0-255 range)
        
        adjusted = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
        
        # Convert to base64
        _, buffer = cv2.imencode('.png', adjusted)
        result_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': result_base64
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File is too large. Maximum size is 16MB'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def server_error(e):
    """Handle server errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # print("=" * 60)
    # print("🎛️  FT Magnitude/Phase Mixer - Server Starting")
    # print("=" * 60)
    # print(f"📁 Frontend directory: {FRONTEND_DIR}")
    # print(f"📁 Templates: {os.path.join(FRONTEND_DIR, 'templates')}")
    # print(f"📁 Static files: {os.path.join(FRONTEND_DIR, 'static')}")
    # print("=" * 60)
    # print("🌐 Server running on: http://127.0.0.1:5000")
    # print("⏹️  Press CTRL+C to stop the server")
    # print("=" * 60)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)