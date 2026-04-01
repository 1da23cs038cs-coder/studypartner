# run.ps1 - Study Partner launcher (PowerShell)
# Right-click → Run with PowerShell

Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  Study Partner - Starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "  URL: http://localhost:8501" -ForegroundColor Green
Write-Host "  Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

try {
    # Run streamlit and wait
    $proc = Start-Process -FilePath "streamlit" -ArgumentList "run app.py" -NoNewWindow -PassThru
    $proc.WaitForExit()
} catch {
    # Try with python -m if streamlit command not found
    $proc = Start-Process -FilePath "python" -ArgumentList "-m streamlit run app.py" -NoNewWindow -PassThru
    $proc.WaitForExit()
} finally {
    Write-Host ""
    Write-Host "  Stopping server..." -ForegroundColor Yellow

    # Kill anything on port 8501
    $port = netstat -ano | Select-String ":8501" | Select-String "LISTENING"
    if ($port) {
        $pid_num = ($port -split "\s+")[-1]
        Stop-Process -Id $pid_num -Force -ErrorAction SilentlyContinue
    }

    # Kill python and streamlit processes
    Get-Process -Name "python"   -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "python3"  -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "streamlit"-ErrorAction SilentlyContinue | Stop-Process -Force

    Write-Host "  Server stopped." -ForegroundColor Green
    Start-Sleep -Seconds 2
}
