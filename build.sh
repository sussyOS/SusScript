mkdir dist >> /dev/null
set osbuild=%1
clear
if [osbuild==W] 
    nuitka --mode="onefile" --no-deployment-flag=self-execution --output-dir=dist sussy.py
    nuitka --mode="onefile" --output-dir=dist vent.py
    copy /y dist\sussy.exe C:\Users\George\Documents\sus\bin\sussy.exe >> /dev/null
    copy /y dist\vent.exe C:\Users\George\Documents\sus\bin\vent.exe >> /dev/null
    rmdir /s /q dist
    clear
else if osbuild==M 
    exit
else if osbuild==L
    exit
else 
    echo Invalid OS build option. Please choose W, M, or L.
    exit /b 1
