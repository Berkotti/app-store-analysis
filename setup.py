#!/usr/bin/env python
"""
Setup script for App Store Analysis project
Created: 2025-08-29
Updated: 2025-08-29
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.9+"""
    if sys.version_info < (3, 9):
        print("Error: Python 3.9 or higher is required.")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✓ Python version: {sys.version}")


def create_virtual_env():
    """Create virtual environment if it doesn't exist"""
    venv_path = Path(".venv")
    
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"])
        print("✓ Virtual environment created")
    else:
        print("✓ Virtual environment already exists")


def install_requirements():
    """Install required packages"""
    print("\nInstalling requirements...")
    
    # Determine pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = Path(".venv/Scripts/pip")
    else:  # Unix/Linux/Mac
        pip_path = Path(".venv/bin/pip")
    
    if not pip_path.exists():
        print("Error: pip not found in virtual environment")
        print("Please activate the virtual environment and run: pip install -r requirements.txt")
        return False
    
    # Upgrade pip first
    subprocess.run([str(pip_path), "install", "--upgrade", "pip"])
    
    # Install requirements
    result = subprocess.run([str(pip_path), "install", "-r", "requirements.txt"])
    
    if result.returncode == 0:
        print("✓ Requirements installed successfully")
        return True
    else:
        print("Error installing requirements")
        return False


def setup_kaggle_credentials():
    """Help user set up Kaggle credentials"""
    print("\n=== Kaggle API Setup ===")
    print("To use Kaggle datasets, you need to set up API credentials:")
    print("1. Go to https://www.kaggle.com/account")
    print("2. Scroll to 'API' section")
    print("3. Click 'Create New API Token'")
    print("4. Save the downloaded kaggle.json file to ~/.kaggle/")
    print("   OR")
    print("   Copy your username and key to the .env file")
    
    # Check if .env exists
    if not Path(".env").exists():
        print("\nCreating .env file from template...")
        if Path(".env.example").exists():
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("✓ .env file created. Please edit it with your credentials.")
    else:
        print("✓ .env file already exists")


def create_directories():
    """Create necessary directories"""
    dirs = [
        "data/raw/kaggle",
        "data/raw/api", 
        "data/raw/scraped",
        "data/processed",
        "data/cache/api_responses",
        "data/cache/scrape_sessions",
        "logs",
        "models",
        "outputs"
    ]
    
    print("\nCreating project directories...")
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✓ All directories created")


def main():
    """Main setup function"""
    print("=" * 50)
    print("App Store Analysis Project Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    create_virtual_env()
    
    # Create directories
    create_directories()
    
    # Install requirements
    success = install_requirements()
    
    if success:
        # Setup Kaggle
        setup_kaggle_credentials()
        
        print("\n" + "=" * 50)
        print("✓ Setup completed successfully!")
        print("=" * 50)
        print("\nNext steps:")
        print("1. Activate virtual environment:")
        if os.name == 'nt':
            print("   .venv\\Scripts\\activate")
        else:
            print("   source .venv/bin/activate")
        print("2. Configure .env file with your API credentials")
        print("3. Run data collection:")
        print("   python src/data_collection/kaggle_downloader.py")
        print("   python src/data_collection/itunes_api.py")
        print("4. Start Jupyter notebook:")
        print("   jupyter notebook")
    else:
        print("\n⚠ Setup completed with warnings")
        print("Please install requirements manually:")
        print("pip install -r requirements.txt")


if __name__ == "__main__":
    main()