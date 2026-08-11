@echo off
echo ========================================================
echo Starting Ghidora Transport Server on http://127.0.0.1:8000/
echo ========================================================
start http://127.0.0.1:8000/
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
pause
