from PIL import Image
from collections import Counter
import os

def analizar_colores(ruta):
    img = Image.open(ruta).convert("RGB")
    pixels = list(img.getdata())
    conteo = Counter(pixels)
    
    print(f"Top 15 colores en {ruta}:")
    for color, count in conteo.most_common(15):
        print(f"Color: {color}, Cantidad: {count}")

if __name__ == "__main__":
    analizar_colores("public/nuevoLogoTransparente.png")
