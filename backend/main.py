from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path
from core import ArcaScanner, FileProcessor

app = FastAPI(title="El Arca Brain", version="1.0.0")

# TODO: Ajustar a la ruta real de tu librería
LIBRARY_ROOT = os.path.join(os.getcwd(), "..", "public", "library")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "message": "El Cerebro de El Arca está escuchando 🧠"}

@app.get("/scan")
def scan_library_endpoint():
    """Escanea la carpeta library y lista archivos."""
    scanner = ArcaScanner(LIBRARY_ROOT)
    files = scanner.scan_directory()
    return {"count": len(files), "files": files[:100]} # Limitamos preview a 100

@app.post("/analyze")
def analyze_file(file_path: str):
    """Analiza un archivo específico (hash y texto) para IA."""
    # Seguridad básica: asegurar que esté dentro de library
    full_path = Path(LIBRARY_ROOT) / file_path
    
    if not full_path.exists():
        return {"error": "File not found"}
    
    hash_val = FileProcessor.get_file_hash(full_path)
    text_preview = FileProcessor.extract_text(full_path)[:500] # Primeros 500 chars
    
    return {
        "filename": full_path.name,
        "hash": hash_val,
        "text_preview": text_preview
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
