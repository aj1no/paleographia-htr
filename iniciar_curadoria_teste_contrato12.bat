@echo off
rem Curadoria do grupo de TESTE reservado (contrato do livro 12, 1763). Reconhecedor desligado.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Instale primeiro: py -3.12 -m venv .venv e .venv\Scripts\python.exe -m pip install -e ".[test]"
  exit /b 1
)
echo Curadoria do teste: sem sugestoes de modelo, por protocolo.
echo Abrindo http://127.0.0.1:8017/ ...
start "" "http://127.0.0.1:8017/"
.venv\Scripts\python.exe -m paleographia serve --config configs/curation_teste_contrato12.toml --host 127.0.0.1 --port 8017
