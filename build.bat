@echo off
@mkdir dist >> nul
@set osbuild=%1
@cls
if %osbuild%==W (
    @nuitka --mode="onefile" --no-deployment-flag=self-execution --output-dir=dist sussy.py
    @nuitka --mode="onefile" --output-dir=dist vent.py
    @copy /y dist\sussy.exe C:\Users\George\Documents\sus\bin\sussy.exe >> nul 
    @copy /y dist\vent.exe C:\Users\George\Documents\sus\bin\vent.exe >> nul
    @rmdir /s /q dist
) else if %osbuild%==M (
    exit
) else if %osbuild%==L (
    @nuitka --mode="onefile" --no-deployment-flag=self-execution --output-dir=dist sussy.py
    @nuitka --mode="onefile" --output-dir=dist vent.py
    @copy /y dist\sussy.exe C:\Users\George\Documents\sus\bin\sussy.exe >> nul 
    @copy /y dist\vent.exe C:\Users\George\Documents\sus\bin\vent.exe >> nul
    @rmdir /s /q dist
) else (
    @echo Invalid OS build option. Please choose W, M, or L.
    exit /b 1
)
@echo Build complete.
