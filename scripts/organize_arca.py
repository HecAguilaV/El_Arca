import os
import json
import shutil
import logging
from pathlib import Path
from tqdm import tqdm

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def organize_files():
    root_dir = Path(".")
    target_dir = root_dir / "biblioteca_arca"
    json_path = root_dir / "inventario_arca.json"

    if not json_path.exists():
        logger.error("No se encontró 'inventario_arca.json'. Ejecuta primero ark_inventory.py")
        return

    # Cargar inventario
    with open(json_path, 'r', encoding='utf-8') as f:
        inventory = json.load(f)

    # Filtrar no duplicados y archivos sin errores
    valid_files = [item for item in inventory if not item.get('is_duplicate') and not item.get('error')]
    
    logger.info(f"Se copiarán {len(valid_files)} archivos únicos a '{target_dir}'.")
    
    # Crear directorio destino
    if not target_dir.exists():
        target_dir.mkdir()

    success_count = 0
    
    for item in tqdm(valid_files, desc="Copiando archivos", unit="file"):
        try:
            source_path = root_dir / item['path']
            # Mantener estructura de carpetas relativa? 
            # El usuario pidió "crear una copia en un directorio", para evitar colisiones de nombre (ej. 01.pdf en distintas carpetas)
            # lo mejor es replicar la estructura o usar el hash como nombre.
            # Vamos a replicar la estructura para que sea legible.
            
            dest_path = target_dir / item['path']
            
            # Crear carpetas padres si no existen
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copiar
            if source_path.exists():
                shutil.copy2(source_path, dest_path)
                success_count += 1
            else:
                logger.warning(f"Archivo no encontrado en origen: {source_path}")
                
        except Exception as e:
            logger.error(f"Error copiando {item['filename']}: {e}")

    logger.info(f"Proceso finalizado. {success_count} archivos copiados exitosamente a '{target_dir}'.")

if __name__ == "__main__":
    organize_files()
