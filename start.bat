@echo off
chcp 65001

REM check whether venv exists
if exist venv (
    echo activate venv...
    call venv\Scripts\activate
) else (
    echo Python venv does not exist, use system Python...
)

REM install project dependencies if requirements.txt exists
if exist oddagent/requirements.txt (
    echo install project dependencies...
    pip install -r oddagent/requirements.txt
)

REM start flask app
echo start xiaoluo service...
python3 -m oddagent.app

pause