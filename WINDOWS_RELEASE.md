# Windows Release Guide

Is project ka simple installer file version ke sath banta hai, for example `BankStatementExtractorSetup-1.0.0.exe`. End user ko sirf is file ko run karna hoga, aur program us ke Windows computer mein install ho jayega.

## End User Ke Liye

User ko ye file dein:

- `BankStatementExtractorSetup-1.0.0.exe`

User steps:

1. `BankStatementExtractorSetup-1.0.0.exe` par double-click kare
2. `Next` dabaye
3. `Install` kare
4. Program Start Menu ya Desktop shortcut se open kare

## Aap Ke Liye Build Karne Ka Simple Tareeqa

Ye installer **Windows machine** par build hoga. Linux-built files use na karein.

Required:

- Python 3 for Windows
- Inno Setup 6

Project folder mein ye file run karein:

```bat
build_windows_installer.bat
```

Ye script automatically:

1. Virtual environment banayegi
2. Dependencies install karegi
3. PyInstaller build banayegi
4. `version.py` se version read karegi
5. Final setup file generate karegi

Final output:

- `BankStatementExtractorSetup-1.0.0.exe`

## Version Change Karna

Nayi release ke liye sirf [version.py](/home/infiniti/Projects/Pdf_extrector/version.py:1) mein:

- `APP_VERSION = "1.0.0"`

ko update karein, phir `build_windows_installer.bat` dobara run karein.

## Manual Build

Agar kabhi manually banana ho:

```powershell
py -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm StatmentExtractor.spec
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_config.iss
```
