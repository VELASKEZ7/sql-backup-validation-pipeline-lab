$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$sqlFile = Join-Path $root "data\change.sql"
$snapshot = Join-Path $root "data\mock_db_snapshot.json"
$outputDir = Join-Path $root "out"
$entrypoint = Join-Path $root "src\sql_pipeline.py"

python $entrypoint --sql $sqlFile --snapshot $snapshot --output-dir $outputDir

Write-Host "Pipeline ejecutado. Ver salida en: $outputDir"
