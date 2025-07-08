@echo off
echo [*] Stopping client processes...
taskkill /f /im python.exe /t >nul 2>&1
echo [*] Removing temporary files...
del /q "C:\Windows\Temp\edu_client_*" >nul 2>&1
echo [*] Uninstallation complete
echo [!] Manual cleanup may be required for any scheduled tasks
pause
