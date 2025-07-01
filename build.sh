#!/bin/bash

osbuild=$1

mkdir -p dist
clear

if [ "$osbuild" = "W" ]; then
    nuitka --mode=onefile --no-deployment-flag=self-execution --output-dir=dist sussy.py
    nuitka --mode=onefile --output-dir=dist vent.py
    cp -f dist/sussy.exe ~/Documents/sus/bin/sussy.exe
    cp -f dist/vent.exe ~/Documents/sus/bin/vent.exe
    rm -rf dist
elif [ "$osbuild" = "M" ]; then
    exit 0
elif [ "$osbuild" = "L" ]; then
    nuitka --mode=onefile --output-filename=sussy --no-deployment-flag=self-execution --output-dir=dist sussy.py
    nuitka --mode=onefile --output-filename=vent --output-dir=dist vent.py
    cp -f dist/sussy ~/Documents/sus/bin/sussy
    cp -f dist/vent ~/Documents/sus/bin/vent
    rm -rf dist
else
    echo "Invalid OS build option. Please choose W, M, or L."
    exit 1
fi

echo "Build complete."
