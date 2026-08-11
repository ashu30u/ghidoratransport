@echo off
echo ========================================================
echo   GHIDORA TRANSPORT - ONE-CLICK AUTO START SERVER & NGROK
echo ========================================================
echo.
echo 1. Cleaning old ngrok processes...
taskkill /F /IM ngrok.exe >nul 2>&1

echo 2. Fixing Database Schema & Google Login...
.venv\Scripts\python.exe fix_google_duplicate_app.py >nul 2>&1
.venv\Scripts\python.exe auto_migrate_review_columns.py >nul 2>&1
.venv\Scripts\python.exe fix_review_null_constraint.py >nul 2>&1
.venv\Scripts\python.exe ensure_reviews_db.py >nul 2>&1
start "Ghidora Django Server" cmd /k "cd /d C:\Users\dmtam\OneDrive\Desktop\GhidoraTransportProject && .venv\Scripts\python.exe fix_google_duplicate_app.py && .venv\Scripts\python.exe auto_migrate_review_columns.py && .venv\Scripts\python.exe fix_review_null_constraint.py && .venv\Scripts\python.exe ensure_reviews_db.py && .venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000"

echo 3. Waiting 3 seconds for server to initialize...
timeout /t 3 /nobreak >nul

echo 4. Starting Ngrok Tunnel...
start "Ghidora Ngrok Tunnel" cmd /k "ngrok http 127.0.0.1:8000"

echo.
echo ========================================================
echo   SUCCESS! Both Server and Ngrok are now running!
echo   Open your ngrok link on your mobile phone!
echo ========================================================
pause
