from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
import os
import uuid
import time
import json
import base64
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

from core.ft_processor import FTProcessor
from core.task_manager import TaskManager
from utils.file_utils import allowed_file, save_uploaded_file, encode_image_base64
from utils.async_utils import run_async_task
from .schemas import (
    ImageUploadRequest, MixRequest, RegionFilterRequest, 
    BrightnessContrastRequest, FTComponent
)

ft_mixer_bp = Blueprint('ft_mixer', __name__)
ft_processor = FTProcessor()
task_manager = TaskManager()

# Store uploaded images and their FT data
image_store = {}
processing_tasks = {}

@ft_mixer_bp.route('/upload', methods=['POST'])
def upload_image():
    """Upload an image and compute its Fourier Transform"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, current_app.config['ALLOWED_IMAGE_EXTENSIONS']):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Get parameters
        position = request.form.get('position', 0, type=int)
        image_id = str(uuid.uuid4())
        
        # Save uploaded file
        filename = secure_filename(f"{image_id}_{file.filename}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process image
        try:
            # Load and compute FT
            image_array = ft_processor.load_image(filepath)
            ft_data = ft_processor.compute_ft(image_array)
            
            # Generate preview images for each component
            ft_previews = {}
            for component in ['magnitude', 'phase', 'real', 'imaginary']:
                component_data = ft_data.get(component)
                if component_data is not None:
                    # Normalize for visualization
                    if component == 'magnitude':
                        component_data = np.log1p(component_data)
                    
                    # Normalize to 0-255
                    normalized = (component_data - component_data.min()) / (component_data.max() - component_data.min() + 1e-10)
                    normalized_8bit = (normalized * 255).astype(np.uint8)
                    
                    # Convert to base64
                    pil_image = Image.fromarray(normalized_8bit)
                    buffered = BytesIO()
                    pil_image.save(buffered, format="PNG")
                    ft_previews[component] = base64.b64encode(buffered.getvalue()).decode()
            
            # Store image data
            image_store[image_id] = {
                'filepath': filepath,
                'image_array': image_array,
                'ft_data': ft_data,
                'position': position,
                'upload_time': time.time()
            }
            
            # Generate original image preview
            original_preview = encode_image_base64(image_array)
            
            return jsonify({
                'image_id': image_id,
                'original_preview': original_preview,
                'ft_previews': ft_previews,
                'image_shape': image_array.shape,
                'position': position,
                'message': 'Image uploaded and processed successfully'
            }), 200
            
        except Exception as e:
            # Clean up file if processing fails
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Image processing failed: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ft_mixer_bp.route('/images', methods=['GET'])
def get_images():
    """Get list of all uploaded images"""
    images = []
    for img_id, data in image_store.items():
        images.append({
            'image_id': img_id,
            'position': data['position'],
            'shape': data['image_array'].shape,
            'upload_time': data['upload_time']
        })
    return jsonify({'images': images}), 200

@ft_mixer_bp.route('/image/<image_id>', methods=['GET'])
def get_image(image_id):
    """Get specific image data"""
    if image_id not in image_store:
        return jsonify({'error': 'Image not found'}), 404
    
    data = image_store[image_id]
    
    # Generate component previews on demand
    component = request.args.get('component', 'magnitude')
    if component not in ['magnitude', 'phase', 'real', 'imaginary']:
        component = 'magnitude'
    
    ft_data = data['ft_data']
    component_data = ft_data.get(component)
    
    if component_data is None:
        return jsonify({'error': 'Component not available'}), 400
    
    # Generate preview
    if component == 'magnitude':
        component_data = np.log1p(component_data)
    
    normalized = (component_data - component_data.min()) / (component_data.max() - component_data.min() + 1e-10)
    preview = encode_image_base64(normalized)
    
    return jsonify({
        'image_id': image_id,
        'component': component,
        'preview': preview,
        'shape': component_data.shape
    }), 200

@ft_mixer_bp.route('/mix', methods=['POST'])
def mix_images():
    """Mix multiple images using Fourier Transform"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract parameters
        image_ids = data.get('image_ids', [])
        weights = data.get('weights', [1.0] * len(image_ids))
        output_position = data.get('output_position', 0)
        mix_type = data.get('mix_type', 'magnitude_phase')
        
        # Validate inputs
        if len(image_ids) < 1 or len(image_ids) > 4:
            return jsonify({'error': 'Must provide 1-4 images'}), 400
        
        if len(image_ids) != len(weights):
            return jsonify({'error': 'Number of images and weights must match'}), 400
        
        # Check all images exist
        for img_id in image_ids:
            if img_id not in image_store:
                return jsonify({'error': f'Image {img_id} not found'}), 404
        
        # Get FT data for all images
        ft_data_list = []
        for img_id in image_ids:
            ft_data_list.append(image_store[img_id]['ft_data'])
        
        # Create task ID
        task_id = str(uuid.uuid4())
        
        # Start async mixing task
        task = run_async_task(
            ft_processor.mix_images,
            ft_data_list=ft_data_list,
            weights=weights
        )
        
        processing_tasks[task_id] = {
            'task': task,
            'image_ids': image_ids,
            'weights': weights,
            'output_position': output_position,
            'start_time': time.time(),
            'status': 'processing'
        }
        
        return jsonify({
            'task_id': task_id,
            'status': 'processing',
            'message': 'Mixing started'
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ft_mixer_bp.route('/mix/<task_id>', methods=['GET'])
def get_mix_result(task_id):
    """Get result of mixing task"""
    if task_id not in processing_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task_data = processing_tasks[task_id]
    task = task_data['task']
    
    if task.done():
        try:
            result = task.result()
            
            # Save mixed image
            output_filename = f"mixed_{task_id}.png"
            output_path = ft_processor.save_result(result['mixed_image'], output_filename)
            
            # Generate preview
            preview = encode_image_base64(result['mixed_image'])
            
            # Update task status
            task_data['status'] = 'completed'
            task_data['result'] = result
            task_data['output_path'] = output_path
            task_data['preview'] = preview
            
            return jsonify({
                'task_id': task_id,
                'status': 'completed',
                'preview': preview,
                'output_path': output_path,
                'mixed_magnitude_preview': encode_image_base64(result['mixed_magnitude']),
                'mixed_phase_preview': encode_image_base64(result['mixed_phase'])
            }), 200
            
        except Exception as e:
            task_data['status'] = 'failed'
            task_data['error'] = str(e)
            return jsonify({'error': str(e)}), 500
    else:
        # Task is still running
        elapsed = time.time() - task_data['start_time']
        progress = min(elapsed / 10.0, 0.99)  # Estimate progress
        
        return jsonify({
            'task_id': task_id,
            'status': 'processing',
            'progress': progress,
            'estimated_time_remaining': max(0, 10 - elapsed)
        }), 200

@ft_mixer_bp.route('/region', methods=['POST'])
def apply_region_filter():
    """Apply region filter to images"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        image_ids = data.get('image_ids', [])
        rectangle = data.get('rectangle', {})
        region_type = data.get('region_type', 'inner')
        apply_to_all = data.get('apply_to_all', True)
        
        # Validate rectangle
        required_fields = ['x', 'y', 'width', 'height']
        if not all(field in rectangle for field in required_fields):
            return jsonify({'error': 'Invalid rectangle specification'}), 400
        
        # Process each image
        results = {}
        for img_id in image_ids:
            if img_id not in image_store:
                continue
            
            ft_data = image_store[img_id]['ft_data']
            keep_inner = (region_type == 'inner')
            
            # Apply region filter
            filtered = ft_processor.apply_region_filter(ft_data, region_type, rectangle, keep_inner)
            
            # Inverse FFT to get filtered image
            filtered_ishift = np.fft.ifftshift(filtered)
            filtered_image = np.real(np.fft.ifft2(filtered_ishift))
            filtered_image = np.clip(filtered_image, 0, 1)
            
            # Generate preview
            preview = encode_image_base64(filtered_image)
            
            results[img_id] = {
                'preview': preview,
                'region_type': region_type,
                'rectangle': rectangle
            }
        
        return jsonify({
            'results': results,
            'message': f'Region filter applied to {len(results)} images'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ft_mixer_bp.route('/adjust', methods=['POST'])
def adjust_brightness_contrast():
    """Adjust brightness and contrast of an image"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        image_id = data.get('image_id')
        brightness = data.get('brightness', 0.0)
        contrast = data.get('contrast', 1.0)
        component = data.get('component')
        
        if image_id not in image_store:
            return jsonify({'error': 'Image not found'}), 404
        
        # Get image data
        image_data = image_store[image_id]
        image_array = image_data['image_array']
        
        # Apply adjustment
        adjusted = ft_processor.adjust_brightness_contrast(image_array, brightness, contrast)
        
        # Update stored image
        image_store[image_id]['image_array'] = adjusted
        
        # Recompute FT with adjusted image
        ft_data = ft_processor.compute_ft(adjusted)
        image_store[image_id]['ft_data'] = ft_data
        
        # Generate preview
        preview = encode_image_base64(adjusted)
        
        return jsonify({
            'image_id': image_id,
            'preview': preview,
            'brightness': brightness,
            'contrast': contrast,
            'message': 'Brightness/contrast adjusted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ft_mixer_bp.route('/task/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    """Cancel a processing task"""
    if task_id not in processing_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task_data = processing_tasks[task_id]
    task = task_data['task']
    
    # Try to cancel the task
    if not task.done():
        task.cancel()
        task_data['status'] = 'cancelled'
    
    return jsonify({
        'task_id': task_id,
        'status': 'cancelled',
        'message': 'Task cancelled successfully'
    }), 200

@ft_mixer_bp.route('/clear', methods=['POST'])
def clear_images():
    """Clear all uploaded images"""
    global image_store, processing_tasks
    
    # Clear image store
    for img_id, data in image_store.items():
        if os.path.exists(data['filepath']):
            os.remove(data['filepath'])
    
    image_store = {}
    processing_tasks = {}
    
    return jsonify({
        'message': 'All images cleared successfully'
    }), 200