import os
import requests
import logging
from pathlib import Path

# Configuración
ICONS_DIR = Path("inventory-dashboard/src/assets/icons")
ICONS_BASE_URL = "https://raw.githubusercontent.com/phosphor-icons/core/main/assets/regular"
ICONS_TO_FETCH = [
    "book.svg",
    "file-pdf.svg", 
    "magnifying-glass.svg",
    "copy.svg",
    "cross.svg",
    "chart-bar.svg", 
    "files.svg",
    "presentation.svg", # Para PPTs
    "check-circle.svg",
    "warning.svg"
]

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def download_icons():
    if not ICONS_DIR.exists():
        ICONS_DIR.mkdir(parents=True)
        logger.info(f"Creado directorio: {ICONS_DIR}")

    logger.info("Descargando iconos Phosphor...")

    for icon in ICONS_TO_FETCH:
        url = f"{ICONS_BASE_URL}/{icon}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                file_path = ICONS_DIR / icon
                with open(file_path, "wb") as f:
                    f.write(response.content)
                logger.info(f"✅ Descargado: {icon}")
            else:
                logger.error(f"❌ Error descargando {icon}: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Excepción con {icon}: {e}")

    logger.info("Descarga completa.")

if __name__ == "__main__":
    download_icons()
