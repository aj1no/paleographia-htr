@echo off
rem Desde 10/11 os folios novos (Posturas 1831, carta 1767, contrato do livro 13) ficam na aplicacao
rem oficial, a da apresentacao. Este atalho abre a mesma aplicacao de iniciar_demo.bat, sem link publico.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Instale primeiro: py -3.12 -m venv .venv e .venv\Scripts\python.exe -m pip install -e ".[test]"
  exit /b 1
)
echo Abrindo http://127.0.0.1:8018/leitura ...
start "" "http://127.0.0.1:8018/leitura"
.venv\Scripts\python.exe -m paleographia serve --config configs/demo_apresentacao.toml --host 127.0.0.1 --port 8018
