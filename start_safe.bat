@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Instale primeiro: py -3.12 -m venv .venv e .venv\Scripts\python.exe -m pip install -e ".[test]"
  exit /b 1
)
.venv\Scripts\python.exe -m paleographia serve --host 127.0.0.1 --port 8000
