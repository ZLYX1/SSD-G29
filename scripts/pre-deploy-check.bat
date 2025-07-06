@echo off
echo 🚀 Safe Companions Pre-Deployment Validation
echo ==================================================

echo Running pre-deployment checks...
python scripts\pre-deploy-check.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Pre-deployment checks failed!
    echo Please fix the issues before deploying to production.
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ✅ All checks passed! Ready for deployment.
    echo.
    pause
    exit /b 0
)
