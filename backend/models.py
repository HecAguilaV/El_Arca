from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import datetime

Base = declarative_base()

class LibroDigital(Base):
    """Metadatos de libros en PDF, DOCX, EPUB, etc."""
    __tablename__ = "libros_digitales"

    id = Column(Integer, primary_key=True, index=True)
    ruta = Column(String, unique=True, index=True)
    nombre_archivo = Column(String)
    titulo = Column(String, index=True)
    autor = Column(String, index=True)
    formato = Column(String(10))
    tamano_bytes = Column(Integer)
    categoria = Column(String, index=True)
    etiquetas = Column(String)  # Guardados como string separado por comas
    hash_md5 = Column(String, index=True)
    num_paginas = Column(Integer, default=0)
    descripcion = Column(Text)
    ubicacion_nube = Column(String)  # URL de Google Drive
    es_duplicado = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

class LibroFisico(Base):
    """Gestión de biblioteca física personal."""
    __tablename__ = "libros_fisicos"

    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String, unique=True, index=True)
    titulo = Column(String, index=True)
    autor = Column(String, index=True)
    editorial = Column(String)
    ano_publicacion = Column(Integer)
    categoria = Column(String, index=True)
    estanteria = Column(String)  # Ubicación física (Ej: Pasillo 1, Estante A)
    leido = Column(Boolean, default=False)
    notas_personales = Column(Text)
    tiene_version_digital = Column(Boolean, default=False)
    id_libro_digital = Column(Integer, ForeignKey("libros_digitales.id"), nullable=True)
    fecha_agregado = Column(DateTime(timezone=True), server_default=func.now())

class Nota(Base):
    """Contenido del Notebook (Cuaderno de Estudio)."""
    __tablename__ = "notas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    contenido_html = Column(Text)
    previsualización = Column(String)
    palabras_clave = Column(String)
    es_favorita = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class Configuracion(Base):
    """Preferencias del usuario y estado global."""
    __tablename__ = "configuracion"

    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String, unique=True, index=True)
    valor = Column(Text)
    descripcion = Column(String)
