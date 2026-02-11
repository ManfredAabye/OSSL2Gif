@echo off
REM Erstellt eine eigenständige EXE aus PyOSSL2Gif/main.py mit allen Abhängigkeiten
REM Voraussetzung: Python, pip und pyinstaller müssen installiert sein

REM Virtuelle Umgebung aktivieren (falls vorhanden)
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM PyInstaller installieren, falls nicht vorhanden
pip show pyinstaller >nul 2>&1
if errorlevel 1 pip install pyinstaller

REM EXE bauen (onefile, ohne Konsole, Icon optional)
pyinstaller --noconfirm --onefile --windowed --name OSSL2Gif PyOSSL2Gif\main.py

REM Hinweis für den Nutzer
if exist dist\OSSL2Gif.exe (
    echo.
    echo Fertig! Die EXE befindet sich in dist\OSSL2Gif.exe
) else (
    echo Fehler beim Erstellen der EXE!
)

pause
