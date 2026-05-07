@echo off
echo ========================================
echo LinkedIn Outreach Automation
echo ========================================
echo Starting automation at %date% %time%
echo.

cd /d "%~dp0"
python run_automation.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Automation completed successfully!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Automation failed with error code: %errorlevel%
    echo ========================================
)

echo.
echo Next run: Tomorrow at 8:00 AM
echo.
pause
