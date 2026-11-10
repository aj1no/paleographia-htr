@echo off
rem Curadoria assistida dos folios novos para treino (Posturas 1831, carta 1767, contrato do livro 13).
rem O ajustado B sugere; a equipe corrige e valida no modo leitura.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Instale primeiro: py -3.12 -m venv .venv e .venv\Scripts\python.exe -m pip install -e ".[test]"
  exit /b 1
)
echo Abrindo http://127.0.0.1:8020/leitura ...
start "" "http://127.0.0.1:8020/leitura"
.venv\Scripts\python.exe -m paleographia serve --config configs/novos_folios.toml --host 127.0.0.1 --port 8020
