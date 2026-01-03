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
# Usamos allow_origin_regex para permitir las URLs dinámicas de preview de Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "https://el-arca.vercel.app",
        "https://el-arca.onrender.com"
    ],
    allow_origin_regex=r"https://el-arca.*\.vercel\.app", # Permite cualquier subdominio de Vercel que empiece por el-arca
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
                conn.execute(text("ALTER TABLE notas ADD COLUMN es_favorita BOOLEAN DEFAULT FALSE"))
                conn.commit()
    except Exception as e:
        print(f"Nota sobre migración es_favorita: {e}")

    # Migración: es_sistema
    try:
        with engine.connect() as conn:
            try:
                conn.execute(text("SELECT es_sistema FROM notas LIMIT 1"))
            except Exception:
                conn.rollback()
                print("⚠️ Aplicando migración: Añadiendo columna 'es_sistema' a notas...")
                conn.execute(text("ALTER TABLE notas ADD COLUMN es_sistema BOOLEAN DEFAULT FALSE"))
                conn.commit()
    except Exception as e:
        print(f"Nota sobre migración es_sistema: {e}")

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

    # Semilla: Nota de Bienvenida (Sistema)
    try:
        from sqlalchemy.orm import Session
        session = Session(bind=engine)
        
        # BUSCAR si existe nota de sistema
        nota_sistema = session.query(models.Nota).filter(models.Nota.es_sistema == True).first()
        
        contenido_bienvenida = """
        <h3 class="text-xl font-bold text-amber-500 mb-4">Saludo de Bienvenida</h3>
        <p class="mb-4">Hola, soy <strong>Héctor</strong>, desarrollador de este espacio de estudio bíblico.</p>
        <p class="mb-4">A quien comparta esta aplicación o tenga acceso, quiero contarles que esta es una idea nacida de la necesidad de tener un lugar de <em>inmersión</em> en el estudio de la Palabra. Aunque tradicionalmente este estudio ha sido físico, hoy en día la digitalización es parte de nuestras vidas, ¿por qué no consagrar también un espacio digital para ello?</p>
        <p class="mb-4">Inspirado por herramientas profesionales como <em>Logos (Faithlife)</em> o <em>e-Sword</em>, creé <strong>El Arca</strong>. Aquí he recopilado y centralizado más de 1.200 archivos (libros, manualidades, tareas) acumulados por mi familia y amigos a lo largo del tiempo, conformando esta Biblioteca Digital.</p>
        <p class="mb-4">Mi compromiso es seguir trabajando para indexar, categorizar y etiquetar cada archivo, facilitando una búsqueda temática profunda y precisa.</p>
        <p class="mb-4">Finalmente, deseo que tengan una experiencia enriquecedora y que esta herramienta sea un valor agregado real para su estudio teológico y devocional.</p>
        <hr class="border-gray-700 my-4"/>
        <p class="text-sm text-gray-400 italic">Cualquier comentario para mejorar es bienvenido. Pueden contactarme al hacer clic en el autor al final de la página.</p>
        """

        if not nota_sistema:
            print("🌱 Creando nota de bienvenida del sistema (Nueva)...")
            nueva_nota = models.Nota(
                titulo="Bienvenido a El Arca (Sistema)",
                contenido_html=contenido_bienvenida,
                previsualización="Nota global del sistema.",
                palabras_clave="sistema, inicio",
                es_favorita=False,
                es_sistema=True,
                user_id=None 
            )
            session.add(nueva_nota)
        else:
            print("🔄 Actualizando contenido de nota de sistema...")
            nota_sistema.contenido_html = contenido_bienvenida
            # Opcional: Actualizar título si es necesario
            nota_sistema.titulo = "Bienvenido a El Arca (Sistema)"
            
        session.commit()
        session.close()
    except Exception as e:
        print(f"Error gestionando nota semilla: {e}")

@app.get("/", tags=["Estado"])
def leer_raiz():
    return {
        "estado": "en línea",
        "mensaje": "El Arca 2.0 está operativa",
        "version": "2.1.0"
    }

# --- DIAGNÓSTICO ---
@app.get("/sistema/diagnostico", tags=["Estado"])
def diagnostico_sistema(db: Session = Depends(obtener_db)):
    """Verifica conectividad con DB, Google Drive y Vector Store."""
    resultado = {
        "base_datos": "conectada",
        "google_drive": "desconocido",
        "vector_store": "desconocido",
        "mime_type_test": "ok"
    }

    # 1. DB Check
    from sqlalchemy import text
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        resultado["base_datos"] = f"Error: {e}"

    # 2. Drive Check
    try:
        # Check simple de credenciales sin pedir archivos (evita 403 en scopes restringidos)
        from servicio_drive import servicio_drive
        if servicio_drive.creds or servicio_drive.api_key:
             resultado["google_drive"] = {"estado": "ok", "mensaje": "Credenciales configuradas"}
        else:
             resultado["google_drive"] = {"estado": "error", "mensaje": "Faltan credenciales"}
    except Exception as e:
        resultado["google_drive"] = {"estado": "error", "mensaje": str(e)}

    # 3. Vector Check
    try:
        # Simple ping implícito
        if servicio_vectorial and servicio_vectorial.client:
             servicio_vectorial.client.heartbeat()
             resultado["vector_store"] = "conectado"
        else:
             resultado["vector_store"] = "no inicializado"
    except Exception as e:
         resultado["vector_store"] = f"Error: {e}"

    return resultado

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
    try:
        background_tasks.add_task(ServicioBiblioteca.sincronizar_con_drive, db)
        return {"mensaje": "Sincronización con Google Drive iniciada en segundo plano."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/libros/ver/{file_id}", tags=["Biblioteca Digital"])
def ver_libro_drive(file_id: str):
    """Proxy para visualizar archivos directamente desde Google Drive sin hacerlos públicos."""
    from servicio_drive import servicio_drive
    
    try:
        # Usamos generador para Streaming Real (cero RAM, velocidad instantánea)
        stream_generator, mime_type, filename = servicio_drive.generar_descarga(file_id)
        
        # Validar si el generador es válido (servicio_drive devuelve generador vacío en error)
        if mime_type == "application/octet-stream" and filename == "error.bin":
            raise HTTPException(status_code=404, detail="Archivo no encontrado o inaccesible en Drive.")

        headers = {
            "Content-Disposition": f'inline; filename="{filename}"',
            "Content-Type": mime_type,
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "no-cache",
            "Access-Control-Allow-Origin": "*" # Header manual de seguridad por si falla middleware en streaming
        }
        
        return StreamingResponse(
            stream_generator, 
            media_type=mime_type,
            headers=headers
        )
    except Exception as e:
        print(f"Error sirviendo archivo {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

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
    # Buscamos la nota PRIMERO sin filtrar por usuario para ver permisos
    db_nota = db.query(models.Nota).filter(models.Nota.id == nota_id).first()
    
    if not db_nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    
    # 1. Protección de Notas de Sistema
    if db_nota.es_sistema:
        # PERMITIR EDITAR SOLO AL ADMIN
        ALLOWED_ADMINS = ["hdaguila@gmail.com", "hector@elarca.com"] 
        if user_id not in ALLOWED_ADMINS:
            raise HTTPException(status_code=403, detail="Solo el administrador puede editar notas del sistema.")

    # 2. Protección de Notas de Usuarios (si no es sistema)
    elif user_id and db_nota.user_id and db_nota.user_id != user_id:
         raise HTTPException(status_code=403, detail="No tienes permiso para editar esta nota.")
    
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
