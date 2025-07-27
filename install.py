#!/usr/bin/env python3
"""
XSS Sentinel Installation Script
Installs all required dependencies with proper error handling
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_core_dependencies():
    """Install core dependencies"""
    core_packages = [
        "requests>=2.28.1",
        "beautifulsoup4>=4.11.1", 
        "scikit-learn>=1.1.2",
        "numpy>=1.23.2",
        "tqdm>=4.64.0",
        "colorama>=0.4.5",
        "joblib>=1.1.0",
        "lxml>=4.9.0",
        "selenium>=4.0.0",
        "fake-useragent>=1.1.0",
        "cloudscraper>=1.2.0",
        "undetected-chromedriver>=3.5.0",
        "requests-html>=0.10.0",
        "aiohttp>=3.8.0",
        "asyncio-throttle>=1.0.0",
        "python-whois>=0.8.0",
        "dnspython>=2.3.0",
        "cryptography>=3.4.0",
        "pycryptodome>=3.15.0",
        "urllib3>=1.26.0",
        "playwright>=1.40.0"
    ]
    
    for package in core_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            return False
    return True

def install_ai_dependencies():
    """Install AI dependencies (optional)"""
    print("\n🤖 Installing AI/ML dependencies (optional)...")
    
    ai_packages = [
        "sentence-transformers>=2.2.0",
        "transformers>=4.20.0", 
        "torch>=1.12.0",
        "tensorflow>=2.10.0"
    ]
    
    success_count = 0
    for package in ai_packages:
        if run_command(f"pip install {package}", f"Installing {package}"):
            success_count += 1
        else:
            print(f"⚠️ Warning: Failed to install {package}. AI features will be limited.")
    
    if success_count == len(ai_packages):
        print("✅ All AI dependencies installed successfully")
    elif success_count > 0:
        print(f"⚠️ {success_count}/{len(ai_packages)} AI dependencies installed. Some AI features may be limited.")
    else:
        print("❌ No AI dependencies installed. AI features will be disabled.")
    
    return success_count > 0

def install_development_dependencies():
    """Install development dependencies (optional)"""
    print("\n🔧 Installing development dependencies (optional)...")
    
    dev_packages = [
        "pytest>=7.0.0",
        "flake8>=5.0.0", 
        "black>=22.0.0"
    ]
    
    for package in dev_packages:
        run_command(f"pip install {package}", f"Installing {package}")
    
    print("✅ Development dependencies installation completed")

def install_package():
    """Install the XSS Sentinel package"""
    print("\n📦 Installing XSS Sentinel package...")
    return run_command("pip install -e .", "Installing XSS Sentinel in development mode")

def setup_playwright():
    """Setup Playwright browsers"""
    print("\n🌐 Setting up Playwright browsers...")
    return run_command("playwright install", "Installing Playwright browsers")

def main():
    """Main installation function"""
    print("🚀 XSS Sentinel Installation Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install core dependencies
    print("\n📚 Installing core dependencies...")
    if not install_core_dependencies():
        print("❌ Core dependencies installation failed")
        sys.exit(1)
    
    # Install AI dependencies
    install_ai_dependencies()
    
    # Install development dependencies
    install_development_dependencies()
    
    # Install the package
    if not install_package():
        print("❌ Package installation failed")
        sys.exit(1)
    
    # Setup Playwright
    setup_playwright()
    
    print("\n🎉 Installation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Test the installation: xss-sentinel --help")
    print("2. Run a quick test: xss-sentinel https://example.com --mode quick")
    print("3. For AI features, ensure all AI dependencies were installed")
    
    print("\n📖 For more information, see the README.md file")

if __name__ == "__main__":
    main() 