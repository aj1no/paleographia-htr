@echo off
rem Editor de folios novos com sugestoes do PP-OCRv6 (configs/editor_folios.toml).
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Instale primeiro: py -3.12 -m venv .venv e .venv\Scripts\python.exe -m pip install -e ".[test]"
  exit /b 1
)
docker info >nul 2>&1
if errorlevel 1 (
  echo [aviso] Docker Desktop nao esta em execucao. Abra o Docker Desktop para receber sugestoes.
  echo         A revisao manual continua disponivel.
) else (
  docker image inspect paleographia-kraken:7.1.0-cpu >nul 2>&1
  if errorlevel 1 echo [aviso] Imagem paleographia-kraken:7.1.0-cpu ausente. Veja runtime\kraken_ppocrv6\README.md
)
if not exist "models\ppocrv6_ajustado_D1_20261110\medium_ajustado_D1.safetensors" echo [aviso] Peso do modelo D1 ausente. Baixe do Release do GitHub: veja o README, secao Sugestoes do modelo.
echo Abrindo http://127.0.0.1:8010/ ...
start "" "http://127.0.0.1:8010/"
.venv\Scripts\python.exe -m paleographia serve --config configs/editor_folios.toml --host 127.0.0.1 --port 8010
