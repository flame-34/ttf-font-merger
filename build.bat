@echo off
REM Build a standalone TtfMergeTool.exe (single file, no browser needed).
REM Prereq: pywebview + pyinstaller + fontTools installed in .\libs\
setlocal
cd /d "%~dp0"
set "PYTHONNOUSERSITE=1"
set "PYTHONPATH=%~dp0libs"
python -m PyInstaller --noconfirm --onefile --windowed --name TtfMergeTool ^
  --paths libs ^
  --collect-all fontTools --collect-all webview --collect-all pythonnet --collect-all clr_loader ^
  --icon app.ico ^
  --add-data "static;static" ^
  desktop.py
if errorlevel 1 (
  echo.
  echo Build FAILED.
  exit /b 1
)
echo.
echo Build OK: %~dp0dist\TtfMergeTool.exe
endlocal
