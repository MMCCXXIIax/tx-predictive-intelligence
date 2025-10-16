@echo off
echo ========================================
echo TX Backend - Railway Deployment Fix
echo ========================================
echo.

echo Step 1: Adding files to git...
git add requirements-light.txt RAILWAY_DEPLOY_FIX.md deploy-railway.bat
echo.

echo Step 2: Committing changes...
git commit -m "Fix Railway build timeout - use lightweight requirements"
echo.

echo Step 3: Pushing to GitHub...
git push origin main
echo.

echo ========================================
echo DONE! Now do this in Railway dashboard:
echo ========================================
echo.
echo 1. Go to your Railway service
echo 2. Click "Variables" tab
echo 3. Add new variable:
echo    Name: NIXPACKS_PYTHON_REQUIREMENTS_FILE
echo    Value: requirements-light.txt
echo 4. Click "Deploy" or wait for auto-deploy
echo.
echo Your backend will be live in 2-3 minutes!
echo ========================================
pause
