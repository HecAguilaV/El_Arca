<div align="center">
  <img src="public/LOGO.svg" alt="El Arca Logo" width="120" height="auto" />
  <h1>El Arca</h1>
  <p><em>"La sabiduría clama en las calles, alza su voz en las plazas..."</em> - Proverbios 1:20</p>
  <p><strong>Plataforma Integral de Estudio Teológico, Gestión Bibliotecaria y Devocional Digital.</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Versión-1.0.0-blue" alt="v1.0.0">
  </p>
</div>

---

## Descripción

El Arca es un sistema avanzado para la gestión de bibliotecas teológicas personales, estudio asistido por IA, toma de notas estructurada y entorno de enfoque devocional.

## Características Principales

### Entorno de Trabajo Dual
Una interfaz diseñada para la productividad teológica:
*   **Panel Izquierdo:** Recursos de lectura.
*   **Panel Derecho:** Herramientas de estudio.

### Seguridad y Privacidad
*   **Autenticación:** Login seguro vía Google.
*   **Aislamiento:** Datos privados por usuario.
*   **Acceso:** Restringido a usuarios autenticados.

### Asistente Teológico
*   **Personalidades:** Erudito, Neopuritano, Bautista Moderno.
*   **Chat Contextual:** Historial y formato Markdown.

### Herramientas
*   **Biblioteca Digital:** Gestión de libros PDF.
*   **Cuaderno de Notas:** Editor rico con auto-guardado.
*   **Diccionario Teológico:** Definiciones al vuelo.
*   **Temporizador + Música:** Para sesiones de estudio ("Deep Work").

### Configuración Técnica
*   **Frontend:** Svelte + Vite + TailwindCSS
*   **Backend:** Python (FastAPI) + SQLite
*   **Nube:** Despliegue en Vercel & Render

## Despliegue

### Variables de Entorno (.env)

```bash
VITE_API_BASE_URL="https://tu-backend.onrender.com"
VITE_FIREBASE_API_KEY="..."
GEMINI_API_KEY="..."
DATABASE_URL="sqlite:///./el_arca.db"
```

### Ejecución Local

1.  **Backend:**
    ```bash
    cd backend
    uvicorn main:app --reload
    ```

2.  **Frontend:**
    ```bash
    pnpm dev
    ```

---
**Autor**
Hector Aguila
>_Un Soñador con Poca RAM_ 👨🏻‍💻
