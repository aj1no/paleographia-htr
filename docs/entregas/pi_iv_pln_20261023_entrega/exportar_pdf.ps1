param(
    [string]$Documento = (Join-Path $PSScriptRoot 'artigo.docx'),
    [string]$Pdf = (Join-Path $PSScriptRoot 'artigo.pdf')
)
$ErrorActionPreference = 'Stop'
$taskDocPath = (Resolve-Path -LiteralPath $Documento).Path
$taskPdfPath = [System.IO.Path]::GetFullPath($Pdf)
if ($taskDocPath -eq $taskPdfPath) { throw 'A origem e a saída devem ser distintas.' }
$taskWord = $null
$taskDocument = $null
try {
    # Instância dedicada, invisível, com documento aberto somente para leitura.
    $taskWord = New-Object -ComObject Word.Application
    $taskWord.Visible = $false
    $taskWord.DisplayAlerts = 0
    $taskWord.AutomationSecurity = 3
    $taskDocument = $taskWord.Documents.Open($taskDocPath, $false, $true, $false)
    $taskDocument.Repaginate()
    $taskDocument.ExportAsFixedFormat($taskPdfPath, 17)
    [PSCustomObject]@{
        pdf = $taskPdfPath
        pages = $taskDocument.ComputeStatistics(2)
        renderer = 'Microsoft Word ' + $taskWord.Version
        source_opened_read_only = $true
    } | ConvertTo-Json
}
finally {
    if ($null -ne $taskDocument) {
        $taskDocument.Close(0)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($taskDocument)
    }
    if ($null -ne $taskWord) {
        $taskWord.Quit(0)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($taskWord)
    }
}
