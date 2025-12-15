# Migration Guide: From Monolithic to Modular Backend

## Overview

This guide explains how to migrate from the original monolithic `app.py` to the new modular structure.

## What Changed?

### Before (Original)
```
backend/
├── app.py              # ~463 lines, everything in one file
└── requirements.txt
```

### After (Refactored)
```
backend/
├── app.py              # Original (preserved)
├── app_refactored.py   # New entry point using modular structure
├── requirements.txt
├── config.py           # Configuration management
├── api/                # API routes (blueprints)
│   ├── __init__.py
│   ├── routes.py
│   ├── image_routes.py
│   └── mixing_routes.py
├── core/               # Business logic
│   ├── __init__.py
│   ├── image_processor.py
│   ├── fft_processor.py
│   ├── mixer.py
│   └── storage.py
├── utils/              # Utilities
│   ├── __init__.py
│   ├── validators.py
│   ├── converters.py
│   └── helpers.py
├── middleware/         # Middleware
│   ├── __init__.py
│   └── error_handlers.py
└── tests/              # Test suite
    └── __init__.py
```

## Migration Options

### Option 1: Use Both (Recommended for Testing)

Keep both versions during transition:
- `app.py` - Original monolithic version (backup)
- `app_refactored.py` - New modular version

**To run original:**
```bash
cd backend
python app.py
```

**To run refactored:**
```bash
cd backend
python app_refactored.py
```

### Option 2: Replace Original

Once you've tested and are satisfied with the refactored version:

1. Backup the original:
   ```bash
   mv backend/app.py backend/app_original.py
   ```

2. Rename refactored to main:
   ```bash
   mv backend/app_refactored.py backend/app.py
   ```

3. Update documentation to reflect the change.

### Option 3: Gradual Migration

You can also gradually migrate by:
1. Start using the new modules in the original `app.py`
2. Replace functions one by one
3. Eventually transition to the application factory pattern

## Testing the Refactored Backend

### 1. Install Dependencies (if not already done)
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Server
```bash
python app_refactored.py
```

### 3. Test Endpoints

**Health Check:**
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "success": true,
  "status": "ok",
  "message": "FT Mixer API is running"
}
```

**Upload Image:**
```bash
curl -X POST -F "image=@test_image.png" -F "imageId=1" \
  http://localhost:5000/api/upload
```

**Mix Images:**
```bash
curl -X POST http://localhost:5000/api/mix_images \
  -H "Content-Type: application/json" \
  -d '{
    "images": [
      {"id": "1", "weight": 0.5},
      {"id": "2", "weight": 0.5}
    ],
    "component": "magnitude",
    "regionType": "full",
    "regionSize": 0.5
  }'
```

## Key Differences

### Configuration

**Original:**
```python
# Hard-coded in app.py
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
```

**Refactored:**
```python
# Centralized in config.py
from config import config
app.config.from_object(config['development'])
```

### Routes

**Original:**
```python
@app.route('/upload', methods=['POST'])
def upload_image():
    # Route implementation
    pass
```

**Refactored:**
```python
# In api/image_routes.py
from flask import Blueprint
image_bp = Blueprint('images', __name__)

@image_bp.route('/upload', methods=['POST'])
def upload_image():
    # Route implementation
    pass
```

### Business Logic

**Original:**
```python
# Mixed with route
@app.route('/upload', methods=['POST'])
def upload_image():
    # All logic here including:
    # - File validation
    # - Image processing
    # - FFT computation
    # - Storage
    # - Response formatting
```

**Refactored:**
```python
# Separated into modules
from core.image_processor import ImageProcessor
from core.fft_processor import FFTProcessor
from core.storage import storage

@image_bp.route('/upload', methods=['POST'])
def upload_image():
    # Route only coordinates the flow
    img = ImageProcessor.convert_to_grayscale(img)
    storage.store_original(image_id, img)
    fft_data = FFTProcessor.compute_fft(img)
```

## Benefits of the Refactored Version

1. **Maintainability**: Clear separation makes code easier to understand and modify
2. **Testability**: Each module can be tested independently
3. **Reusability**: Core logic can be used in different contexts
4. **Scalability**: Easy to add new features without bloating main file
5. **Team Collaboration**: Multiple developers can work on different modules
6. **Best Practices**: Follows Flask and Python community standards

## API Compatibility

✅ **The refactored backend is 100% API compatible with the original.**

All endpoints maintain the same:
- URLs
- Request formats
- Response formats
- Behavior

The frontend requires **no changes** to work with the refactored backend.

## Troubleshooting

### Import Errors

If you get import errors like `ModuleNotFoundError`:

```bash
# Make sure you're in the backend directory
cd backend

# Run Python from the backend directory
python app_refactored.py

# Or set PYTHONPATH
export PYTHONPATH=/path/to/backend:$PYTHONPATH
python app_refactored.py
```

### Port Already in Use

If port 5000 is already in use:

1. Stop the other process, or
2. Modify the port in `config.py`:
   ```python
   PORT = 5001  # or any available port
   ```

### CORS Issues

If you have CORS problems, update `config.py`:
```python
CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5173']
```

## Next Steps

1. **Test thoroughly**: Compare behavior with original version
2. **Add tests**: Create unit tests in the `tests/` directory
3. **Add logging**: Implement proper logging for debugging
4. **Documentation**: Add docstrings and API documentation
5. **Environment variables**: Use `.env` file for configuration
6. **CI/CD**: Set up automated testing and deployment

## Rollback Plan

If you need to rollback to the original:

1. If you kept both files, just use `app.py`
2. If you replaced it, restore from `app_original.py` or git history
3. The original is always available in git history:
   ```bash
   git checkout HEAD~1 backend/app.py
   ```

## Support

For questions or issues with the migration:
1. Review the `BACKEND_STRUCTURE.md` for detailed documentation
2. Check the original `app.py` for reference implementation
3. Consult Flask documentation for blueprints and application factory pattern
