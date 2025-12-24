import os
import shutil

def flatten_directory(root_dir):
    print(f"--- Aplanando directorio: {root_dir} ---")
    
    # Lista para rastrear archivos movidos
    moved_count = 0
    collision_count = 0
    
    # Caminamos de abajo hacia arriba para poder borrar carpetas vacías fácilmente
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Si estamos en la raiz, no movemos nada (ya están ahí)
        if dirpath == root_dir:
            continue
            
        for filename in filenames:
            source_file = os.path.join(dirpath, filename)
            target_file = os.path.join(root_dir, filename)
            
            # Manejo de colisiones (si el archivo ya existe en la raiz)
            if os.path.exists(target_file):
                collision_count += 1
                name, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(target_file):
                    target_file = os.path.join(root_dir, f"{name}_{counter}{ext}")
                    counter += 1
            
            try:
                shutil.move(source_file, target_file)
                moved_count += 1
                # print(f"Movido: {filename}") # Demasiado ruido si hay muchos archivos
            except Exception as e:
                print(f"❌ Error moviendo {filename}: {e}")

        # Intentar borrar directorio si quedó vacío
        try:
            os.rmdir(dirpath)
        except OSError:
            # No está vacío (quizás quedaron archivos ocultos o de sistema), lo ignoramos
            pass

    print(f"\n✅ Proceso completado.")
    print(f"📁 Archivos movidos a la raíz: {moved_count}")
    print(f"⚠️ Renombrados por colisión: {collision_count}")
    print("El directorio ahora es plano y seguro para Windows/Drive.")

if __name__ == "__main__":
    LIBRARY_PATH = r"C:\Users\hdagu\Desktop\De TODO Cristiano\inventory-dashboard\public\library"
    flatten_directory(LIBRARY_PATH)
