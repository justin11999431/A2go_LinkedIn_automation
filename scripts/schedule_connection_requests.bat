@echo off
echo Scheduling connection requests for tomorrow at 8:00am...
schtasks /create /tn "A2go Connection Requests" /tr "python %~dp0send_connection_requests.py" /sc once /st 08:00 /sd %date:~4,2%/%date:~7,2%/%date:~10,4% /f
if %errorlevel% equ 0 (
    echo Task scheduled successfully!
    echo The connection requests will be sent tomorrow at 8:00am.
) else (
    echo Failed to schedule task. Error code: %errorlevel%
)
pause
