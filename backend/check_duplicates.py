import os
import shutil
import json
from pathlib import Path
from collections import defaultdict
from core import ArcaScanner, FileProcessor

# Configuración
LIBRARY_PATH = Path("../public/library")
DUPLICATES_DIR = Path("../public/library/_duplicates_quarantine")
REPORT_FILE = Path("duplication_report.txt")

def main():
    print(f"🔍 Escaneando biblioteca en: {LIBRARY_PATH.resolve()}")
    
    if not LIBRARY_PATH.exists():
        print("❌ Error: No se encuentra la carpeta public/library")
        return

    # 1. Escanear
    scanner = ArcaScanner(LIBRARY_PATH)
    files = scanner.scan_directory()
    print(f"📂 Total archivos encontrados: {len(files)}")

    # 2. Hashing (Agrupar por contenido)
    print("🧠 Analizando contenido (Calculando Hashes)...")
    content_map = defaultdict(list)
    
    for i, file_meta in enumerate(files):
        full_path = Path(file_meta['full_path'])
        
        # Saltarse basura
        if file_meta['filename'] == ".DS_Store" or file_meta['filename'].startswith("~$"):
            continue

        try:
            file_hash = FileProcessor.get_file_hash(full_path)
            content_map[file_hash].append(file_meta)
            
            if i % 50 == 0:
                print(f"   Procesados {i}/{len(files)}...")
        except Exception as e:
            print(f"⚠️ Error leyendo {file_meta['filename']}: {e}")

    # 3. Identificar Duplicados
    duplicates_groups = {k: v for k, v in content_map.items() if len(v) > 1}
    
    print(f"\n✨ Análisis completado:")
    print(f"   Archivos únicos: {len(content_map)}")
    print(f"   Grupos de duplicados detectados: {len(duplicates_groups)}")

    if not duplicates_groups:
        print("✅ No se encontraron duplicados por contenido.")
        return

    # 4. Procesar Duplicados
    print(f"\n📦 Moviendo duplicados a: {DUPLICATES_DIR}")
    DUPLICATES_DIR.mkdir(parents=True, exist_ok=True)
    
    moved_count = 0
    with open(REPORT_FILE, "w", encoding="utf-8") as report:
        report.write("REPORTE DE DUPLICADOS EL ARCA\n")
        report.write("=============================\n\n")

        for hash_val, group in duplicates_groups.items():
            # Estrategia: Quedarse con el nombre más corto o el que NO tiene copia/números
            # Ordenar por longitud de nombre (ascendente) -> El más corto suele ser el original
            group.sort(key=lambda x: len(x['filename']))
            
            original = group[0]
            copies = group[1:]
            
            report.write(f"GRUPO {hash_val[:8]} (Contenido Idéntico):\n")
            report.write(f"   ✅ ORIGINAL (Conservado): {original['path']}\n")
            
            for copy in copies:
                src = Path(copy['full_path'])
                
                # Definir destino preservando estructura o plana? 
                # Plana con prefijo para evitar colisiones
                safe_name = f"{hash_val[:6]}_{copy['filename']}"
                dst = DUPLICATES_DIR / safe_name
                
                try:
                    shutil.move(src, dst)
                    msg = f"   🚫 MOVIDO A CUARENTENA: {copy['path']} -> {dst.name}"
                    print(msg)
                    report.write(msg + "\n")
                    moved_count += 1
                except Exception as e:
                    report.write(f"   ❌ ERROR MOVIENDO: {copy['path']} - {e}\n")
            
            report.write("\n")

    print(f"\n🧹 Limpieza finalizada. {moved_count} archivos movidos a '_duplicates_quarantine'.")
    print(f"📄 Revisa {REPORT_FILE.resolve()} para más detalles.")

if __name__ == "__main__":
    main()
