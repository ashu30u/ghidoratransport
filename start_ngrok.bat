@echo off
echo Starting Django Server and ngrok tunnel...
cd /d "C:\Users\dmtam\OneDrive\Desktop\GhidoraTransportProject"

if exist ".venv\Scripts\python.exe" (
    set "PY_CMD=.venv\Scripts\python.exe"
) else (
    set "PY_CMD=python"
)

echo Fixing Google SocialApp duplicates...
%PY_CMD% fix_google_socialapp.py

echo Launching Django server on port 8000 in a new window...
start "Django Server" cmd /k "cd /d C:\Users\dmtam\OneDrive\Desktop\GhidoraTransportProject && %PY_CMD% manage.py runserver 127.0.0.1:8000"

timeout /t 4 /nobreak >nul

echo Launching ngrok tunnel for jester-clang-steadfast.ngrok-free.dev...
start "ngrok Tunnel" cmd /k "ngrok http --domain=jester-clang-steadfast.ngrok-free.dev 127.0.0.1:8000"

echo Done! Django and ngrok are running in separate windows.
echo Public URL: https://jester-clang-steadfast.ngrok-free.dev
