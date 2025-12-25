import json
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models
from pathlib import Path

def migrar_datos():
    json_path = Path("../public/data.json")
    if not json_path.exists():
        print("❌ No se encontró data.json para migrar.")
        return

    db = SessionLocal()
    from database import inicializar_base_de_datos
    inicializar_base_de_datos()
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            datos = json.load(f)

        print(f"🚀 Migrando {len(datos)} registros...")
        
        # Obtener hashes existentes
        hashes_db = {l.hash_md5 for l in db.query(models.LibroDigital.hash_md5).all()}
        
        registros_nuevos = 0
        for item in datos:
            md5 = item.get("md5_hash")
            if md5 and md5 not in hashes_db:
                nuevo_libro = models.LibroDigital(
                    ruta=item.get("path"),
                    nombre_archivo=item.get("filename"),
                    titulo=Path(item.get("filename")).stem,
                    formato=item.get("format"),
                    tamano_bytes=item.get("size_bytes"),
                    categoria=item.get("category", "General"),
                    etiquetas=item.get("tags", ""),
                    hash_md5=md5,
                    num_paginas=item.get("page_count", 0),
                    es_duplicado=item.get("is_duplicate", False)
                )
                db.add(nuevo_libro)
                hashes_db.add(md5)
                registros_nuevos += 1
        
        db.commit()
        print(f"✅ Migración completada. Se añadieron {registros_nuevos} libros nuevos.")
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrar_datos()
