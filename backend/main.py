# Parche de compatibilidad para Python 3.9
try:
    import importlib.metadata
    if not hasattr(importlib.metadata, 'packages_distributions'):
        import importlib_metadata
        importlib.metadata.packages_distributions = importlib_metadata.packages_distributions
except ImportError:
    pass

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import logging
# Cargar variables de entorno desde .env ANTES de importar servicios
from dotenv import load_dotenv
load_dotenv()

from database import obtener_db, inicializar_base_de_datos
import models
import schemas
from servicio_biblioteca import ServicioBiblioteca
from servicio_ia import servicio_ia
from servicio_vectorial import ServicioVectorial

app = FastAPI(
    title="El Arca API",
    description="Servidor centralizado para estudio teológico y gestión de biblioteca.",
    version="2.0.0"
)

# Configurar CORS para desarrollo local y producción (Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos de la biblioteca
RUTA_BIBLIOTECA = os.path.abspath(os.getenv("LIBRARY_PATH", "../public/library"))
if os.path.exists(RUTA_BIBLIOTECA):
    app.mount("/library", StaticFiles(directory=RUTA_BIBLIOTECA), name="library")
else:
    print(f"⚠️ RUTA DE BIBLIOTECA NO ENCONTRADA: {RUTA_BIBLIOTECA}")

# Inicializar DB al arranque (crear tablas si no existen)
@app.on_event("startup")
def evento_inicio():
    inicializar_base_de_datos()

@app.get("/", tags=["Estado"])
def leer_raiz():
    return {
        "estado": "en línea",
        "mensaje": "El Arca 2.0 está operativa",
        "version": "2.0.0"
    }

# --- ENDPOINTS: LIBROS DIGITALES ---

@app.get("/libros/digitales", response_model=List[schemas.LibroDigital], tags=["Biblioteca Digital"])
def listar_libros_digitales(db: Session = Depends(obtener_db)):
    return db.query(models.LibroDigital).all()

@app.post("/libros/digitales/escanear", tags=["Biblioteca Digital"])
def escanear_biblioteca(background_tasks: BackgroundTasks, db: Session = Depends(obtener_db)):
    LIBRARY_PATH = os.getenv("LIBRARY_PATH", "../public/library")
    background_tasks.add_task(ServicioBiblioteca.escanear_directorio, db, LIBRARY_PATH)
    return {"mensaje": "Escaneo local iniciado en segundo plano."}

@app.post("/libros/digitales/sincronizar-drive", tags=["Biblioteca Digital"])
def sincronizar_drive(background_tasks: BackgroundTasks, db: Session = Depends(obtener_db)):
    background_tasks.add_task(ServicioBiblioteca.sincronizar_con_drive, db)
    return {"mensaje": "Sincronización con Google Drive iniciada en segundo plano."}

@app.get("/libros/ver/{file_id}", tags=["Biblioteca Digital"])
def ver_libro_drive(file_id: str):
    """Proxy para visualizar archivos directamente desde Google Drive sin hacerlos públicos."""
    from servicio_drive import servicio_drive
    
    # Usamos generador para Streaming Real (cero RAM, velocidad instantánea)
    stream_generator = servicio_drive.generar_descarga(file_id)
    
    # Determinamos MIME type básico (asumimos PDF por defecto para el visor)
    media_type = "application/pdf"
    
    headers = {
        "Content-Disposition": "inline; filename=documento.pdf",
        "Content-Type": "application/pdf",
        "X-Content-Type-Options": "nosniff",
        "Cache-Control": "no-cache"
    }
    
    return StreamingResponse(
        stream_generator, 
        media_type=media_type,
        headers=headers
    )

# --- ENDPOINTS: LIBROS FÍSICOS ---

@app.get("/libros/fisicos", response_model=List[schemas.LibroFisico], tags=["Biblioteca Física"])
def listar_libros_fisicos(db: Session = Depends(obtener_db)):
    return db.query(models.LibroFisico).all()

@app.get("/libros/fisicos/isbn/{isbn}", tags=["Biblioteca Física"])
def buscar_libro_por_isbn(isbn: str):
    from servicio_biblioteca import ServicioFisico
    datos = ServicioFisico.buscar_por_isbn(isbn)
    if not datos:
        raise HTTPException(status_code=404, detail="No se encontraron datos para este ISBN")
    return datos

@app.post("/libros/fisicos", response_model=schemas.LibroFisico, tags=["Biblioteca Física"])
def agregar_libro_fisico(libro: schemas.LibroFisicoCrear, db: Session = Depends(obtener_db)):
    nuevo_libro = models.LibroFisico(**libro.dict())
    db.add(nuevo_libro)
    db.commit()
    db.refresh(nuevo_libro)
    return nuevo_libro

# --- ENDPOINTS: NOTAS (CUADERNO) ---

@app.get("/notas", response_model=List[schemas.Nota], tags=["Cuaderno"])
def listar_notas(db: Session = Depends(obtener_db)):
    return db.query(models.Nota).order_by(models.Nota.fecha_actualizacion.desc()).all()

@app.post("/notas", response_model=schemas.Nota, tags=["Cuaderno"])
def crear_nota(nota: schemas.NotaCrear, db: Session = Depends(obtener_db)):
    nueva_nota = models.Nota(**nota.dict())
    db.add(nueva_nota)
    db.commit()
    db.refresh(nueva_nota)
    return nueva_nota

@app.put("/notas/{nota_id}", response_model=schemas.Nota, tags=["Cuaderno"])
def actualizar_nota(nota_id: int, nota_actualizada: schemas.NotaCrear, db: Session = Depends(obtener_db)):
    db_nota = db.query(models.Nota).filter(models.Nota.id == nota_id).first()
    if not db_nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    
    for key, value in nota_actualizada.dict().items():
        setattr(db_nota, key, value)
    
    db.commit()
    db.refresh(db_nota)
@app.delete("/notas/{nota_id}", tags=["Cuaderno"])
def eliminar_nota(nota_id: int, db: Session = Depends(obtener_db)):
    db_nota = db.query(models.Nota).filter(models.Nota.id == nota_id).first()
    if not db_nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    db.delete(db_nota)
    db.commit()
    return {"mensaje": "Nota eliminada correctamente"}

# --- ENDPOINTS: DICCIONARIO TEOLÓGICO ---

@app.get("/diccionario/{termino}", tags=["Diccionario"])
def consultar_diccionario(termino: str, perspectiva: Optional[str] = "reformado"):
    definicion = servicio_ia.definir_termino(termino, perspectiva)
    return {"termino": termino, "definicion": definicion}

# --- ENDPOINTS: ASISTENTE IA (RAG) ---

servicio_vectorial = ServicioVectorial()

@app.post("/preguntar", tags=["Asistente IA"])
def preguntar_a_biblioteca(consulta: schemas.ConsultaBase):
    # 1. Buscar fragmentos relevantes
    contexto = ""
    try:
        resultados = servicio_vectorial.buscar_similitud(consulta.pregunta)
        if resultados and "documents" in resultados and resultados["documents"]:
            contexto = "\n".join(resultados["documents"][0])
    except Exception as e:
        print(f"Error en búsqueda vectorial: {e}")

    # 2. Generar respuesta con Gemini
    prompt = f"""
    Eres 'El Arca AI', un asistente especializado en teología y biblia. 
    Usa el siguiente contexto extraído de la biblioteca personal del usuario para responder a su pregunta.
    Si el contexto no contiene la información, usa tu conocimiento general pero prioriza el contexto.

    CONTEXTO:
    {contexto}

    PREGUNTA:
    {consulta.pregunta}

    Respuesta técnica, pastoral y profesional en español:
    """
    
    if not hasattr(servicio_ia, 'model') or servicio_ia.model is None:
        raise HTTPException(
            status_code=503, 
            detail="El servicio de IA no está configurado o la API Key es inválida."
        )

    try:
        respuesta = servicio_ia.model.generate_content(prompt)
        return {"respuesta": respuesta.text, "fuentes": resultados.get("metadatas", []) if contexto else []}
    except Exception as e:
        logger.error(f"Error generando contenido con Gemini: {e}")
        raise HTTPException(status_code=500, detail="Error interno al procesar la respuesta de la IA.")
