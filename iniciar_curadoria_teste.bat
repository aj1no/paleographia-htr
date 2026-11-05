@echo off
rem Curadoria do grupo de TESTE reservado (pagamento a Thomas Pardo). Reconhecedor desligado.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Instale primeiro: py -3.12 -m venv .venv e .venv\Scripts\python.exe -m pip install -e ".[test]"
  exit /b 1
)
echo Curadoria do teste: sem sugestoes de modelo, por protocolo.
echo Abrindo http://127.0.0.1:8014/ ...
start "" "http://127.0.0.1:8014/"
.venv\Scripts\python.exe -m paleographia serve --config configs/curation_teste_pagamento.toml --host 127.0.0.1 --port 8014
