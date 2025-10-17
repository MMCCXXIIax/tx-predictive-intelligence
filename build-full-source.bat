@echo off
REM ============================================
REM TX BACKEND - FULL SOURCE BUILD (WSL2)
REM This script uses WSL2 for optimal Docker performance
REM ============================================

echo ========================================
echo TX BACKEND - FULL SOURCE BUILD
echo ========================================
echo.

REM Check if WSL2 is installed
wsl --status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: WSL2 is not installed!
    echo.
    echo To install WSL2:
    echo 1. Open PowerShell as Administrator
    echo 2. Run: wsl --install
    echo 3. Restart your computer
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)

echo WSL2 detected! ✓
echo.

REM Check if Docker is installed in WSL2
wsl docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Docker is not installed in WSL2!
    echo.
    echo To install Docker in WSL2:
    echo 1. Open WSL2: wsl
    echo 2. Run: curl -fsSL https://get.docker.com -o get-docker.sh
    echo 3. Run: sudo sh get-docker.sh
    echo 4. Run: sudo usermod -aG docker $USER
    echo 5. Run: sudo service docker start
    echo 6. Run this script again
    echo.
    pause
    exit /b 1
)

echo Docker detected in WSL2! ✓
echo.

REM Start Docker service in WSL2
echo Starting Docker service...
wsl sudo service docker start >nul 2>&1
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo BUILDING FROM SOURCE IN WSL2
echo ========================================
echo.
echo This will take 30-45 minutes
echo.
echo Timeline:
echo   - NumPy, SciPy, Pandas: 5-10 min
echo   - PyTorch (from source): 20-30 min
echo   - Everything else: 5-10 min
echo.
echo Progress will be shown below...
echo.
echo ========================================
echo.

REM Make build script executable and run it
wsl chmod +x "/mnt/c/Users/S/TX BACK/tx-predictive-intelligence/build-docker-wsl.sh"
wsl cd "/mnt/c/Users/S/TX BACK/tx-predictive-intelligence" ^&^& ./build-docker-wsl.sh

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Your Docker image is ready!
    echo.
    echo Next steps:
    echo 1. docker login
    echo 2. docker tag tx-backend:latest YOUR-USERNAME/tx-backend:latest
    echo 3. docker push YOUR-USERNAME/tx-backend:latest
    echo 4. Deploy to Railway
    echo.
) else (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo.
    echo Check build.log for details
    echo.
)

pause
