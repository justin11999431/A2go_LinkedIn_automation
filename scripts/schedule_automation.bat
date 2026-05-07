@echo off
echo ========================================
echo Schedule LinkedIn Outreach Automation
echo ========================================
echo.
echo This will schedule the automation to run daily at 8:00 AM
echo.

cd /d "%~dp0"

echo Creating Windows Task Scheduler task...
schtasks /create /tn "A2go LinkedIn Outreach Automation" /tr "%~dp0run_automation.bat" /sc daily /st 08:00 /f

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Task scheduled successfully!
    echo ========================================
    echo.
    echo Task Name: A2go LinkedIn Outreach Automation
    echo Schedule: Daily at 8:00 AM
    echo Action: Run run_automation.bat
    echo.
    echo The automation will now run automatically every day at 8:00 AM.
    echo.
    echo To run the automation manually, run: run_automation.bat
    echo.
    echo To view the task, open Task Scheduler and look for "A2go LinkedIn Outreach Automation"
    echo.
) else (
    echo.
    echo ========================================
    echo Failed to schedule task. Error code: %errorlevel%
    echo ========================================
    echo.
    echo Please run this command as Administrator.
    echo.
)

pause
