#!/usr/bin/env python
"""
Startup script for Beamforming Simulator
This script handles environment setup and starts the Flask application
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Setup Python path and create necessary directories"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    backend_dir = project_root / 'backend'
    
    # Add backend to Python path
    sys.path.insert(0, str(backend_dir))
    
    # Create necessary directories
    directories = [
        backend_dir / 'scenarios',
        backend_dir / 'core',
        backend_dir / 'models',
        project_root / 'frontend' / 'static' / 'css',
        project_root / 'frontend' / 'static' / 'js',
        project_root / 'frontend' / 'templates'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Create __init__.py files for Python packages
    init_files = [
        backend_dir / 'core' / '__init__.py',
        backend_dir / 'models' / '__init__.py'
    ]
    
    for init_file in init_files:
        if not init_file.exists():
            init_file.touch()
            print(f"✓ Created package file: {init_file}")
    
    return backend_dir

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask',
        'flask_cors',
        'numpy',
        'scipy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("\n❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease install dependencies:")
        print("   pip install -r backend/requirements.txt")
        return False
    
    print("✓ All dependencies are installed")
    return True

def main():
    """Main startup function"""
    print("=" * 60)
    print("🎯 Beamforming Simulator - Starting Application")
    print("=" * 60)
    print()
    
    # Setup environment
    print("Setting up environment...")
    backend_dir = setup_environment()
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print()
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Import and run Flask app
    try:
        print("Starting Flask server...")
        print("-" * 60)
        from app import app
        
        # Run the application
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
        
    except ImportError as e:
        print(f"\n❌ Error importing application: {e}")
        print("\nPlease ensure all files are in the correct locations:")
        print("   - backend/app.py")
        print("   - backend/core/beamforming_simulator.py")
        print("   - backend/core/phased_array.py")
        print("   - backend/models/scenario_manager.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()