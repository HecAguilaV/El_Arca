from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- ESQUEMAS: LIBROS DIGITALES ---

class LibroDigitalBase(BaseModel):
    ruta: str
    nombre_archivo: str
    titulo: Optional[str] = None
    autor: Optional[str] = None
    formato: str
    tamano_bytes: int
    categoria: str
    etiquetas: Optional[str] = ""
    hash_md5: str
    num_paginas: Optional[int] = 0
    descripcion: Optional[str] = None
    ubicacion_nube: Optional[str] = None

class LibroDigital(LibroDigitalBase):
    id: int
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True

# --- ESQUEMAS: LIBROS FÍSICOS ---

class LibroFisicoBase(BaseModel):
    isbn: Optional[str] = None
    titulo: str
    autor: Optional[str] = None
    editorial: Optional[str] = None
    ano_publicacion: Optional[int] = None
    categoria: Optional[str] = "General"
    estanteria: Optional[str] = None
    leido: Optional[bool] = False
    notas_personales: Optional[str] = None
    tiene_version_digital: Optional[bool] = False
    id_libro_digital: Optional[int] = None

class LibroFisicoCrear(LibroFisicoBase):
    pass

class LibroFisico(LibroFisicoBase):
    id: int
    fecha_agregado: datetime

    class Config:
        from_attributes = True

# --- ESQUEMAS: NOTAS ---

class NotaBase(BaseModel):
    titulo: str
    contenido_html: str
    previsualización: Optional[str] = ""
    palabras_clave: Optional[str] = ""

class NotaCrear(NotaBase):
    pass

class Nota(NotaBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True

# --- ESQUEMAS: CONSULTAS IA ---

class ConsultaBase(BaseModel):
    pregunta: str
