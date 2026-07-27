$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location -Path $ScriptDir

Write-Host "[1/5] Starting Docker infrastructure (Kafka, Postgres)..."
docker compose up -d

Write-Host "[2/5] Starting Backend Agent in background..."
Start-Process -FilePath "powershell" -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "cd 'services\backend-agent'; python -m venv venv; .\venv\Scripts\activate; pip install -r requirements.txt -q; uvicorn main:app --host 0.0.0.0 --port 8000" -WindowStyle Minimized

Write-Host "[3/5] Starting Eligibility Gate in background..."
Start-Process -FilePath "powershell" -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "cd 'services\eligibility-gate'; python -m venv venv; .\venv\Scripts\activate; pip install -r requirements.txt -q; python gate.py" -WindowStyle Minimized

Write-Host "[4/5] Starting Disruption Detector in background..."
Start-Process -FilePath "powershell" -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "cd 'services\disruption-detector'; python -m venv venv; .\venv\Scripts\activate; pip install -r requirements.txt -q; python detector.py" -WindowStyle Minimized

Write-Host "[5/5] Starting React Frontend in background..."
Start-Process -FilePath "powershell" -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "cd frontend; npm install --silent; npm run dev" -WindowStyle Minimized