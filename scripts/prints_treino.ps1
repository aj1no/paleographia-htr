# Tira prints do treino ao vivo enquanto o contêiner roda, para registrar a execução.
# Chamado por gravar_treino.bat; também pode rodar sozinho:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\prints_treino.ps1 -Modo A
# Captura só duas janelas, sem roubar o foco (PrintWindow): o terminal do treino
# ("PaleographIA - treino ao vivo") e o Docker Desktop. Nada além delas aparece nos prints.
param([string]$Modo = "A", [int]$Minutos = 10, [int]$EsperaInicio = 15)

$raiz = Split-Path -Parent $PSScriptRoot
$pasta = Join-Path $raiz ("output\prints_treino_{0}_{1}" -f $Modo, (Get-Date -Format "yyyyMMddTHHmmss"))
New-Item -ItemType Directory -Force $pasta | Out-Null

Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class JanelaPrint {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
}
"@
[JanelaPrint]::SetProcessDPIAware() | Out-Null

function Print([string]$Titulo, [string]$Nome) {
  $p = Get-Process | Where-Object { $_.MainWindowTitle -like $Titulo } | Select-Object -First 1
  if (-not $p) { return }
  $h = $p.MainWindowHandle
  if ([JanelaPrint]::IsIconic($h)) { return }  # minimizada: não há o que fotografar
  $r = New-Object JanelaPrint+RECT
  [JanelaPrint]::GetWindowRect($h, [ref]$r) | Out-Null
  $bmp = New-Object System.Drawing.Bitmap ($r.R - $r.L), ($r.B - $r.T)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $dc = $g.GetHdc()
  [JanelaPrint]::PrintWindow($h, $dc, 2) | Out-Null  # 2 = PW_RENDERFULLCONTENT
  $g.ReleaseHdc($dc)
  $bmp.Save((Join-Path $pasta ("{0}_{1}.png" -f $Nome, (Get-Date -Format "HHmmss"))), [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
}
function Rodando { [bool](docker ps --filter name=paleographia-finetune --format "{{.Names}}") }
function Ambos([string]$Sufixo) {
  Print "PaleographIA - treino ao vivo" ("treino_{0}{1}" -f $Modo, $Sufixo)
  Print "*Docker Desktop" ("docker{0}" -f $Sufixo)
}

$limite = (Get-Date).AddMinutes($EsperaInicio)
while (-not (Rodando) -and (Get-Date) -lt $limite) { Start-Sleep -Seconds 10 }
while (Rodando) {
  Ambos ""
  $fim = (Get-Date).AddMinutes($Minutos)
  while ((Get-Date) -lt $fim -and (Rodando)) { Start-Sleep -Seconds 20 }
}
Start-Sleep -Seconds 15  # deixa o resumo final aparecer no terminal
Ambos "_final"
