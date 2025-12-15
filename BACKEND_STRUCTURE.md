# Backend Structure Documentation

## Current State

The backend is currently a single monolithic `app.py` file (~463 lines) containing:
- Flask application setup
- CORS configuration
- Image upload handling
- FFT processing
- Image mixing logic
- Brightness/contrast adjustment
- All business logic mixed with routing

## Issues with Current Structure

1. **Monolithic Design**: All code in one file makes it hard to maintain and test
2. **No Separation of Concerns**: Routes, business logic, and utilities are mixed
3. **No Configuration Management**: Hard-coded values scattered throughout
4. **No Modular Organization**: Difficult to scale or add new features
5. **Limited Testability**: Hard to unit test individual components
6. **No Error Handling Centralization**: Error handling is repeated
7. **Global State Management**: Using global variables for image data storage

## Recommended Backend Structure

```
backend/
├── app.py                      # Application entry point (minimal)
├── requirements.txt            # Python dependencies
├── config.py                   # Configuration management
├── api/                        # API layer
│   ├── __init__.py
│   ├── routes.py              # Main routes blueprint
│   ├── image_routes.py        # Image-related endpoints
│   └── mixing_routes.py       # Mixing-related endpoints
├── core/                       # Core business logic
│   ├── __init__.py
│   ├── image_processor.py     # Image processing logic
│   ├── fft_processor.py       # FFT computation and management
│   ├── mixer.py               # Image mixing algorithms
│   └── storage.py             # Data storage management
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── validators.py          # Input validation
│   ├── converters.py          # Image format conversions
│   └── helpers.py             # Helper functions
├── middleware/                 # Middleware components
│   ├── __init__.py
│   └── error_handlers.py      # Centralized error handling
└── tests/                      # Test suite (optional but recommended)
    ├── __init__.py
    ├── test_image_processor.py
    ├── test_fft_processor.py
    └── test_mixer.py
```

## Module Responsibilities

### 1. `app.py` - Application Entry Point
- Create Flask application instance
- Register blueprints
- Configure middleware
- Initialize extensions (CORS, etc.)
- Start the server

### 2. `config.py` - Configuration Management
- Application settings (host, port, debug mode)
- File upload limits
- Directory paths (upload folder, static files)
- CORS settings
- Environment-based configuration

### 3. `api/` - API Layer
**Purpose**: Handle HTTP requests and responses

- `routes.py`: Main routes (health check, index)
- `image_routes.py`: Image upload, FFT processing endpoints
- `mixing_routes.py`: Image mixing endpoints
- Use Flask Blueprints for modularity
- Keep routes thin - delegate to core layer

### 4. `core/` - Business Logic Layer
**Purpose**: Core application logic, independent of HTTP

- `image_processor.py`: 
  - Grayscale conversion
  - Image resizing
  - Brightness/contrast adjustment
  - Image normalization

- `fft_processor.py`:
  - FFT computation
  - FFT component extraction (magnitude, phase, real, imaginary)
  - FFT data storage and management
  - Unified size management

- `mixer.py`:
  - Weighted mixing algorithms
  - Region mask creation
  - Inverse FFT reconstruction
  - Component mixing logic

- `storage.py`:
  - Manage image data storage
  - FFT data storage
  - Thread-safe operations
  - Data retrieval and updates

### 5. `utils/` - Utility Functions
**Purpose**: Reusable helper functions

- `validators.py`:
  - Validate file uploads
  - Validate mixing parameters
  - Validate image dimensions

- `converters.py`:
  - Base64 encoding/decoding
  - NumPy to image conversions
  - Format conversions

- `helpers.py`:
  - Common helper functions
  - Math utilities
  - Array operations

### 6. `middleware/` - Middleware Components
**Purpose**: Request/response processing

- `error_handlers.py`:
  - Centralized error handling
  - Custom error responses
  - Logging
  - Error formatters

## Benefits of This Structure

### 1. **Maintainability**
- Clear separation of concerns
- Easy to locate and modify code
- Logical organization

### 2. **Scalability**
- Easy to add new features
- Modular components can be extended independently
- Can add new blueprints for new functionality

### 3. **Testability**
- Core logic separated from HTTP layer
- Easy to write unit tests
- Mock dependencies easily

### 4. **Reusability**
- Core modules can be used in different contexts
- Utilities can be shared across modules
- Business logic independent of web framework

### 5. **Team Collaboration**
- Multiple developers can work on different modules
- Clear ownership of components
- Reduced merge conflicts

### 6. **Code Quality**
- Easier to enforce coding standards
- Better error handling
- Improved logging and debugging

## Migration Strategy

### Phase 1: Create Structure
1. Create directory structure
2. Create `__init__.py` files
3. Create empty module files

### Phase 2: Extract Configuration
1. Move configuration to `config.py`
2. Update references to use config

### Phase 3: Extract Core Logic
1. Move FFT logic to `fft_processor.py`
2. Move image processing to `image_processor.py`
3. Move mixing logic to `mixer.py`
4. Move storage logic to `storage.py`

### Phase 4: Extract Utilities
1. Move validators to `validators.py`
2. Move converters to `converters.py`
3. Move helpers to `helpers.py`

### Phase 5: Create API Blueprints
1. Create blueprints for routes
2. Move routes to appropriate blueprint files
3. Keep routes thin

### Phase 6: Add Middleware
1. Create error handlers
2. Add logging middleware
3. Add request validation

### Phase 7: Update Entry Point
1. Simplify `app.py`
2. Use application factory pattern
3. Register all components

### Phase 8: Testing & Validation
1. Test all endpoints
2. Verify functionality
3. Check for regressions

## Best Practices

### 1. **Use Application Factory Pattern**
```python
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app)
    
    # Register blueprints
    from api.image_routes import image_bp
    from api.mixing_routes import mixing_bp
    app.register_blueprint(image_bp, url_prefix='/api')
    app.register_blueprint(mixing_bp, url_prefix='/api')
    
    return app
```

### 2. **Use Blueprints for Routing**
```python
from flask import Blueprint

image_bp = Blueprint('images', __name__)

@image_bp.route('/upload', methods=['POST'])
def upload_image():
    # Route logic
    pass
```

### 3. **Separate Business Logic**
```python
# In core/image_processor.py
class ImageProcessor:
    @staticmethod
    def convert_to_grayscale(image):
        # Pure business logic
        pass
```

### 4. **Use Dependency Injection**
```python
# Routes receive dependencies
@image_bp.route('/upload', methods=['POST'])
def upload_image():
    processor = ImageProcessor()
    result = processor.process(request.files['image'])
    return jsonify(result)
```

### 5. **Centralized Error Handling**
```python
# In middleware/error_handlers.py
@app.errorhandler(Exception)
def handle_exception(e):
    # Log error
    # Return formatted response
    pass
```

### 6. **Configuration Management**
```python
# In config.py
class Config:
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = 'uploads'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
```

## Additional Recommendations

### 1. **Add Type Hints**
Use Python type hints for better code documentation and IDE support:
```python
def resize_image(img: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    return cv2.resize(img, (target_size[1], target_size[0]))
```

### 2. **Add Logging**
Implement proper logging instead of print statements:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Processing image upload")
```

### 3. **Add Input Validation**
Validate all inputs before processing:
```python
def validate_image_upload(file):
    if not file:
        raise ValueError("No file provided")
    if not allowed_file(file.filename):
        raise ValueError("Invalid file type")
```

### 4. **Add Documentation**
Use docstrings for all functions and classes:
```python
def create_region_mask(shape, region_type, region_size):
    """
    Create a mask for inner/outer region selection.
    
    Args:
        shape: Tuple of (height, width)
        region_type: 'full', 'inner', or 'outer'
        region_size: Float between 0 and 1
    
    Returns:
        numpy.ndarray: Binary mask
    """
```

### 5. **Add Environment Variables**
Use environment variables for sensitive configuration:
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
```

### 6. **Add API Versioning**
Prepare for future API changes:
```python
app.register_blueprint(image_bp, url_prefix='/api/v1')
```

### 7. **Add Request/Response Schemas**
Use schemas for validation and documentation:
```python
# Could use marshmallow or pydantic
from marshmallow import Schema, fields

class ImageUploadSchema(Schema):
    image = fields.Raw(required=True)
    imageId = fields.String(required=True)
```

## Conclusion

The recommended structure provides:
- ✅ Clear separation of concerns
- ✅ Better maintainability and testability
- ✅ Easier collaboration
- ✅ Professional code organization
- ✅ Scalability for future features
- ✅ Industry best practices

This structure follows Flask and Python best practices and is suitable for a production-grade application.
