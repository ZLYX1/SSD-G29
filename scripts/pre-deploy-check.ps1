#!/usr/bin/env pwsh

Write-Host "🚀 Safe Companions Pre-Deployment Validation" -ForegroundColor Green
Write-Host "=" * 50

Write-Host "Running pre-deployment checks..." -ForegroundColor Yellow

& python scripts\pre-deploy-check.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Pre-deployment checks failed!" -ForegroundColor Red
    Write-Host "Please fix the issues before deploying to production." -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to continue"
    exit 1
} else {
    Write-Host ""
    Write-Host "✅ All checks passed! Ready for deployment." -ForegroundColor Green
    Write-Host ""
    Read-Host "Press Enter to continue"
    exit 0
}
