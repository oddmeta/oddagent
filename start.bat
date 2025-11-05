@echo off

:: Set UTF-8 encoding
chcp 65001 >nul

:: Check Python virtual environment
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    if not exist "venv" (
        echo Python virtual environment creation failed.
        exit /b 1
    )
)
else (
    echo Python virtual environment found.
)

:: Activate virtual environment
echo Activating Python virtual environment...
call venv\Scripts\activate

:: Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

:: Start the service
echo Starting backend service (port 5050)...
python app.py

:: Prevent window from closing (optional, uncomment if needed)
:: pause