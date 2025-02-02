@echo off
echo Activating virtual environment...
call "venv\Scripts\activate.bat"

echo Running bot...
python -u "main.py"

pause
