Param(
    [string]$ApiKey = $env:OPENWEATHER_API_KEY
)

if (-not $ApiKey) {
    $ApiKey = Read-Host "Enter your OpenWeather API key"
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found on PATH. Install Python 3.8+ and re-run this script."
    exit 1
}

python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements.txt

Write-Host "Starting Flask app on http://localhost:5000"
$env:OPENWEATHER_API_KEY = $ApiKey
& .venv\Scripts\python backend\app.py
