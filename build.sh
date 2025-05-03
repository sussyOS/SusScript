#!/bin/bash

mkdir -p dist
osbuild="$1"
clear

if [ "$osbuild" = "W" ]; then
    nuitka --mode="onefile" --no-deployment-flag=self-execution --output-dir=dist sussy.py
    nuitka --mode="onefile" --output-dir=dist vent.py
    cp -f dist/sussy.exe "/mnt/c/Users/George/Documents/sus/bin/sussy.exe"
    cp -f dist/vent.exe "/mnt/c/Users/George/Documents/sus/bin/vent.exe"
    rm -rf dist
elif [ "$osbuild" = "M" ]; then
    exit 0
elif [ "$osbuild" = "L" ]; then
    exit 0
else
    echo "Invalid OS build option. Please choose W, M, or L."
    exit 1
fi

echo "Build complete."
