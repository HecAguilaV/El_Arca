# El Arca - Biblioteca Digital & Asistente Teológico

> *"La sabiduría clama en las calles, alza su voz en las plazas..."* - Proverbios 1:20

**# El Arca 2.0 🚢
> **Plataforma de Estudio Teológico y Gestión de Biblioteca Digital**

Sistema integral para la gestión de bibliotecas teológicas personales, estudio asistido por IA y toma de notas estructurada.

## 📊 Estado del Proyecto
![Estado](https://img.shields.io/badge/Estado-Desplegado-success)
![Versión](https://img.shields.io/badge/Versión-2.0.0-blue)
![Documentos](https://img.shields.io/badge/Biblioteca-~1200_Documentos-orange)

## 🌟 Características Principales

*   **Biblioteca Masiva:** Indexación y sincronización probada con **~1200 documentos** (PDF, DOCX) desde Google Drive.
*   **Asistente Teológico (RAG):** Chat contextual que responde preguntas basándose SOLO en tu biblioteca privada.
*   **Diccionario Generativo:** Definiciones teológicas profundas y etimológicas generadas al vuelo por IA.
*   **Cuaderno de Estudio:** Editor de texto enriquecido (Tiptap) con exportación a PDF "Editorial".
*   **Sincronización Nube:** Base de datos en Neon (Postgres) y archivos en Drive. de la [API.Bible](https://scripture.api.bible/).
*   **Versículo de Estudio**: Carga pasajes aleatorios o busca referencias específicas.
*   **Diseño "Soli Deo Gloria"**: Tipografía serif elegante y modo de lectura sin distracciones.

### 2. Asistente Teológico (IA)
*   **Aislamiento Seguro**: Un módulo de IA independiente (Gemini Flash) que **no** tiene acceso a tus datos privados ni a la API bíblica, garantizando privacidad.
*   **Personas**:
    *   **Erudito**: Académico, preciso y formal.
    *   **Neopuritano**: Enfocado en la santidad y la doctrina pura (Estilo Paul Washer).
    *   **Bautista Moderno**: Exegético, práctico y contemporáneo.
*   **Chat Optimizado**: Historial de conversación y formato Markdown.

### 3. Biblioteca Inteligente (Híbrida)
*   **Modo Local (PC)**: Gestiona miles de PDFs directos desde tu disco duro (`public/library`).
*   **Modo Nube (Web/Móvil)**: Integración con **Google Drive**.
    *   Usa el botón "Nube" (`CloudArrowUp`) para acceder a tus archivos desde cualquier lugar.
    *   La lista de libros (Catálogo) es visible en web, pero la descarga se hace vía Drive para no saturar el hosting.
*   **Filtros Rápidos**: Busca por categoría (Seminario, Escuela Dominical, Libros Físicos).
*   **Cuaderno de Notas**: Editor persistente para tus estudios.

### 4. El Cerebro (Backend Python)
*   Un potente backend en Python (`backend/`) que se encarga del trabajo sucio:
    *   **Deduplicación**: Elimina archivos repetidos usando Hash SHA-256.
    *   **Escaneo**: Indexa tu biblioteca en milisegundos.
    *   **Aplanamiento**: Mantiene tu carpeta de archivos ordenada y plana.

---

## Despliegue en Vercel

Para llevar "El Arca" a la nube:

1.  Sube este repo a GitHub (sin la carpeta `public/library`).
2.  Importa el proyecto en Vercel.
3.  Configura las **Variables de Entorno**:
    *   `VITE_GEMINI_API_KEY`: Tu clave de Google AI.
    *   `VITE_API_BIBLE_KEY`: Tu clave de API.Bible.
    *   `VITE_GOOGLE_DRIVE_URL`: Link a tu carpeta compartida de Drive.
    *   `VITE_API_URL`: (Opcional) URL de tu backend si lo despliegas aparte (ej. Render/Railway), o déjalo vacío para modo "Solo Frontend".

---

## Instalación y Uso

### Requisitos
*   **Node.js** (v18+) & **pnpm**
*   **Python** (v3.10+)

### Iniciar el Sistema ("Start Brain")
Para su comodidad, hemos incluido un script maestro que levanta tanto el Frontend como el Backend:

```powershell
./start_brain.ps1
```

Esto abrirá:
1.  **Frontend**: `http://localhost:5173` (La interfaz de usuario)
2.  **Backend**: `http://localhost:8000` (El servicio de datos)

---

## Personalización

*   **Tema "Stone"**: Un modo claro diseñado para reducir la fatiga visual, con tonos papel antiguo (`#e7e5e4`) y tinta gris oscuro.
*   **Modo Noche**: Para las vigilias de estudio (`#0f0f13`).

---

## Estructura del Proyecto

```
/
├── backend/            # Servicio Python (FastAPI)
│   ├── main.py         # Servidor API
│   ├── core.py         # Lógica de escaneo
│   └── check_duplicates.py # Limpieza de archivos
├── public/
│   └── library/        # TUS LIBROS (PDF/DOCX)
├── src/
│   ├── components/     # Widgets (Biblia, Chat, Notebook)
│   └── App.svelte      # Interfaz Principal
└── README.md           # Este archivo
```

---
**Héctor Aguila**   
>Un Soñador con Poca Ram 👨🏻‍💻 
