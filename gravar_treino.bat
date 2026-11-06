@echo off
rem Grava um treino de verdade (A ou B), um por vez.
chcp 65001 >nul
cd /d "%~dp0"
title PaleographIA - treino ao vivo
if not exist ".venv\Scripts\python.exe" (
  echo Instale primeiro: py -3.12 -m venv .venv e .venv\Scripts\python.exe -m pip install -e ".[test]"
  pause
  exit /b 1
)
docker info >nul 2>&1
if errorlevel 1 (
  echo Abra o Docker Desktop e rode este atalho de novo.
  pause
  exit /b 1
)
echo.
echo  PaleographIA - ajuste fino do PP-OCRv6
echo.
echo    A = so Traslado (191 linhas; cerca de 2h20 na GTX 1650)
echo    B = Traslado + 550 linhas publicas da Inquisicao (cerca de 1h30 por epoca; varias horas)
echo.
choice /c AB /n /m "  Qual treino gravar? [A/B] "
if errorlevel 2 (set MODO=B) else (set MODO=A)
where nvidia-smi >nul 2>&1 && start "GPU - nvidia-smi" cmd /k nvidia-smi -l 3
echo.
echo  Treino %MODO% escolhido. Uma janela ao lado mostra o uso da GPU (nao e o treino).
echo  Prints automaticos do terminal e do Docker a cada 10 min: output\prints_treino_%MODO%_*
echo.
echo  O TREINO AINDA NAO COMECOU.
echo  Comece a gravar a tela (Win+Shift+R ou Win+Alt+R), volte a ESTA janela
echo  e aperte qualquer tecla para COMECAR o treino.
pause >nul
cls
start "" /min powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File scripts\prints_treino.ps1 -Modo %MODO%
.venv\Scripts\python.exe scripts\treinar_ao_vivo.py %MODO%
echo.
echo  Saidas: pasta output\treino_ao_vivo_%MODO%_* (console.log, validacoes e peso exportado).
pause
