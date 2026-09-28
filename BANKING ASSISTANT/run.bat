@echo off
title AI Banking Support - Live Server
echo ========================================================
echo Starting AI Banking Support Server with Hindsight Cloud
echo ========================================================
echo.
py -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
