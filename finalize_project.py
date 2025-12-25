import os
import shutil
import logging
from pathlib import Path

# Configuración
ROOT_DIR = Path(".")
PROJECT_DIR = ROOT_DIR / "inventory-dashboard"
PUBLIC_LIB_DIR = PROJECT_DIR / "public" / "library"
SCRIPTS_DIR = PROJECT_DIR / "scripts"

# Carpetas/Archivos a conservar (además del proyecto)
KEEP_DIRS = ["inventory-dashboard", ".gemini", ".git"]
KEEP_FILES = ["finalize_project.py", "requirements.txt"] 

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def migrate_and_clean():
    # 1. Crear directorios destino
    if not PUBLIC_LIB_DIR.exists():
        PUBLIC_LIB_DIR.mkdir(parents=True)
    if not SCRIPTS_DIR.exists():
        SCRIPTS_DIR.mkdir(parents=True)

    # 2. Mover Biblioteca Arca
    source_lib = ROOT_DIR / "biblioteca_arca"
    if source_lib.exists():
        logger.info("📦 Migrando biblioteca_arca a public/library...")
        # Mover contenido, no la carpeta en sí para evitar public/library/biblioteca_arca
        for item in source_lib.iterdir():
            dest = PUBLIC_LIB_DIR / item.name
            if dest.exists():
                 if item.is_dir():
                     shutil.rmtree(dest)
                 else:
                     dest.unlink()
            shutil.move(str(item), str(PUBLIC_LIB_DIR))
        # Borrar carpeta vacía
        if source_lib.exists():
             shutil.rmtree(source_lib)
    else:
        logger.warning("⚠️ No se encontró biblioteca_arca.")

    # 3. Mover Scripts Python
    scripts = ["ark_inventory.py", "organize_arca.py", "add_physical.py", "download_icons.py", "unzip_drive.py"]
    logger.info("📜 Migrando scripts a inventory-dashboard/scripts/...")
    for script in scripts:
        src = ROOT_DIR / script
        if src.exists():
            shutil.move(str(src), str(SCRIPTS_DIR / script))

    # 4. Limpieza (The Purge)
    logger.info("🔥 Iniciando limpieza del directorio raíz...")
    # Nombre del archivo ZIP de salida
    zip_filename = "el_arca_v_final.zip"
    
    # Directorio que queremos comprimir (el actual)
    source_dir = "."
    
    for item in ROOT_DIR.iterdir():
        # Ignorar lo que debemos conservar
        if item.name in KEEP_DIRS or item.name in KEEP_FILES:
            continue
        
        try:
            if item.is_dir():
                logger.info(f"Eliminando directorio: {item.name}")
                shutil.rmtree(item)
            else:
                logger.info(f"Eliminando archivo: {item.name}")
                item.unlink()
        except Exception as e:
            logger.error(f"Error eliminando {item.name}: {e}")

    logger.info("✨ Limpieza completada. Proyecto consolidado en 'inventory-dashboard'.")

if __name__ == "__main__":
    migrate_and_clean()
