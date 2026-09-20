@echo off
title VAJRA Backend Engine
:loop
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
timeout /t 1 /nobreak >nul
goto loop
