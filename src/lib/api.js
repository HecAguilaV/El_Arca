/**
 * Servicio de API para El Arca 2.0
 * Centraliza las peticiones al backend de FastAPI.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function peticion(endpoint, opciones = {}) {
    const respuesta = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...opciones,
        headers: {
            "Content-Type": "application/json",
            ...opciones.headers,
        },
    });

    if (!respuesta.ok) {
        const error = await respuesta.json().catch(() => ({ detail: "Error desconocido" }));
        throw new Error(error.detail || "Error en la petición al servidor");
    }

    return respuesta.json();
}

export const api = {
    // Libros Digitales
    libros: {
        listar: () => peticion("/libros/digitales"),
        escanear: () => peticion("/libros/digitales/escanear", { method: "POST" }),
        sincronizarDrive: () => peticion("/libros/digitales/sincronizar-drive", { method: "POST" }),
    },

    // Libros Físicos
    fisicos: {
        listar: () => peticion("/libros/fisicos"),
        buscarISBN: (isbn) => peticion(`/libros/fisicos/isbn/${isbn}`),
        crear: (libro) => peticion("/libros/fisicos", { method: "POST", body: JSON.stringify(libro) }),
    },

    // Notas (Cuaderno)
    notas: {
        listar: () => peticion("/notas"),
        crear: (nota) => peticion("/notas", { method: "POST", body: JSON.stringify(nota) }),
        actualizar: (id, nota) => peticion(`/notas/${id}`, { method: "PUT", body: JSON.stringify(nota) }),
        eliminar: (id) => peticion(`/notas/${id}`, { method: "DELETE" }),
    },

    // Diccionario Teológico
    diccionario: {
        consultar: (termino, perspectiva = "reformado") =>
            peticion(`/diccionario/${encodeURIComponent(termino)}?perspectiva=${perspectiva}`),
    },

    // Asistente IA (RAG)
    asistente: {
        preguntar: (pregunta) => peticion("/preguntar", { method: "POST", body: JSON.stringify({ pregunta }) }),
    },
};
