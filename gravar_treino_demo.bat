@echo off
rem Treino de demonstracao para gravar em video (cerca de 6 min na GTX 1650).
chcp 65001 >nul
cd /d "%~dp0"
title PaleographIA - treino ao vivo (demonstracao)
if not exist ".venv\Scripts\python.exe" (
  echo Instale primeiro: py -3.12 -m venv .venv e .venv\Scripts\python.exe -m pip install -e ".[test]"
  pause
  exit /b 1
)
docker info >/dev/null 2>&1
if errorlevel 1 (
  echo Abra o Docker Desktop e rode este atalho de novo.
  pause
  exit /b 1
)
where nvidia-smi >/dev/null 2>&1 && start "GPU - nvidia-smi" cmd /k nvidia-smi -l 3
echo.
echo  PaleographIA - ajuste fino do PP-OCRv6 (demonstracao)
echo  40 linhas do Traslado para treino, 7 linhas humanas de 1795 para validacao, 1 epoca.
echo  Uma janela ao lado mostra o uso da GPU.
echo.
echo  Comece a gravar a tela (Win+Shift+R ou Win+Alt+R) e depois aperte uma tecla.
pause >nul
cls
.venv\Scripts\python.exe scripts\treinar_ao_vivo.py demo
echo.
echo  Saidas: pasta output\treino_ao_vivo_demo_* (console.log, validacoes e peso exportado).
pause
