import vtracer
import os

def transformar_logo(ruta_entrada, ruta_salida):
    if not os.path.exists(ruta_entrada):
        print(f"Error: No se encuentra el archivo {ruta_entrada}")
        return

    print(f"Iniciando vectorización de {ruta_entrada}...")
    
    # vtracer.convert toma la ruta de entrada y de salida.
    # Los parámetros por defecto suelen ser muy buenos para logotipos.
    vtracer.convert_image_to_svg_py(ruta_entrada, ruta_salida)
    
    if os.path.exists(ruta_salida):
        print(f"Éxito: Logo convertido a {ruta_salida}")
    else:
        print("Error: No se pudo generar el archivo SVG.")

if __name__ == "__main__":
    entrada = "public/candidatoLogo.png"
    salida = "public/candidatoLogo.svg"
    transformar_logo(entrada, salida)
