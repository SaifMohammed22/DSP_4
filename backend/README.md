# Backend - FT Mixer API

Backend server for the Fourier Transform Magnitude/Phase Mixer application.

## Structure

This backend has been refactored from a monolithic design into a modular, maintainable architecture.

### Directory Layout

```
backend/
├── app.py                      # Original monolithic version (preserved)
├── app_refactored.py          # New modular entry point ⭐
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
│
├── api/                        # API Layer - HTTP routes
│   ├── routes.py              # Main routes (health check)
│   ├── image_routes.py        # Image upload & processing endpoints
│   └── mixing_routes.py       # Image mixing endpoints
│
├── core/                       # Core Business Logic
│   ├── storage.py             # Thread-safe data storage
│   ├── image_processor.py     # Image processing operations
│   ├── fft_processor.py       # FFT computation & management
│   └── mixer.py               # Image mixing algorithms
│
├── utils/                      # Utilities
│   ├── validators.py          # Input validation
│   ├── converters.py          # Data format conversions
│   └── helpers.py             # Helper functions
│
├── middleware/                 # Middleware Components
│   └── error_handlers.py      # Centralized error handling
│
└── tests/                      # Test Suite
    └── (test files here)
```

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**
   
   **Option A: Run refactored version (recommended):**
   ```bash
   python app_refactored.py
   ```
   
   **Option B: Run original version:**
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check
```
GET /api/health
```
Returns server status.

### Upload Image
```
POST /api/upload
Content-Type: multipart/form-data

Parameters:
- image: Image file
- imageId: Image slot ID (1-4)
```
Uploads and processes an image, converts to grayscale, computes FFT components.

### Process FFT
```
POST /api/process_fft
Content-Type: application/json

Body:
{
  "image": "base64_encoded_image",
  "imageId": "1"
}
```
Alternative endpoint for processing images sent as base64.

### Mix Images
```
POST /api/mix_images
Content-Type: application/json

Body:
{
  "images": [
    {"id": "1", "weight": 0.5},
    {"id": "2", "weight": 0.5}
  ],
  "component": "magnitude",
  "regionType": "full",
  "regionSize": 0.5
}
```
Mixes images based on FFT components with weighted averaging.

**Parameters:**
- `images`: Array of image objects with id and weight
- `component`: FFT component to mix (`magnitude`, `phase`, `real`, `imaginary`)
- `regionType`: Region selection (`full`, `inner`, `outer`)
- `regionSize`: Region size percentage (0-1)

### Adjust Brightness/Contrast
```
POST /api/adjust_brightness_contrast
Content-Type: application/json

Body:
{
  "image": "base64_encoded_image",
  "brightness": 0,
  "contrast": 0
}
```
Adjusts brightness and contrast of an image.

**Parameters:**
- `brightness`: -100 to 100
- `contrast`: -100 to 100

## Configuration

Configuration is managed in `config.py` with environment-specific settings:

- **Development**: Debug mode enabled, verbose logging
- **Production**: Debug mode disabled, security-focused
- **Testing**: Isolated configuration for tests

### Environment Variables

- `FLASK_ENV`: Set to `development`, `production`, or `testing`
- `SECRET_KEY`: Secret key for production (required in production)

## Architecture

### Application Factory Pattern

The refactored backend uses the application factory pattern:

```python
from app_refactored import create_app

app = create_app('development')
```

This provides:
- Easier testing
- Multiple app instances
- Cleaner configuration management

### Blueprints

Routes are organized into blueprints:
- `main_bp`: Core routes (health check)
- `image_bp`: Image-related endpoints
- `mixing_bp`: Mixing-related endpoints

### Separation of Concerns

```
Request → API Layer → Core Logic → Storage
              ↓
         Validation
              ↓
         Conversion
```

1. **API Layer**: Handles HTTP requests/responses
2. **Core Logic**: Business logic (independent of HTTP)
3. **Storage**: Thread-safe data management
4. **Utils**: Reusable utilities
5. **Middleware**: Cross-cutting concerns

## Key Features

### Thread-Safe Storage
The `core/storage.py` module provides thread-safe storage for:
- Original images
- Resized images (unified size)
- FFT data for each image
- Current mixing task

### Automatic Image Resizing
All uploaded images are automatically resized to the smallest uploaded image dimensions to ensure consistency.

### FFT Components
For each image, the backend computes:
- Magnitude spectrum
- Phase spectrum
- Real component
- Imaginary component

All normalized for display.

### Weighted Mixing
Supports weighted mixing of FFT components with:
- Custom weights per image
- Component selection
- Region selection (full, inner, outer)
- Adjustable region size

## Development

### Adding a New Endpoint

1. **Create route in appropriate blueprint:**
   ```python
   # In api/image_routes.py
   @image_bp.route('/new_endpoint', methods=['POST'])
   def new_endpoint():
       # Implementation
       pass
   ```

2. **Add business logic to core module:**
   ```python
   # In core/image_processor.py
   @staticmethod
   def new_operation(image):
       # Logic here
       pass
   ```

3. **Add tests:**
   ```python
   # In tests/test_image_processor.py
   def test_new_operation():
       # Test implementation
       pass
   ```

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to all functions/classes
- Keep functions focused and small
- Validate inputs
- Handle errors gracefully

## Testing

### Manual Testing

```bash
# Health check
curl http://localhost:5000/api/health

# Upload image
curl -X POST -F "image=@test.png" -F "imageId=1" \
  http://localhost:5000/api/upload
```

### Unit Tests

```bash
# Run tests (when implemented)
python -m pytest tests/
```

## Migration from Original

See `MIGRATION_GUIDE.md` for detailed migration instructions.

**Key Point:** Both versions are API-compatible. The frontend works with either version without changes.

## Performance Considerations

- Images are processed on-demand
- FFT data is cached in memory
- Thread locks prevent race conditions
- File size limited to 16MB

## Security

- File type validation
- File size limits
- Input validation for all endpoints
- CORS configuration
- Error message sanitization in production

## Troubleshooting

### Common Issues

**Import errors:**
```bash
# Ensure you're in the backend directory
cd backend
python app_refactored.py
```

**Port already in use:**
```bash
# Change port in config.py or use environment variable
PORT=5001 python app_refactored.py
```

**CORS errors:**
- Update `CORS_ORIGINS` in `config.py`
- Ensure frontend URL is allowed

## Documentation

- `BACKEND_STRUCTURE.md`: Detailed architecture documentation
- `MIGRATION_GUIDE.md`: Migration from original to refactored
- Code docstrings: Inline documentation

## Contributing

1. Follow the existing structure
2. Add tests for new features
3. Update documentation
4. Validate inputs
5. Handle errors properly

## License

Educational project for Digital Signal Processing course.
