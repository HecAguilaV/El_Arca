Write-Host "🚀 Iniciando EL CEREBRO (Backend) de El Arca..." -ForegroundColor Cyan
Write-Host "Asegúrate de tener Python instalado y las dependencias (pip install -r backend/requirements.txt)" -ForegroundColor Yellow

# Verificar si python o py está disponible
if (Get-Command python -ErrorAction SilentlyContinue) {
    $py = "python"
}
elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $py = "py"
}
else {
    Write-Error "No se encontró Python instalado."
    exit 1
}

# Ejecutar usando el módulo directamente para evitar errores de PATH
Set-Location "backend"
& $py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
