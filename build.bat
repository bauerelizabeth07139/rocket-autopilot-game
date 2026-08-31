@echo off
rem Build Rocket Autopilot into a single Windows exe.
python tools\make_icon.py
pyinstaller --onefile --windowed --name RocketAutopilot --icon asset\rocket.ico main.py
echo.
echo Built: dist\RocketAutopilot.exe
echo Verifying with self-tests...
dist\RocketAutopilot.exe --selftest
