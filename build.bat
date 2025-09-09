@echo off
echo Building ErogeRichPresence with Nuitka...

nuitka --onefile --windows-console-mode=disable --windows-icon-from-ico=assets/icon.ico --output-filename=ErogeRichPresence.exe --include-data-dir=assets=assets --include-data-file=config.json=config.json ErogeRichPresence.pyw

if %errorlevel% == 0 (
    echo Build successful! ErogeRichPresence.exe created.
    echo Don't forget to copy assets folder to the same directory as the exe!
) else (
    echo Build failed!
)

pause
