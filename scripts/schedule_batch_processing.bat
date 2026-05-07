@echo off
echo ========================================
echo Schedule LinkedIn Outreach Batch Processing
echo ========================================
echo.
echo This will schedule the batch processing to run daily at 9:00 AM
echo.

cd /d "%~dp0"

echo Creating Windows Task Scheduler task...
schtasks /create /tn "A2go LinkedIn Outreach Batch Processing" /tr "%~dp0batch_processing.py" /sc daily /st 09:00 /f

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Task scheduled successfully!
    echo ========================================
    echo.
    echo Task Name: A2go LinkedIn Outreach Batch Processing
    echo Schedule: Daily at 9:00 AM
    echo Action: Run batch_processing.py
    echo.
    echo The batch processing will now run automatically every day at 9:00 AM.
    echo.
echo Features:
echo - Processes up to 20 new leads per day
echo - Adjusts quota based on follow-up messages needed
echo - Sends follow-up messages based on timing
- Checks for human responses and stops automation
- Updates workflow sheet with all actions
echo - Preserves messaging sequences for all leads
    echo.
    echo To run the batch processing manually, run: batch_processing.py
    echo.
    echo To view the task, open Task Scheduler and look for "A2go LinkedIn Outreach Batch Processing"
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
