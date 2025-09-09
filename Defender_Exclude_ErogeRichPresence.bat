@echo off
:: Check for administrator privileges
NET SESSION >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /B
)

:: Exclude 'ErogeRichPresence' folder in Windows Defender
echo Adding 'ErogeRichPresence' folder to Windows Defender exclusions...
powershell Add-MpPreference -ExclusionPath "C:\Users\%USERNAME%\AppData\Local\Programs\ErogeRichPresence"

:: Inform the user that the operation is complete
echo ErogeRichPresence folder successfully added to Windows Defender exclusions.
pause
