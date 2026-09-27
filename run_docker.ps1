Param(
    [string]$ApiKey = $env:OPENWEATHER_API_KEY,
    [string]$NgrokToken = $env:NGROK_AUTHTOKEN
)

if (-not $ApiKey) {
    $ApiKey = Read-Host "Enter your OpenWeather API key"
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker not found on PATH. Install Docker Desktop and re-run this script."
    exit 1
}

$env:OPENWEATHER_API_KEY = $ApiKey
if ($NgrokToken) { $env:NGROK_AUTHTOKEN = $NgrokToken }

Write-Host "Building and starting services (this will stream logs)..."
docker compose up --build
