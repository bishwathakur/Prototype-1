<#
.SYNOPSIS
Starts all AXIS Prototype services.
#>

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location -Path $ScriptDir

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Starting AXIS Travel Disruption Prototype" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

Write-Host "[1/4] Starting Docker infrastructure (Kafka, Postgres)..."
docker compose up -d

Write-Host "[2/4] Starting Backend Agent in background..."
Start-Process -FilePath "powershell" -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "cd 'services\backend-agent'; python -m venv venv; .\venv\Scripts\activate; pip install -r requirements.txt -q; uvicorn main:app --host 0.0.0.0 --port 8000" -WindowStyle Minimized

Write-Host "[3/4] Starting Disruption Detector in background..."
Start-Process -FilePath "powershell" -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "cd 'services\disruption-detector'; python -m venv venv; .\venv\Scripts\activate; pip install -r requirements.txt -q; python detector.py" -WindowStyle Minimized

Write-Host "[4/4] Starting React Frontend in background..."
Start-Process -FilePath "powershell" -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "cd frontend; npm install --silent; npm run dev" -WindowStyle Minimized

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "✅ All services are starting up!" -ForegroundColor Green
Write-Host "React UI will be available at: http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "👉 To trigger a disruption, run in this terminal:" -ForegroundColor Yellow
Write-Host "   .\trigger_disruption.ps1" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Green
