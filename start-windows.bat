@echo off
echo Starting SSD-G29 Messaging Application Setup for Windows Docker Desktop
echo.

REM Check if Docker Desktop is running
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running or not installed.
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo.

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: docker-compose is not available.
    echo Please ensure Docker Desktop includes docker-compose.
    pause
    exit /b 1
)

echo ✅ Docker Compose is available
echo.

REM Stop any existing containers
echo 🔄 Stopping any existing containers...
docker-compose -f docker-compose.dev.yml down

REM Build and start the containers
echo 🔄 Building and starting containers...
docker-compose -f docker-compose.dev.yml up --build -d

REM Wait for services to be ready
echo 🔄 Waiting for services to start...
timeout /t 10 /nobreak > nul

REM Check if containers are running
echo 🔍 Checking container status...
docker-compose -f docker-compose.dev.yml ps

echo.
echo ========================================
echo 🎉 Setup Complete!
echo.
echo Your application should now be running:
echo 📱 Web App:       http://localhost:5000
echo 🗄️  Database:     http://localhost:5432
echo 🔧 pgAdmin:      http://localhost:8080
echo.
echo pgAdmin Login:
echo   Email:    admin@ssd.local
echo   Password: admin123
echo.
echo To stop the application:
echo   docker-compose -f docker-compose.dev.yml down
echo.
echo To view logs:
echo   docker-compose -f docker-compose.dev.yml logs -f
echo ========================================
echo.
pause
