"""
Image-related API endpoints.
"""
from flask import Blueprint, request, jsonify
import traceback

from core.image_processor import ImageProcessor
from core.fft_processor import FFTProcessor
from core.storage import storage
from utils.validators import Validator
from utils.converters import Converter
from utils.helpers import Helper

image_bp = Blueprint('images', __name__)


@image_bp.route('/upload', methods=['POST'])
def upload_image():
    """
    Handle image upload and convert to grayscale.
    Automatically resizes all images to unified size.
    """
    try:
        # Validate file
        if 'image' not in request.files:
            return Helper.create_error_response('No image file provided')
        
        file = request.files['image']
        is_valid, error_msg = Validator.validate_file_upload(file)
        if not is_valid:
            return Helper.create_error_response(error_msg)
        
        # Get image slot ID
        image_id = request.form.get('imageId', '1')
        
        # Read and decode image
        image_bytes = file.read()
        img = ImageProcessor.decode_image(image_bytes)
        if img is None:
            return Helper.create_error_response('Failed to decode image')
        
        # Convert to grayscale
        gray_img = ImageProcessor.convert_to_grayscale(img)
        
        # Store original image
        storage.store_original(image_id, gray_img)
        
        # Reprocess all images to unify sizes
        updated_display_components = FFTProcessor.reprocess_all_images()
        
        # Get current unified size
        unified_size = storage.get_unified_size()
        
        # Get this image's resized version
        resized_img = storage.get_resized(image_id)
        
        # Prepare response data
        this_image_data = updated_display_components.get(image_id, {})
        
        # Convert all components to base64
        response_data = {
            'image': Converter.numpy_to_base64(resized_img),
            'width': unified_size[1] if unified_size else gray_img.shape[1],
            'height': unified_size[0] if unified_size else gray_img.shape[0],
            'magnitude': Converter.numpy_to_base64(this_image_data.get('magnitude')),
            'phase': Converter.numpy_to_base64(this_image_data.get('phase')),
            'real': Converter.numpy_to_base64(this_image_data.get('real')),
            'imaginary': Converter.numpy_to_base64(this_image_data.get('imaginary')),
        }
        
        # Add updated images for all slots
        updated_images = {}
        for img_id, components in updated_display_components.items():
            updated_images[img_id] = {
                'image': Converter.numpy_to_base64(storage.get_resized(img_id)),
                'magnitude': Converter.numpy_to_base64(components['magnitude']),
                'phase': Converter.numpy_to_base64(components['phase']),
                'real': Converter.numpy_to_base64(components['real']),
                'imaginary': Converter.numpy_to_base64(components['imaginary']),
            }
        
        response_data['updatedImages'] = updated_images
        
        return jsonify(Helper.create_success_response(response_data))
    
    except Exception as e:
        traceback.print_exc()
        return Helper.create_error_response(str(e), 500)


@image_bp.route('/process_fft', methods=['POST'])
def process_fft():
    """
    Process FFT on server side and store for mixing.
    (Alternative endpoint for when image is sent as base64)
    """
    try:
        data = request.json
        image_data = data.get('image')
        image_id = str(data.get('imageId', '1'))
        
        if not image_data:
            return Helper.create_error_response('No image data provided')
        
        # Decode base64 image
        img = Converter.base64_to_numpy(image_data)
        if img is None:
            return Helper.create_error_response('Failed to decode image')
        
        # Store original
        storage.store_original(image_id, img)
        
        # Compute FFT
        fft_data = FFTProcessor.compute_fft(img)
        storage.store_fft(image_id, fft_data)
        
        # Prepare display components
        display_components = FFTProcessor.prepare_display_components(fft_data)
        
        # Convert to base64
        response_data = Converter.components_to_base64(display_components)
        
        return jsonify(Helper.create_success_response(response_data))
    
    except Exception as e:
        traceback.print_exc()
        return Helper.create_error_response(str(e), 500)


@image_bp.route('/adjust_brightness_contrast', methods=['POST'])
def adjust_brightness_contrast():
    """Adjust brightness and contrast of an image."""
    try:
        data = request.json
        image_data = data.get('image')
        brightness = data.get('brightness', 0)
        contrast = data.get('contrast', 0)
        
        if not image_data:
            return Helper.create_error_response('No image data provided')
        
        # Validate parameters
        is_valid, error_msg = Validator.validate_brightness_contrast(brightness, contrast)
        if not is_valid:
            return Helper.create_error_response(error_msg)
        
        # Decode base64 image
        img = Converter.base64_to_numpy(image_data)
        if img is None:
            return Helper.create_error_response('Failed to decode image')
        
        # Apply brightness and contrast
        adjusted = ImageProcessor.adjust_brightness_contrast(img, brightness, contrast)
        
        # Convert to base64
        result_base64 = Converter.numpy_to_base64(adjusted)
        
        return jsonify(Helper.create_success_response({'image': result_base64}))
    
    except Exception as e:
        traceback.print_exc()
        return Helper.create_error_response(str(e), 500)
