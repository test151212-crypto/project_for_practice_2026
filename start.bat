@echo off
title Freelance Marketplace

call venv\Scripts\activate.bat

echo Starting Django server...
start "Django Server" cmd /k "python manage.py runserver"

echo Starting Celery worker (solo pool for Windows)...
start "Celery Worker" cmd /k "celery -A freelance worker --loglevel=info --pool=solo"

echo Starting Celery beat...
start "Celery Beat" cmd /k "celery -A freelance beat --loglevel=info"

echo All components started. Close windows to stop.
pause