@echo off
title Haq Saathi - Voice Legal Companion
echo ========================================================
echo       HAQ SAATHI (హక్ సాథీ • हक़ साथी • حق ساتھی)
echo  Voice Legal Rights Companion for Informal Workers
echo ========================================================
echo.
echo [1/2] Verifying Python and dependencies...
py -m pip install -r requirements.txt --quiet
echo [2/2] Starting Haq Saathi Server on http://127.0.0.1:8000 ...
echo.
echo Open your browser at: http://127.0.0.1:8000
echo Press Ctrl+C to terminate the server.
echo ========================================================
py -m uvicorn haq_saathi.backend.main:app --host 127.0.0.1 --port 8000 --reload
