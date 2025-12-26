import os
from collections import defaultdict
from pathlib import Path

def analizar_biblioteca(ruta_base):
    print(f"--- Analizando biblioteca en: {ruta_base} ---")
    
    if not os.path.exists(ruta_base):
        print("❌ La carpeta no existe.")
        return

    conteo_tipos = defaultdict(int)
    total_archivos = 0
    archivos_sin_extension = 0
    
    for root, dirs, files in os.walk(ruta_base):
        # Ignorar archivos ocultos tipo .DS_Store
        files = [f for f in files if not f.startswith('.')]
        
        for file in files:
            path = Path(file)
            ext = path.suffix.lower()
            
            if ext:
                conteo_tipos[ext] += 1
            else:
                archivos_sin_extension += 1
            
            total_archivos += 1

    print("\n📊 RESULTADOS DEL ANÁLISIS:")
    print(f"Total de archivos encontrados: {total_archivos}")
    print("-" * 30)
    for ext, count in sorted(conteo_tipos.items(), key=lambda item: item[1], reverse=True):
        print(f"{ext}: {count}")
    
    if archivos_sin_extension > 0:
        print(f"(sin extensión): {archivos_sin_extension}")
        
    print("-" * 30)

if __name__ == "__main__":
    analizar_biblioteca("public/library")
