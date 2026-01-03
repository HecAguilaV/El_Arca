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
    allow_origins=[
        "http://localhost:5173", 
        "https://el-arca.vercel.app",
        "https://el-arca-git-main-hectors-projects-c4ab2891.vercel.app" # Opcional: para previews
    ],
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
    # Migración ligera automática para SQLite (Añadir columna es_favorita si falta)
    from database import engine
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            # Check si la columna existe (solo para SQLite/Postgres simple)
            try:
                conn.execute(text("SELECT es_favorita FROM notas LIMIT 1"))
            except Exception:
                conn.rollback() # Importante para Postgres: limpiar la transacción fallida antes de seguir
                print("⚠️ Aplicando migración: Añadiendo columna 'es_favorita' a tabla notas...")
                # Postgres requiere FALSE literal para booleanos, SQLite lo acepta también.
    # Migración: user_id
    try:
        with engine.connect() as conn:
            try:
                conn.execute(text("SELECT user_id FROM notas LIMIT 1"))
            except Exception:
                conn.rollback()
                print("⚠️ Aplicando migración: Añadiendo columna 'user_id' a notas...")
                conn.execute(text("ALTER TABLE notas ADD COLUMN user_id VARCHAR"))
                conn.commit()
    except Exception as e:
        print(f"Nota sobre migración user_id: {e}")

@app.get("/", tags=["Estado"])
def leer_raiz():
    return {
        "estado": "en línea",
        "mensaje": "El Arca 2.0 está operativa",
        "version": "2.1.0"
    }

# ... (omitted diagnostic code) ...

# --- ENDPOINTS: NOTAS (CUADERNO) ---

@app.get("/notas", response_model=List[schemas.Nota], tags=["Cuaderno"])
def listar_notas(user_id: Optional[str] = None, db: Session = Depends(obtener_db)):
    query = db.query(models.Nota)
    if user_id:
        query = query.filter(models.Nota.user_id == user_id)
    else:
        # Si no hay user_id (caso legacy o error), devolvemos las notas PUBLICAS/LEGACY (user_id IS NULL)
        # Ojo: esto significa que si entras sin loguear ves las notas viejas.
        query = query.filter(models.Nota.user_id == None)
        
    return query.order_by(models.Nota.fecha_actualizacion.desc()).all()

@app.post("/notas", response_model=schemas.Nota, tags=["Cuaderno"])
def crear_nota(nota: schemas.NotaCrear, user_id: Optional[str] = None, db: Session = Depends(obtener_db)):
    # Nota: NotaCrear no tiene user_id en el schema base, lo inyectamos aquí si viene en query param
    # Lo ideal sería actualizar el schema, pero lo haremos dinámicamente en el modelo
    datos_nota = nota.dict()
    if user_id:
        datos_nota["user_id"] = user_id
        
    nueva_nota = models.Nota(**datos_nota)
    db.add(nueva_nota)
    db.commit()
    db.refresh(nueva_nota)
    return nueva_nota

@app.put("/notas/{nota_id}", response_model=schemas.Nota, tags=["Cuaderno"])
def actualizar_nota(nota_id: int, nota_actualizada: schemas.NotaCrear, user_id: Optional[str] = None, db: Session = Depends(obtener_db)):
    query = db.query(models.Nota).filter(models.Nota.id == nota_id)
    # Seguridad básica: asegurar que solo editas tus notas si se pasa user_id (opcional por ahora)
    if user_id:
        query = query.filter(models.Nota.user_id == user_id)
        
    db_nota = query.first()
    
    if not db_nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada o permiso denegado")
    
    for key, value in nota_actualizada.dict().items():
        setattr(db_nota, key, value)
    
    db.commit()
    db.refresh(db_nota)
    return db_nota

@app.delete("/notas/{nota_id}", tags=["Cuaderno"])
def eliminar_nota(nota_id: int, user_id: Optional[str] = None, db: Session = Depends(obtener_db)):
    query = db.query(models.Nota).filter(models.Nota.id == nota_id)
    if user_id:
        query = query.filter(models.Nota.user_id == user_id)
        
    db_nota = query.first()
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
