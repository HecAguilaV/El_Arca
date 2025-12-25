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
from servicio_vectorial import ServicioVectorial
from servicio_drive import servicio_drive

# Inicializar servicios globalmente para reuso
servicio_vectorial = ServicioVectorial()

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
                    db.refresh(nuevo_libro)

                    # --- NUEVO: INDEXACIÓN VECTORIAL (RAG) ---
                    if texto_preview:
                        try:
                            # Indexamos solo los primeros fragmentos para no saturar
                            # En el futuro podríamos dividir todo el libro en chunks
                            servicio_vectorial.indexar_fragmento(
                                id_libro=str(nuevo_libro.id),
                                texto=texto_preview,
                                metadatos={
                                    "titulo": nuevo_libro.titulo,
                                    "autor": "Desconocido",
                                    "categoria": nuevo_libro.categoria,
                                    "formato": nuevo_libro.formato
                                }
                            )
                            logger.info(f"Vectorizado en Chroma: {archivo.name}")
                        except Exception as ve:
                            logger.error(f"Error vectorizando {archivo.name}: {ve}")
                    
                    hashes_existentes.add(hash_val)
                    logger.info(f"Libro indexado y guardado: {archivo.name}")
                except Exception as e:
                    logger.error(f"Error procesando {archivo}: {e}")
                    db.rollback()

    @staticmethod
    def sincronizar_con_drive(db: Session):
        """Escanea Drive, añade nuevos y ELIMINA los que ya no existen en la nube."""
        logger.info("Iniciando sincronización completa con Google Drive...")
        archivos_drive = servicio_drive.listar_archivos()
        
        if not archivos_drive:
            logger.warning("No se encontraron archivos en Drive.")
            return

        # 1. Mapear lo que hay en Drive por MD5 (o por ID si el MD5 falla)
        mapa_drive = {f.get('md5Checksum'): f for f in archivos_drive if f.get('md5Checksum')}
        # Fallback para archivos sin MD5: usar ID de Drive
        ids_drive = {f.get('id') for f in archivos_drive}
        md5s_drive = set(mapa_drive.keys())

        # 2. Obtener lo que tenemos en la Base de Datos (solo libros de Drive)
        libros_db = db.query(LibroDigital).filter(LibroDigital.categoria == "Nube (Drive)").all()
        
        # 3. ELIMINACIÓN: Borrar de DB lo que ya NO está en Drive
        eliminados = 0
        for libro in libros_db:
            # Si no está por MD5 ni por ID, entonces se borró de la nube
            if libro.hash_md5 not in md5s_drive and libro.ruta not in ids_drive:
                db.delete(libro)
                eliminados += 1
        
        if eliminados > 0:
            db.commit()
            logger.info(f"Limpieza completada: {eliminados} registros eliminados (ya no existen en Drive).")

        if eliminados > 0:
            db.commit()
            logger.info(f"Limpieza completada: {eliminados} registros eliminados (ya no existen en Drive).")

        # 4. ADICIÓN: Añadir lo que está en Drive pero no en DB
        # Obtenemos sets de control para verificar existencia
        hashes_en_db = {l.hash_md5 for l in db.query(LibroDigital.hash_md5).filter(LibroDigital.hash_md5 != None).all()}
        ids_en_db = {l.ruta for l in db.query(LibroDigital.ruta).filter(LibroDigital.categoria == "Nube (Drive)").all()}
        
        nuevos = 0
        
        for f in archivos_drive:
            file_id = f.get('id')
            md5 = f.get('md5Checksum')
            name = f.get('name')
            
            # CRITERIO DE EXISTENCIA:
            # 1. Si tiene ID y ya está en DB (por ID/ruta) -> EXISTE.
            if file_id in ids_en_db:
                continue
                
            # 2. Si tiene MD5 y ese MD5 ya está en DB -> EXISTE (Deduplicación estricta).
            #    NOTA: Si el usuario quiere guardar duplicados, habría que comentar esto.
            #    Pero mantenemos deduplicación de contenido idéntico por sanidad.
            if md5 and md5 in hashes_en_db:
                continue
            
            try:
                # Si no tiene MD5 (Google Doc/Sheet), usamos el ID como "hash" temporal o lo dejamos nulo
                hash_final = md5 if md5 else f"gdoc_{file_id}"
                
                nuevo_libro = LibroDigital(
                    ruta=file_id,
                    nombre_archivo=name,
                    titulo=Path(name).stem,
                    formato=name.split('.')[-1] if '.' in name else 'gdoc',
                    tamano_bytes=int(f.get('size', 0)),
                    categoria="Nube (Drive)",
                    hash_md5=hash_final,
                    descripcion="Sincronizado desde la nube."
                )
                db.add(nuevo_libro)
                # Actualizamos sets en memoria para evitar intentar insertar duplicados en este mismo ciclo
                if md5: hashes_en_db.add(md5)
                ids_en_db.add(file_id)
                
                nuevos += 1
                
                if nuevos % 100 == 0:
                    db.commit()
            except Exception as e:
                logger.error(f"Error registrando {name}: {e}")
                db.rollback()

        db.commit()
        logger.info(f"Sincronización terminada. {nuevos} libros añadidos, {eliminados} eliminados.")

class ServicioFisico:
    @staticmethod
    def buscar_por_isbn(isbn: str):
        """Busca metadatos de un libro usando Open Library con fallback a Google Books."""
        # 1. Intentar Open Library
        try:
            url_ol = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
            res = requests.get(url_ol, timeout=5)
            data = res.json()
            key = f"ISBN:{isbn}"
            if key in data:
                info = data[key]
                return {
                    "titulo": info.get("title"),
                    "autor": ", ".join([a["name"] for a in info.get("authors", [])]),
                    "editorial": ", ".join([p["name"] for p in info.get("publishers", [])]),
                    "ano_publicacion": info.get("publish_date"),
                    "categoria": "General"
                }
        except Exception as e:
            logger.warning(f"Open Library falló para {isbn}: {e}")

        # 2. Fallback a Google Books
        try:
            url_gb = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
            res = requests.get(url_gb, timeout=5)
            data = res.json()
            if "items" in data:
                info = data["items"][0]["volumeInfo"]
                return {
                    "titulo": info.get("title"),
                    "autor": ", ".join(info.get("authors", ["Desconocido"])),
                    "editorial": info.get("publisher", "Desconocida"),
                    "ano_publicacion": info.get("publishedDate"),
                    "categoria": ", ".join(info.get("categories", ["General"]))
                }
        except Exception as e:
            logger.error(f"Google Books también falló para {isbn}: {e}")
            
        return None
