param([string]$Key)

$pids = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and $_.CommandLine -like '*backend\\app.py*' } | Select-Object -ExpandProperty ProcessId -ErrorAction SilentlyContinue
if ($pids) { $pids | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue } }

$env:OPENWEATHER_API_KEY = $Key
Write-Host "Starting backend\app.py with provided API key..."
Start-Process -FilePath ".\\.venv\\Scripts\\python" -ArgumentList "backend\\app.py" -NoNewWindow
