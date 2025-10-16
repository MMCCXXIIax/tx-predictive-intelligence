@echo off
echo ========================================
echo TX Backend - Docker Build and Deploy
echo ========================================
echo.

echo Step 1: Building Docker image (this takes 10-15 min first time)...
echo Building with PyTorch and all AI features...
echo.

docker build -t tx-backend:latest .

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Docker build failed!
    echo Make sure Docker Desktop is running.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build successful! Now testing locally...
echo ========================================
echo.

echo Step 2: Testing image locally...
docker run -d -p 5000:5000 --name tx-backend-test --env-file .env tx-backend:latest

echo.
echo Waiting 10 seconds for app to start...
timeout /t 10 /nobreak > nul

echo.
echo Testing health endpoint...
curl http://localhost:5000/health

echo.
echo.
echo ========================================
echo Local test complete!
echo ========================================
echo.
echo To push to Docker Hub and deploy to Railway:
echo.
echo 1. Login to Docker Hub:
echo    docker login
echo.
echo 2. Tag image:
echo    docker tag tx-backend:latest YOUR-DOCKERHUB-USERNAME/tx-backend:latest
echo.
echo 3. Push image:
echo    docker push YOUR-DOCKERHUB-USERNAME/tx-backend:latest
echo.
echo 4. In Railway dashboard:
echo    - New Project
echo    - Deploy from Docker Image
echo    - Enter: YOUR-DOCKERHUB-USERNAME/tx-backend:latest
echo    - Add environment variables
echo    - Deploy (2 minutes!)
echo.
echo ========================================
echo.
echo To stop test container:
echo    docker stop tx-backend-test
echo    docker rm tx-backend-test
echo.
pause
