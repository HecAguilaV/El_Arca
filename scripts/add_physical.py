import json
import logging
import argparse
import requests
from pathlib import Path
from datetime import datetime

# Configuración
INVENTORY_FILE = Path("inventario_arca.json")
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def get_book_metadata(isbn: str):
    """Obtiene metadatos de OpenLibrary."""
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    try:
        response = requests.get(url)
        data = response.json()
        key = f"ISBN:{isbn}"
        if key in data:
            return data[key]
        return None
    except Exception as e:
        logger.error(f"Error conectando a OpenLibrary: {e}")
        return None

def add_physical_book(isbn: str):
    if not INVENTORY_FILE.exists():
        logger.error("No se encuentra inventario_arca.json. Ejecuta ark_inventory.py primero.")
        return

    logger.info(f"Buscando ISBN: {isbn} ...")
    meta = get_book_metadata(isbn)
    
    title = meta.get("title", "Desconocido") if meta else "Libro Físico (Manual)"
    authors = ", ".join([a["name"] for a in meta.get("authors", [])]) if meta else "Autor Desconocido"
    
    if meta:
        logger.info(f"✅ Encontrado: '{title}' por {authors}")
    else:
        logger.warning("⚠️ No encontrado en OpenLibrary. Se agregará como genérico.")
        title = input("Ingrese Título: ") or title
        authors = input("Ingrese Autor: ") or authors

    # Cargar inventario
    with open(INVENTORY_FILE, 'r', encoding='utf-8') as f:
        inventory = json.load(f)

    # Crear entrada
    entry = {
        "path": "Estantería Real 🏠",
        "filename": f"{title} [{isbn}]",
        "format": "fisico",
        "size_bytes": 0,
        "category": "Libro Físico",
        "tags": "teología, libro, físico",
        "md5_hash": f"isbn_{isbn}",
        "is_duplicate": False,
        "page_count": meta.get("number_of_pages", 0) if meta else 0,
        "keywords": authors, # Usamos keywords para autor
        "title": title,
        "cover_url": meta.get("cover", {}).get("large", "") if meta else "",
        "added_at": datetime.now().isoformat()
    }
    
    inventory.append(entry)
    
    # Guardar
    with open(INVENTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=4, ensure_ascii=False)
    
    logger.info(f"🎉 Libro agregado exitosamente al inventario.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agregar libro físico al inventario")
    parser.add_argument("isbn", help="ISBN del libro (sin guiones preferiblemente)")
    args = parser.parse_args()
    
    add_physical_book(args.isbn)
