from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from database import obtener_db, inicializar_base_de_datos
import models
import schemas
from servicios import ServicioBiblioteca

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

# Inicializar DB al arranque (crear tablas si no existen)
@app.on_event("startup")
def startup_event():
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
    return {"mensaje": "Escaneo iniciado en segundo plano."}

# --- ENDPOINTS: LIBROS FÍSICOS ---

@app.get("/libros/fisicos", response_model=List[schemas.LibroFisico], tags=["Biblioteca Física"])
def listar_libros_fisicos(db: Session = Depends(obtener_db)):
    return db.query(models.LibroFisico).all()

@app.get("/libros/fisicos/isbn/{isbn}", tags=["Biblioteca Física"])
def buscar_libro_por_isbn(isbn: str):
    from servicios import ServicioFisico
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
    return db_nota
