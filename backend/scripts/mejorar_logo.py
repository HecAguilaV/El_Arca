import vtracer
import os
from lxml import etree

def procesar_logo_premium(entrada, salida, titulo, slogan):
    # 1. Convertir a SVG (vtracer preserva curvas de logos mejor que otros)
    print(f"Vectorizando {entrada}...")
    vtracer.convert_image_to_svg_py(entrada, salida)
    
    if not os.path.exists(salida):
        print("Error: No se generó el SVG")
        return

    # 2. Manipular el SVG para transparencia y texto real
    print("Aplicando transparencia y añadiendo texto editable...")
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(salida, parser)
    root = tree.getroot()
    
    # El primer path suele ser el fondo (FCFCFC o similar)
    # Buscamos paths que cubran todo el canvas o tengan colores casi blancos
    paths = root.xpath("//*[local-name()='path']")
    
    paths_borrados = 0
    for path in paths:
        fill = path.get("fill", "").upper()
        # Si el fill es blanco puro o casi blanco, lo quitamos
        if fill in ["#FCFCFC", "#FFFFFF", "#F9F9F8", "#FAFAFA"]:
            path.getparent().remove(path)
            paths_borrados += 1
            # Solo borramos el primero que suele ser el fondo
            if paths_borrados >= 1:
                break

    # 3. Añadir sistema de fuentes y texto
    # Ajustamos el viewBox si es necesario o simplemente añadimos al final
    width = int(root.get("width", "1024"))
    height = int(root.get("height", "1024"))
    
    # Crear un grupo para el texto
    text_group = etree.SubElement(root, "g", {
        "id": "capa-texto",
        "transform": f"translate({width//2}, {height - 100})",
        "style": "font-family: 'Inter', sans-serif; text-anchor: middle;"
    })

    # Título (El Arca)
    # Nota: El usuario quiere "El Arca" y luego el mensaje. 
    # El logo original ya tiene un "EL ARCA" vectorizado probablemente.
    # Vamos a añadir el slogan debajo.
    
    etree.SubElement(text_group, "text", {
        "y": "40",
        "fill": "#23384F", # Azul oscuro elegante
        "style": "font-size: 32px; font-weight: bold; letter-spacing: 0.1em; text-transform: uppercase;"
    }).text = titulo

    etree.SubElement(text_group, "text", {
        "y": "80", 
        "fill": "#627382", # Gris azulado profesional
        "style": "font-size: 18px; font-weight: 400; letter-spacing: 0.05em;"
    }).text = slogan

    # Guardar con formato
    with open(salida, "wb") as f:
        f.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8"))
    
    print(f"✅ Proceso completado. Archivo final: {salida}")

if __name__ == "__main__":
    archivo_entrada = "public/candidatoLogo.png"
    archivo_salida = "public/candidatoLogo.svg" # Sobreescribimos el anterior
    
    # Sugerencias de slogan:
    # 1. Tu espacio para el estudio teológico.
    # 2. Profundizando en la Verdad.
    # 3. Sabiduría al alcance de tu mano.
    
    procesar_logo_premium(
        archivo_entrada, 
        archivo_salida, 
        "EL ARCA", 
        "Tu espacio para el estudio teológico"
    )
