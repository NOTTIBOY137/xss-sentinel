@echo off
REM XSS Sentinel v2.0 Neural Engine - Windows Installation Script
echo ====================================================================
echo  XSS SENTINEL v2.0 NEURAL ENGINE - WINDOWS INSTALLATION
echo ====================================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [STEP 1/6] Python detected
python --version
echo.

REM Create virtual environment
echo [STEP 2/6] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created
)
echo.

REM Activate virtual environment
echo [STEP 3/6] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated
echo.

REM Upgrade pip
echo [STEP 4/6] Upgrading pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing anyway...
)
echo.

REM Install core dependencies
echo [STEP 5/6] Installing core dependencies...
echo This may take a few minutes...
python -m pip install requests beautifulsoup4 numpy scikit-learn tqdm colorama pytest --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install core dependencies
    pause
    exit /b 1
)
echo Core dependencies installed
echo.

REM Install optional neural dependencies
echo [STEP 6/6] Install neural engine dependencies?
echo This includes PyTorch and OpenCV (~2GB download)
set /p INSTALL_NEURAL="Install neural dependencies? (y/n): "

if /i "%INSTALL_NEURAL%"=="y" (
    echo Installing neural dependencies...
    echo This may take 10-15 minutes depending on your connection...
    python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --quiet
    python -m pip install opencv-python Pillow --quiet
    if errorlevel 1 (
        echo [WARNING] Some neural dependencies may have failed to install
        echo You can install them later with: pip install torch torchvision opencv-python
    ) else (
        echo Neural dependencies installed
    )
) else (
    echo Skipping neural dependencies
    echo You can install them later with: pip install torch torchvision opencv-python
)

echo.
echo ====================================================================
echo Installation Complete!
echo ====================================================================
echo.
echo To activate the environment in the future:
echo   venv\Scripts\activate
echo.
echo To run the quick test:
echo   python examples\quick_test.py
echo.
echo To run a demo:
echo   python examples\simple_demo.py
echo.
echo Documentation: README_NEURAL_ENGINE.md
echo.
pause
