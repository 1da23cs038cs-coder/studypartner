@echo off
title Study Partner

echo.
echo  ==========================================
echo   Study Partner - Starting Server...
echo  ==========================================
echo.
echo  Open your browser at: http://localhost:8501
echo  Press CTRL+C or close this window to stop.
echo.

:: Start streamlit
streamlit run app.py

:cleanup
echo.
echo  Stopping server...
:: Kill all python processes using port 8501
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
:: Also kill any remaining streamlit/python
taskkill /F /IM streamlit.exe >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Study Partner" /IM python.exe >nul 2>&1
echo  Server stopped. You can close this window.
echo.
pause
