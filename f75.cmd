@echo off
set PYTHONIOENCODING=utf-8
set PYTHONPATH=%~dp0
"%~dp0.venv\Scripts\python.exe" -m f75 %*
