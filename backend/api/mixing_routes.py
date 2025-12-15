"""
Mixing-related API endpoints.
"""
from flask import Blueprint, request, jsonify
import traceback

from core.mixer import Mixer
from utils.validators import Validator
from utils.converters import Converter
from utils.helpers import Helper

mixing_bp = Blueprint('mixing', __name__)


@mixing_bp.route('/mix_images', methods=['POST'])
def mix_images():
    """
    Mix images based on FT components with weighted average.
    Supports cancellation of previous mixing tasks.
    """
    try:
        data = request.json
        
        # Validate mixing parameters
        is_valid, error_msg = Validator.validate_mixing_params(data)
        if not is_valid:
            return Helper.create_error_response(error_msg)
        
        # Extract parameters
        image_weights = {str(img['id']): img['weight'] for img in data.get('images', [])}
        component = data.get('component', 'magnitude')
        region_type = data.get('regionType', 'full')
        region_size = data.get('regionSize', 0.5)
        
        # Perform mixing
        result_img = Mixer.mix_images(
            image_weights=image_weights,
            component=component,
            region_type=region_type,
            region_size=region_size
        )
        
        # Convert to base64
        result_base64 = Converter.numpy_to_base64(result_img)
        
        return jsonify(Helper.create_success_response({'result': result_base64}))
    
    except ValueError as e:
        return Helper.create_error_response(str(e), 400)
    except Exception as e:
        traceback.print_exc()
        return Helper.create_error_response(str(e), 500)
