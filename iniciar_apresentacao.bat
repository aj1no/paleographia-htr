@echo off
rem Prepara tudo para a apresentacao com um clique: aplicacao (porta 8018), slides e a pasta
rem "PaleographIA - apresentacao" da Area de Trabalho, com o folio de demonstracao.
rem A janela do servidor fica minimizada e aberta; se algo falhar, ela mostra o erro.
chcp 65001 >nul
cd /d "%~dp0"
title PaleographIA - preparando a apresentacao
echo.
echo  PaleographIA - preparando a apresentacao...
echo.

call :responde
if errorlevel 1 (
  echo  Deixando a demonstracao no estado guardado: o folio de demonstracao sai da lista...
  .venv\Scripts\python.exe scripts\demo_apresentacao.py restaurar
  echo  Abrindo a aplicacao...
  start "PaleographIA - servidor (NAO FECHE)" /min cmd /k .venv\Scripts\python.exe -m paleographia serve --config configs/demo_apresentacao.toml --host 127.0.0.1 --port 8018
) else (
  echo  A aplicacao ja estava aberta.
)

powershell -NoProfile -Command "for ($i = 0; $i -lt 60; $i++) { try { Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8018/leitura' -TimeoutSec 2 | Out-Null; exit 0 } catch { Start-Sleep -Seconds 1 } }; exit 1"
if errorlevel 1 (
  echo.
  echo  A aplicacao nao respondeu em 60 segundos.
  echo  Abra a janela "PaleographIA - servidor" na barra de tarefas para ver o erro.
  pause
  exit /b 1
)

start "" "http://127.0.0.1:8018/leitura"
if exist "outputs\PaleographIA_Apresentacao_atualizada.pptx" start "" "outputs\PaleographIA_Apresentacao_atualizada.pptx"
powershell -NoProfile -Command "$p = Join-Path ([Environment]::GetFolderPath('Desktop')) ('PaleographIA - apresenta' + [char]0x00E7 + [char]0x00E3 + 'o'); if (Test-Path $p) { Start-Process explorer.exe $p }"

echo.
echo  Pronto: aplicacao em http://127.0.0.1:8018/leitura, slides e a pasta com o folio de demonstracao.
echo  Para encerrar, feche a janela "PaleographIA - servidor (NAO FECHE)" na barra de tarefas.
timeout /t 8 >nul
exit /b 0

:responde
powershell -NoProfile -Command "try { Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8018/leitura' -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }"
exit /b %errorlevel%
