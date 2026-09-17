$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) { throw "No existe .venv. Crea/activa el entorno del proyecto primero." }
. ".\.venv\Scripts\Activate.ps1"
$env:TFM_QUANTUM_MODE = "pilot"
Write-Host "Modo cuántico PILOT: se seleccionará una molécula para probar xTB/ORCA." -ForegroundColor Cyan
python -m jupyter lab "notebooks\TFM_SAF_pipeline_cientifico_COMPLETO.ipynb"
