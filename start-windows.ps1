# PowerShell script to start Safe Companion Messaging Application with Docker Desktop
Write-Host "Starting Safe Companion Messaging Application Setup for Windows Docker Desktop" -ForegroundColor Green
Write-Host ""

# Check if Docker Desktop is running
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker is running: $dockerVersion" -ForegroundColor Green
    } else {
        throw "Docker command failed"
    }
} catch {
    Write-Host "❌ ERROR: Docker is not running or not installed." -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if docker-compose is available
try {
    $composeVersion = docker-compose --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker Compose is available: $composeVersion" -ForegroundColor Green
    } else {
        throw "Docker Compose command failed"
    }
} catch {
    Write-Host "❌ ERROR: docker-compose is not available." -ForegroundColor Red
    Write-Host "Please ensure Docker Desktop includes docker-compose." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Stop any existing containers
Write-Host "🔄 Stopping any existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml down

# Build and start the containers
Write-Host "🔄 Building and starting containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml up --build -d

# Wait for services to be ready
Write-Host "🔄 Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check if containers are running
Write-Host "🔍 Checking container status..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml ps

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Your application should now be running:" -ForegroundColor White
Write-Host "📱 Web App:       http://localhost:5000" -ForegroundColor Cyan
Write-Host "🗄️  Database:     http://localhost:5432" -ForegroundColor Cyan
Write-Host "🔧 pgAdmin:      http://localhost:8080" -ForegroundColor Cyan
Write-Host ""
Write-Host "pgAdmin Login:" -ForegroundColor White
Write-Host "   Email:    admin@ssd.local" -ForegroundColor Gray
Write-Host "   Password: admin123" -ForegroundColor Gray
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor White
Write-Host "   Stop:     docker-compose -f docker-compose.dev.yml down" -ForegroundColor Gray
Write-Host "   Logs:     docker-compose -f docker-compose.dev.yml logs -f" -ForegroundColor Gray
Write-Host "   Rebuild:  docker-compose -f docker-compose.dev.yml up --build" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Open the application in the default browser
Write-Host "🌐 Opening application in browser..." -ForegroundColor Yellow
Start-Process "http://localhost:5000"

Read-Host "Press Enter to exit"
