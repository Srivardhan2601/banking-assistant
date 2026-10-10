@echo off
title AI Banking Support - Live Server
echo ===================================================
echo Starting AI Banking Support Server on Port 8000...
echo Open your browser at: http://127.0.0.1:8000/
echo ===================================================
py -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
