@echo off
rem Demonstracao da apresentacao (copia; dados oficiais intocados).
rem Abre a aplicacao na porta 8018 e, se existir tools\cloudflared.exe, um link publico temporario.
cd /d "%~dp0"
if not exist "configs\demo_apresentacao.toml" (
  echo Monte a demonstracao antes: .venv\Scripts\python.exe scripts\demo_apresentacao.py montar --de PASTA_DO_WORKSPACE --config CONFIG
  exit /b 1
)
start "PaleographIA - demonstracao" .venv\Scripts\python.exe -m paleographia serve --config configs/demo_apresentacao.toml --host 127.0.0.1 --port 8018
timeout /t 4 >nul
start "" "http://127.0.0.1:8018/leitura"
if exist "tools\cloudflared.exe" (
  echo.
  echo Link publico: procure abaixo a linha com "trycloudflare.com" e acrescente /leitura no fim.
  echo Feche esta janela para desligar o link.
  echo.
  tools\cloudflared.exe tunnel --no-autoupdate --url http://127.0.0.1:8018
)
