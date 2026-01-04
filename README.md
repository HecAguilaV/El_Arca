# El Arca - Biblioteca Digital & Asistente Teológico

> *"La sabiduría clama en las calles, alza su voz en las plazas..."* - Proverbios 1:20

**# El Arca v2.1.0 🚢**
> **Plataforma Integral de Estudio Teológico, Gestión Bibliotecaria y Devocional Digital.**

Sistema avanzado para la gestión de bibliotecas teológicas personales, estudio asistido por IA, toma de notas estructurada y entorno de enfoque devocional.

## 📊 Estado del Proyecto
![Estado](https://img.shields.io/badge/Estado-Producción-success)
![Versión](https://img.shields.io/badge/Versión-2.1.0_Stable-blue)
![Stack](https://img.shields.io/badge/Stack-Svelte_FastAPI_Firebase-orange)

## 🌟 Características Principales (v2.1.0)

### 1. Entorno de Trabajo Dual ("Dual Workbench")
Una interfaz revolucionaria diseñada para la productividad teológica:
*   **Panel Izquierdo (Recursos):** Biblioteca Digital, Lector de PDFs/EPUBs, Biblioteca Física.
*   **Panel Derecho (Herramientas):** Cuaderno de Notas, Asistente IA, Biblia, Diccionario.
*   **Colapso Inteligente:** Maximiza tu espacio de lectura o escritura según lo necesites.

### 2. Seguridad y Privacidad
*   **Autenticación Robusta:** Login seguro vía **Google (Firebase Auth)**.
*   **Aislamiento de Datos:** Cada usuario tiene su propio "arca" privada. Tus notas, favoritos y configuraciones son invisibles para otros.
*   **Muro de Acceso:** Sin cuenta, no hay acceso. Protección total contra miradas indiscretas.

### 3. Asistente Teológico (IA)
*   **Personalidades Especializadas:**
    *   **Erudito:** Académico, exegético y formal.
    *   **Neopuritano:** Enfocado en la santidad y doctrina (Estilo Reformado/Puritano).
    *   **Bautista Moderno:** Práctico, contemporáneo y accesible.
*   **Chat Contextual:** Historial de conversación persistente y formateo Markdown.

### 4. Herramientas de Estudio
*   **Biblioteca Híbrida:** Gestión de libros digitales (PDF) y registro de tu biblioteca física.
*   **Cuaderno de Notas Avanzado:** Editor rico (Tiptap) con auto-guardado en base de datos.
*   **Diccionario Teológico:** Definiciones profundas generadas al vuelo.
*   **Temporizador Pomodoro + Música Ambiental:** Funciones integradas para sesiones de estudio profundo sin distracciones.

### 5. Configuración Técnica
*   **Backend:** Python (FastAPI) con base de datos SQLite (Gestionada por SQLAlchemy).
*   **Frontend:** Svelte + Vite + TailwindCSS.
*   **Nube:** Despliegue optimizado en Vercel (Front) y Render (Back).

---

## 🚀 Despliegue y Configuración

### Variables de Entorno
El sistema requiere las siguientes claves en tu archivo `.env` o configuración de Vercel/Render:

```bash
# Frontend
VITE_API_BASE_URL="https://tu-backend.onrender.com"
VITE_FIREBASE_API_KEY="..."
# Backend
GEMINI_API_KEY="..."
DATABASE_URL="sqlite:///./el_arca.db"
```

### Ejecución Local

1.  **Backend (Python):**
    ```bash
    cd backend
    pip install -r requirements.txt
    uvicorn main:app --reload
    ```

2.  **Frontend (Node):**
    ```bash
    pnpm install
    pnpm run dev
    ```

---

## 📱 Experiencia Móvil
"El Arca" es completamente responsiva (PWA Ready).
*   **Menú Acordeón:** Navegación fluida en pantallas pequeñas.
*   **Widgets Touch:** Control de música, temporizador y tema con un toque.

---

## Estructura del Proyecto

```
/
├── backend/            # API Python (FastAPI) & Base de Datos
│   ├── main.py         # Endpoints y Lógica de Negocio
│   ├── models.py       # Modelos SQLAlchemy (Usuario, Nota, Libro)
│   └── ...
├── src/
│   ├── components/     # Widgets Svelte (Cuaderno, Lector, etc.)
│   ├── lib/            # Lógica de Cliente (Firebase, Stores)
│   └── App.svelte      # Orquestador Principal
└── README.md           # Este archivo
```

---
**Héctor Aguila**
> *Un Soñador con Poca Ram 👨🏻‍💻*
> *Desarrollado para el Servicio de Apoyo a la Iglesia*
