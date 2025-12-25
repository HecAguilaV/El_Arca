from PIL import Image
import os

def quitar_fondo_premium(ruta_entrada, ruta_salida):
    print(f"Abriendo {ruta_entrada}...")
    img = Image.open(ruta_entrada).convert("RGBA")
    datas = img.getdata()

    newData = []
    # Usamos una tolerancia mayor para el fondo blanco que rodea al logo
    for item in datas:
        r, g, b, a = item
        
        # El fondo es predominantemente blanco puro (255,255,255) o muy cercano
        if r > 240 and g > 240 and b > 240:
            newData.append((255, 255, 255, 0)) # Transparente
        else:
            newData.append(item)

    img.putdata(newData)
    
    # Aplicar un pequeño suavizado en los bordes para quitar el "aliasing" feo
    from PIL import ImageFilter
    img = img.filter(ImageFilter.SMOOTH_MORE)
    
    img.save(ruta_salida, "PNG")
    print(f"✅ Guardado con transparencia limpia y suavizada en {ruta_salida}")

if __name__ == "__main__":
    archivo = "/Users/hector/.gemini/antigravity/brain/d50a6dd3-bb2b-483a-aba1-50e1f9ebb771/el_arca_elite_svg_style_logo_1766683923427.png"
    salida = "public/logoElite_Transparente.png"
    if os.path.exists(archivo):
        quitar_fondo_premium(archivo, salida)
    else:
        print(f"Error: El archivo {archivo} no existe")
