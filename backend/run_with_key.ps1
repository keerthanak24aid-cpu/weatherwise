param([string]$Key)

Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
$env:OPENWEATHER_API_KEY = $Key
Write-Host "Starting backend\app.py with OPENWEATHER_API_KEY set to: $Key"
& .\.venv\Scripts\python backend\app.py
