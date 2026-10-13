@echo off
title Ghidora Transport Auto Launcher
echo ========================================================
echo   GHIDORA TRANSPORT - AUTO START SERVER & NGROK
echo ========================================================
echo.

cd /d "C:\Users\dmtam\OneDrive\Desktop\GhidoraTransportProject"

echo 1. Stopping existing ngrok...
taskkill /F /IM ngrok.exe >nul 2>&1

echo 2. Detecting Python environment...
if exist ".venv\Scripts\python.exe" (
    set "PY_CMD=.venv\Scripts\python.exe"
) else (
    set "PY_CMD=python"
)

echo 3. Starting Django Server on 127.0.0.1:8000...
start "Ghidora Django Server" cmd /k "cd /d C:\Users\dmtam\OneDrive\Desktop\GhidoraTransportProject && %PY_CMD% manage.py runserver 127.0.0.1:8000"

echo 4. Waiting 4 seconds for server to start...
timeout /t 4 /nobreak >nul

echo 5. Starting Ngrok Tunnel...
start "Ghidora Ngrok Tunnel" cmd /k "ngrok http --domain=jester-clang-steadfast.ngrok-free.dev 127.0.0.1:8000"

echo.
echo ========================================================
echo   Done! Check the "Ghidora Django Server" window to ensure
echo   Django started cleanly without errors.
echo ========================================================
pause
