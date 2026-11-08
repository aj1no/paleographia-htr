# Tira prints da janela do treino ("PaleographIA do zero - treino") a cada N minutos enquanto a
# trava runs\.treinando existir, e um print final. Usa PrintWindow: não rouba o foco e só
# fotografa essa janela. Se a janela estiver minimizada, pula.
param([int]$Minutos = 10, [int]$EsperaInicio = 5)

$raiz = $PSScriptRoot
$pasta = Join-Path $raiz "prints"
New-Item -ItemType Directory -Force $pasta | Out-Null
$trava = Join-Path $raiz "runs\.treinando"

Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class JanelaPrintZero {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
}
"@
[JanelaPrintZero]::SetProcessDPIAware() | Out-Null

function Print([string]$Sufixo) {
  $p = Get-Process | Where-Object { $_.MainWindowTitle -like "PaleographIA do zero*" } | Select-Object -First 1
  if (-not $p) { return }
  $h = $p.MainWindowHandle
  if ([JanelaPrintZero]::IsIconic($h)) { return }
  $r = New-Object JanelaPrintZero+RECT
  [JanelaPrintZero]::GetWindowRect($h, [ref]$r) | Out-Null
  if ($r.R -le $r.L) { return }
  $bmp = New-Object System.Drawing.Bitmap ($r.R - $r.L), ($r.B - $r.T)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $dc = $g.GetHdc()
  [JanelaPrintZero]::PrintWindow($h, $dc, 2) | Out-Null
  $g.ReleaseHdc($dc)
  $bmp.Save((Join-Path $pasta ("treino_{0}{1}.png" -f (Get-Date -Format "MMdd_HHmm"), $Sufixo)), [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
}

$limite = (Get-Date).AddMinutes($EsperaInicio)
while (-not (Test-Path $trava) -and (Get-Date) -lt $limite) { Start-Sleep -Seconds 10 }
while (Test-Path $trava) {
  Print ""
  $fim = (Get-Date).AddMinutes($Minutos)
  while ((Get-Date) -lt $fim -and (Test-Path $trava)) { Start-Sleep -Seconds 20 }
}
Start-Sleep -Seconds 10
Print "_final"
