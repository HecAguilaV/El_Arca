import { writable } from 'svelte/store';
import { api } from './api';

// --- ESTADO DE UI ---
export const tema = writable(localStorage.getItem("arca_tema") || "auto");
export const usuario = writable(localStorage.getItem("arca_usuario") || "");
export const pestañaActiva = writable("biblioteca"); // 'biblioteca', 'notas', 'asistente', 'biblia'

// --- ESTADO DE DATOS ---
export const biblioteca = writable([]);
export const librosFisicos = writable([]);
export const notas = writable([]);
export const archivoAbierto = writable(null); // { id, ruta, nombre, formato }
export const cargando = writable(false);

// --- ACCIONES CENTRALIZADAS ---
export async function cargarTodo() {
    cargando.set(true);
    try {
        const [librosData, fisicosData, notasData] = await Promise.all([
            api.libros.listar(),
            api.fisicos.listar(),
            api.notas.listar()
        ]);
        biblioteca.set(librosData);
        librosFisicos.set(fisicosData);
        notas.set(notasData);
    } catch (error) {
        console.error("Error cargando datos:", error);
    } finally {
        cargando.set(false);
    }
}

export async function sincronizarNotas() {
    try {
        const data = await api.notas.listar();
        notas.set(data);
    } catch (error) {
        console.error("Error sincronizando notas:", error);
    }
}
