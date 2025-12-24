import os

def check_long_paths(start_path, max_length=250):
    print(f"--- Buscando rutas mayores a {max_length} caracteres en: {start_path} ---")
    count = 0
    for root, dirs, files in os.walk(start_path):
        for name in files:
            full_path = os.path.join(root, name)
            # Normalizar separadores
            full_path = full_path.replace('/', '\\')
            
            if len(full_path) > max_length:
                count += 1
                excess = len(full_path) - max_length
                print(f"\n[LONGITUD: {len(full_path)}] (+{excess} chars)")
                print(f"ARCHIVO: {name}")
                print(f"RUTA:    {full_path}")
    
    if count == 0:
        print("\n✅ Felicidades! No se encontraron rutas demasiado largas.")
    else:
        print(f"\n⚠️ Se encontraron {count} archivos con rutas problemáticas.")
        print("SUGERENCIA: Acorta los nombres de las carpetas padre (ej: 'Guia del Instructor...' -> 'Guia Instructor').")

if __name__ == "__main__":
    # Ajusta esto a tu ruta real
    LIBRARY_PATH = r"C:\Users\hdagu\Desktop\De TODO Cristiano\inventory-dashboard\public\library"
    check_long_paths(LIBRARY_PATH)
