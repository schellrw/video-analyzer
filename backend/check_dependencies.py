#!/usr/bin/env python3
"""
Dependency Checker for Video Analyzer Platform
Checks which dependencies are installed and which are missing.
"""

import sys
import importlib

# Required dependencies for the optimized features
DEPENDENCIES = {
    'core': {
        'flask': 'Flask web framework',
        'celery': 'Async task processing',
        'sqlalchemy': 'Database ORM',
        'flask_jwt_extended': 'JWT authentication',
        'flask_cors': 'CORS support',
        'requests': 'HTTP client',
        'dotenv': 'Environment variables (python-dotenv)'
    },
    'ai_analysis': {
        'cv2': 'OpenCV for video processing (opencv-python)',
        'PIL': 'Image processing (Pillow)',
        'huggingface_hub': 'Hugging Face API client',
        'numpy': 'Numerical computing'
    },
    'reports': {
        'reportlab': 'PDF generation'
    },
    'caching': {
        'redis': 'Redis client (optional - for caching)'
    }
}

def check_dependency(module_name, description):
    """Check if a dependency is available."""
    try:
        importlib.import_module(module_name)
        return True, f"✅ {module_name}: {description}"
    except ImportError:
        return False, f"❌ {module_name}: {description} - NOT INSTALLED"

def main():
    """Check all dependencies."""
    print("🔍 Checking Video Analyzer Platform Dependencies")
    print("=" * 60)
    
    all_good = True
    missing_deps = []
    
    for category, deps in DEPENDENCIES.items():
        print(f"\n📦 {category.upper()} DEPENDENCIES:")
        category_good = True
        
        for module, description in deps.items():
            available, message = check_dependency(module, description)
            print(f"   {message}")
            
            if not available:
                category_good = False
                all_good = False
                missing_deps.append(module)
        
        if category_good:
            print(f"   ✅ All {category} dependencies available")
    
    print("\n" + "=" * 60)
    
    if all_good:
        print("🎉 All dependencies are installed!")
        print("✅ Your system is ready for the optimized video analysis features.")
    else:
        print("⚠️  Some dependencies are missing:")
        print("\nTo install missing dependencies:")
        
        # Group by likely pip package names
        pip_packages = []
        for dep in missing_deps:
            if dep == 'cv2':
                pip_packages.append('opencv-python')
            elif dep == 'PIL':
                pip_packages.append('Pillow')
            elif dep == 'dotenv':
                pip_packages.append('python-dotenv')
            elif dep == 'flask_jwt_extended':
                pip_packages.append('Flask-JWT-Extended')
            elif dep == 'flask_cors':
                pip_packages.append('Flask-CORS')
            elif dep == 'huggingface_hub':
                pip_packages.append('huggingface-hub')
            else:
                pip_packages.append(dep)
        
        if pip_packages:
            print(f"\npip install {' '.join(pip_packages)}")
        
        print("\nNote: Redis is optional for caching. The system will work without it,")
        print("but caching will be disabled (which is fine for testing).")
    
    print("\n🔧 REDIS SETUP NOTES:")
    print("- If you have REDIS_URL in your .env, that's all you need")
    print("- No local Redis server required (unless you want fallback)")
    print("- No Docker required for basic functionality")
    print("- Caching will be disabled gracefully if Redis is unavailable")

if __name__ == "__main__":
    main() 