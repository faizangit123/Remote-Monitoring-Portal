@echo off
REM ============================================================
REM  Build script for Remote Monitoring Agent
REM  Double-click this file OR run it in terminal to build .exe
REM ============================================================

echo ============================================================
echo   Building Remote Monitoring Agent .exe
echo ============================================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/upgrade PyInstaller
pip install pyinstaller --quiet

REM Clean previous builds
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "agent.spec" del agent.spec

echo Building .exe with PyInstaller...
echo.

REM PyInstaller command explained:
REM --onefile      = bundle everything into ONE .exe file
REM --noconsole    = hide the black console window when .exe runs
REM                  (remove this line if you want to see the console)
REM --name         = name of the output .exe file
REM --icon         = icon for the .exe (optional)
REM --add-data     = include extra files in the bundle
REM --hidden-import= include Python modules PyInstaller might miss

pyinstaller ^
    --onefile ^
    --name "RemoteMonitoringAgent" ^
    --hidden-import=psutil ^
    --hidden-import=websockets ^
    --hidden-import=websockets.legacy ^
    --hidden-import=websockets.legacy.client ^
    --hidden-import=websockets.legacy.server ^
    --hidden-import=dotenv ^
    --hidden-import=wmi ^
    --hidden-import=winreg ^
    main.py

echo.
if exist "dist\RemoteMonitoringAgent.exe" (
    echo ============================================================
    echo   SUCCESS! .exe created at:
    echo   dist\RemoteMonitoringAgent.exe
    echo ============================================================
    echo.
    echo   Copy this file to the target Windows machine.
    echo   Make sure to also create a .env file with:
    echo     AGENT_ID=your-agent-id
    echo     AGENT_TOKEN=your-agent-token
    echo     SERVER_HOST=your-server-ip
    echo ============================================================
) else (
    echo ============================================================
    echo   BUILD FAILED! Check the output above for errors.
    echo ============================================================
)

pause