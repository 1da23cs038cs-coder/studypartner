@echo off
echo Stopping Study Partner server...

:: Kill by port 8501
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501" ^| findstr "LISTENING"') do (
    echo Killing process on port 8501 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)

:: Kill streamlit and python
taskkill /F /IM streamlit.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python3.exe >nul 2>&1

echo Done. Server stopped.
timeout /t 2 >nul
