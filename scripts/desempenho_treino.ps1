# Registra o desempenho do computador enquanto o treino roda, em CSV (uma linha a cada N segundos):
# GPU (uso, memória, potência, temperatura, estado), CPU e memória do Windows, e CPU/memória do
# contêiner de treino segundo o Docker. Termina sozinho quando o contêiner encerra.
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\desempenho_treino.ps1 -Modo B
param([string]$Modo = "A", [int]$Segundos = 30, [int]$EsperaInicio = 15)

$raiz = Split-Path -Parent $PSScriptRoot
$arquivo = Join-Path $raiz ("output\desempenho_treino_{0}_{1}.csv" -f $Modo, (Get-Date -Format "yyyyMMddTHHmmss"))
$cab = "horario,gpu_uso_pct,gpu_mem_mib,gpu_mem_total_mib,gpu_potencia_w,gpu_temp_c,gpu_estado," +
       "cpu_windows_pct,ram_usada_gb,ram_total_gb,conteiner_cpu_pct,conteiner_mem"
Set-Content -Path $arquivo -Value $cab -Encoding utf8

function Conteiner { docker ps --filter name=paleographia-finetune --format "{{.Names}}" | Select-Object -First 1 }
$limite = (Get-Date).AddMinutes($EsperaInicio)
while (-not (Conteiner) -and (Get-Date) -lt $limite) { Start-Sleep -Seconds 10 }

$os = Get-CimInstance Win32_OperatingSystem
$ramTotal = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
while ($nome = Conteiner) {
  $gpu = (nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu,pstate `
          --format=csv,noheader,nounits 2>$null) -replace "\s", ""
  if (-not $gpu) { $gpu = ",,,,," }
  $cpu = [math]::Round((Get-CimInstance Win32_Processor | Measure-Object LoadPercentage -Average).Average, 1)
  $livre = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB
  $ram = [math]::Round($ramTotal - $livre, 2)
  $st = (docker stats --no-stream --format "{{.CPUPerc}},{{.MemUsage}}" $nome 2>$null) -replace "%", "" -replace " / ", "/"
  if (-not $st) { $st = "," }
  $inv = [Globalization.CultureInfo]::InvariantCulture  # ponto decimal, para o CSV não quebrar
  $linha = [string]::Format($inv, "{0},{1},{2},{3},{4},{5}", (Get-Date -Format "yyyy-MM-ddTHH:mm:ss"), $gpu, $cpu, $ram, $ramTotal, $st)
  Add-Content -Path $arquivo -Value $linha -Encoding utf8
  Start-Sleep -Seconds $Segundos
}
