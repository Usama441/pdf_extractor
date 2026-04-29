@echo off
setlocal

cd /d "%~dp0"

echo ==========================================
echo Building Bank Statement Extractor Installer
echo ==========================================
echo.

where py >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python launcher 'py' not found. Install Python 3 for Windows first.
  exit /b 1
)

set "ISCC_PATH=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC_PATH%" set "ISCC_PATH=%ProgramFiles%\Inno Setup 6\ISCC.exe"

if not exist "%ISCC_PATH%" (
  where ISCC >nul 2>nul
  if errorlevel 1 (
    echo [ERROR] Inno Setup Compiler not found.
    echo Install Inno Setup 6 from https://jrsoftware.org/isinfo.php
    exit /b 1
  ) else (
    set "ISCC_PATH=ISCC"
  )
)

if not exist ".venv\Scripts\python.exe" (
  echo [INFO] Creating virtual environment...
  py -m venv .venv
  if errorlevel 1 exit /b 1
)

echo [INFO] Installing dependencies...
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if errorlevel 1 exit /b 1

python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

for /f "usebackq delims=" %%i in (`python -c "from version import APP_VERSION; print(APP_VERSION)"`) do set "APP_VERSION=%%i"

if "%APP_VERSION%"=="" (
  echo [ERROR] Could not read APP_VERSION from version.py
  exit /b 1
)

echo [INFO] Building Windows app bundle...
python -m PyInstaller --noconfirm StatmentExtractor.spec
if errorlevel 1 exit /b 1

echo [INFO] Building installer EXE...
"%ISCC_PATH%" /DAppVersion=%APP_VERSION% installer_config.iss
if errorlevel 1 exit /b 1

echo.
echo [SUCCESS] Installer created:
echo %cd%\BankStatementExtractorSetup-%APP_VERSION%.exe
echo.
echo End user only needs to run:
echo BankStatementExtractorSetup-%APP_VERSION%.exe
echo.

endlocal
