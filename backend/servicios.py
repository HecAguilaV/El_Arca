import os
import hashlib
import requests
from pathlib import Path
from sqlalchemy.orm import Session
from models import LibroDigital, LibroFisico
from pypdf import PdfReader
from docx import Document
from pptx import Presentation
import logging

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ArcaServicios")

class ProcesadorArchivos:
    @staticmethod
    def calcular_md5(ruta_archivo: Path) -> str:
        hash_md5 = hashlib.md5()
        with open(ruta_archivo, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def extraer_texto(ruta_archivo: Path, max_paginas: int = 5) -> str:
        ext = ruta_archivo.suffix.lower()
        texto = ""
        try:
            if ext == ".pdf":
                reader = PdfReader(ruta_archivo)
                for i in range(min(max_paginas, len(reader.pages))):
                    texto += reader.pages[i].extract_text() + "\n"
            elif ext == ".docx":
                doc = Document(ruta_archivo)
                for para in doc.paragraphs[:50]: # Unas cuantas líneas
                    texto += para.text + "\n"
            elif ext == ".txt":
                with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f:
                    texto = f.read(5000)
        except Exception as e:
            logger.error(f"Error extrayendo texto de {ruta_archivo}: {e}")
        return texto.strip()

class ServicioBiblioteca:
    @staticmethod
    def escanear_directorio(db: Session, ruta_raiz: str):
        raiz = Path(ruta_raiz)
        extensiones = [".pdf", ".docx", ".doc", ".epub", ".pptx", ".ppt", ".txt", ".jpg", ".png", ".jpeg"]
        
        # Obtener hashes existentes para evitar duplicados
        hashes_existentes = {l.hash_md5 for l in db.query(models.LibroDigital.hash_md5).all()}
        
        for archivo in raiz.rglob("*"):
            if archivo.is_file() and archivo.suffix.lower() in extensiones:
                try:
                    hash_val = ProcesadorArchivos.calcular_md5(archivo)
                    
                    # Si ya existe en DB, saltar o actualizar
                    if hash_val in hashes_existentes:
                        continue
                    
                    # Extraer info básica
                    stats = archivo.stat()
                    texto_preview = ProcesadorArchivos.extraer_texto(archivo)
                    
                    # Clasificación simple (mejorable con IA después)
                    categoria = "General"
                    if "manualidad" in texto_preview.lower() or "niños" in texto_preview.lower():
                        categoria = "Escuela Dominical"
                    elif "teología" in texto_preview.lower() or "doctrina" in texto_preview.lower():
                        categoria = "Seminario"

                    nuevo_libro = LibroDigital(
                        ruta=str(archivo.relative_to(raiz)),
                        nombre_archivo=archivo.name,
                        titulo=archivo.stem,
                        formato=archivo.suffix.lower().replace(".", ""),
                        tamano_bytes=stats.st_size,
                        categoria=categoria,
                        hash_md5=hash_val,
                        descripcion=texto_preview[:500]
                    )
                    
                    db.add(nuevo_libro)
                    db.commit()
                    hashes_existentes.add(hash_val)
                    logger.info(f"Libro indexado: {archivo.name}")
                except Exception as e:
                    logger.error(f"Error procesando {archivo}: {e}")
                    db.rollback()

class ServicioFisico:
    @staticmethod
    def buscar_por_isbn(isbn: str):
        """Busca metadatos de un libro usando Open Library API."""
        try:
            url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
            res = requests.get(url)
            data = res.json()
            
            key = f"ISBN:{isbn}"
            if key in data:
                info = data[key]
                return {
                    "titulo": info.get("title"),
                    "autor": ", ".join([a["name"] for a in info.get("authors", [])]),
                    "editorial": ", ".join([p["name"] for p in info.get("publishers", [])]),
                    "ano_publicacion": info.get("publish_date"),
                    "categoria": "General" # Open Library no siempre da categorías limpias
                }
        except Exception as e:
            logger.error(f"Error buscando ISBN {isbn}: {e}")
        return None
