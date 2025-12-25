import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Prioridad: 1. DATABASE_URL (Railway/Vercel) 2. SQLite local para desarrollo si no hay env
DATABASE_URL = os.getenv("DATABASE_URL")

# Si no hay URL de Postgres, usamos una local temporal para no romper el desarrollo
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./el_arca_local.db"
    print("⚠️ DATABASE_URL no encontrada. Usando SQLite local para desarrollo.")

# Para Postgres en Railway a veces se necesita corregir el prefijo postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def inicializar_base_de_datos():
    from models import Base
    Base.metadata.create_all(bind=engine)
