<#
.SYNOPSIS
Triggers a mock flight cancellation event.
#>

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location -Path "$ScriptDir\services\event-producer"

Write-Host "Triggering mock flight cancellation (AX100)..." -ForegroundColor Cyan
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt -q
python producer.py
