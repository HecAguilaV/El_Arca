import os
import zipfile
import logging
from pathlib import Path
from tqdm import tqdm

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def unzip_recursive(start_dir: str):
    root_dir = Path(start_dir)
    if not root_dir.exists():
        logger.error(f"El directorio {root_dir} no existe.")
        return

    # Buscar todos los archivos .zip
    zip_files = list(root_dir.rglob("*.zip"))
    
    if not zip_files:
        logger.info("No se encontraron archivos .zip para descomprimir.")
        return

    logger.info(f"Se encontraron {len(zip_files)} archivos ZIP. Iniciando extracción...")

    for zip_path in tqdm(zip_files, desc="Descomprimiendo", unit="zip"):
        try:
            # Crear directorio de extracción con el mismo nombre del zip
            extract_to = zip_path.parent / zip_path.stem
            
            if not extract_to.exists():
                extract_to.mkdir()

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            
            logger.info(f"Descomprimido: {zip_path.name} -> {extract_to}")
            
            # Opcional: Eliminar el zip original para ahorrar espacio?
            # Por seguridad, mejor no borrar nada automáticamente.
            # zip_path.unlink() 
            
        except Exception as e:
            logger.error(f"Error al descomprimir {zip_path}: {e}")

    logger.info("Proceso de descompresión completado.")

if __name__ == "__main__":
    # Ruta específica de Google Drive del usuario
    target_drive = "Google Drive"
    unzip_recursive(target_drive)
