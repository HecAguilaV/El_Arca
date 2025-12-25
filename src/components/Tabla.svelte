<script>
    import { archivoAbierto } from "../lib/stores";
    export let datos = [];
    export let esClaro = false;

    let busqueda = "";

    // Estado de Ordenación
    let campoOrden = "nombre_archivo";
    let direccionOrden = "asc";

    function alternarOrden(campo) {
        if (campoOrden === campo) {
            direccionOrden = direccionOrden === "asc" ? "desc" : "asc";
        } else {
            campoOrden = campo;
            direccionOrden = "asc";
        }
    }

    $: datosFiltrados = datos
        .filter((item) => {
            if (!busqueda) return true;
            const termino = busqueda.toLowerCase();
            return (
                (item.nombre_archivo &&
                    item.nombre_archivo.toLowerCase().includes(termino)) ||
                (item.titulo && item.titulo.toLowerCase().includes(termino)) ||
                (item.autor && item.autor.toLowerCase().includes(termino)) ||
                (item.etiquetas &&
                    item.etiquetas.toLowerCase().includes(termino)) ||
                (item.categoria &&
                    item.categoria.toLowerCase().includes(termino))
            );
        })
        .sort((a, b) => {
            let valA = a[campoOrden] || "";
            let valB = b[campoOrden] || "";

            if (campoOrden === "num_paginas" || campoOrden === "tamano_bytes") {
                valA = Number(valA) || 0;
                valB = Number(valB) || 0;
            } else {
                valA = valA.toString().toLowerCase();
                valB = valB.toString().toLowerCase();
            }

            if (valA < valB) return direccionOrden === "asc" ? -1 : 1;
            if (valA > valB) return direccionOrden === "asc" ? 1 : -1;
            return 0;
        });

    function copiarRuta(ruta) {
        navigator.clipboard.writeText(ruta);
    }

    const esWeb =
        typeof window !== "undefined" &&
        window.location.hostname.includes("vercel.app");

    function manejarClickArchivo(e, fila) {
        e.preventDefault();
        archivoAbierto.set({
            ruta: fila.ruta,
            nombre: fila.titulo || fila.nombre_archivo,
            formato: fila.formato,
        });
    }

    // Clases Dinámicas
    $: claseContenedor = esClaro
        ? "bg-[#fafaf9] border-stone-300"
        : "bg-white/5 border-white/10";
    $: claseBusqueda = esClaro
        ? "bg-stone-200 border-stone-300"
        : "bg-black/20 border-white/10";
    $: claseInput = esClaro
        ? "text-stone-800 placeholder-stone-500"
        : "text-white placeholder-slate-500";
    $: claseCabecera = esClaro
        ? "bg-stone-100 border-b border-stone-200"
        : "bg-[#1a1a20]";
    $: claseTextoCabecera = esClaro
        ? "text-stone-600 hover:text-stone-800"
        : "text-slate-400 hover:text-white";
    $: claseFilaHover = esClaro
        ? "hover:bg-stone-100"
        : "hover:bg-white/[0.02]";
    $: claseTextoPrincipal = esClaro ? "text-stone-900" : "text-slate-200";
    $: claseTextoSecundario = esClaro ? "text-stone-500" : "text-slate-500";
    $: claseBordeDivision = esClaro ? "divide-stone-200" : "divide-white/5";
</script>

<div
    class="{claseContenedor} border rounded-xl overflow-hidden backdrop-blur-md flex flex-col h-full transition-colors duration-500"
>
    <!-- Barra de Búsqueda -->
    <div class="p-4 border-b {claseBusqueda} flex items-center gap-4">
        <span class="text-[10px] uppercase font-bold tracking-widest opacity-40"
            >Buscar</span
        >
        <input
            type="text"
            bind:value={busqueda}
            placeholder="Título, autor, categoría o etiquetas..."
            class="flex-1 bg-transparent border-none focus:outline-none focus:ring-0 text-sm {claseInput}"
        />
        <div
            class="hidden sm:block px-3 py-1 rounded-full text-[10px] uppercase font-bold tracking-widest bg-black/10 opacity-50"
        >
            {datosFiltrados.length} entradas
        </div>
    </div>

    <!-- Contenedor de Tabla -->
    <div class="overflow-auto flex-1">
        <table class="w-full text-left border-collapse">
            <thead class="sticky top-0 z-10 shadow-sm {claseCabecera}">
                <tr>
                    <th
                        class="p-4 text-[10px] font-bold uppercase tracking-widest cursor-pointer select-none group {claseTextoCabecera}"
                        on:click={() => alternarOrden("nombre_archivo")}
                    >
                        Documento {campoOrden === "nombre_archivo"
                            ? direccionOrden === "asc"
                                ? "↑"
                                : "↓"
                            : ""}
                    </th>
                    <th
                        class="p-4 text-[10px] font-bold uppercase tracking-widest cursor-pointer select-none group {claseTextoCabecera}"
                        on:click={() => alternarOrden("categoria")}
                    >
                        Categoría {campoOrden === "categoria"
                            ? direccionOrden === "asc"
                                ? "↑"
                                : "↓"
                            : ""}
                    </th>
                    <th
                        class="p-4 text-[10px] font-bold uppercase tracking-widest cursor-pointer select-none group {claseTextoCabecera}"
                        on:click={() => alternarOrden("num_paginas")}
                    >
                        Páginas {campoOrden === "num_paginas"
                            ? direccionOrden === "asc"
                                ? "↑"
                                : "↓"
                            : ""}
                    </th>
                    <th
                        class="p-4 text-[10px] font-bold uppercase tracking-widest {claseTextoCabecera}"
                    >
                        Etiquetas
                    </th>
                </tr>
            </thead>
            <tbody class="divide-y {claseBordeDivision}">
                {#each datosFiltrados.slice(0, 200) as fila (fila.id || fila.hash_md5 + fila.ruta)}
                    <tr class="{claseFilaHover} transition-colors group">
                        <td class="p-4">
                            <a
                                href="/library/{fila.ruta}"
                                on:click={(e) => manejarClickArchivo(e, fila)}
                                class="block group/link"
                            >
                                <div
                                    class="text-sm font-medium {claseTextoPrincipal} group-hover/link:text-indigo-500 transition-colors"
                                >
                                    {fila.titulo || fila.nombre_archivo}
                                </div>
                                <div
                                    class="text-[10px] uppercase tracking-wider mt-1 opacity-50 font-mono"
                                >
                                    {fila.formato} — {fila.autor ||
                                        "Autor desconocido"}
                                </div>
                            </a>
                        </td>
                        <td class="p-4">
                            <span
                                class="text-[10px] uppercase font-bold tracking-widest opacity-70"
                            >
                                {fila.categoria}
                            </span>
                        </td>
                        <td
                            class="p-4 text-xs font-mono {claseTextoSecundario}"
                        >
                            {fila.num_paginas || 0}
                        </td>
                        <td class="p-4">
                            <div class="flex flex-wrap gap-2">
                                {#if fila.etiquetas}
                                    {#each fila.etiquetas.split(",") as etiqueta}
                                        <span
                                            class="text-[9px] uppercase font-bold tracking-wider px-2 py-0.5 border {claseBordeDivision} opacity-50"
                                        >
                                            {etiqueta.trim()}
                                        </span>
                                    {/each}
                                {:else}
                                    <span class="opacity-20">—</span>
                                {/if}
                            </div>
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>

        {#if datosFiltrados.length > 200}
            <div
                class="p-6 text-center text-[10px] uppercase font-bold tracking-[0.2em] opacity-30"
            >
                Paginación automática activa — Mostrando 200 de {datosFiltrados.length}
            </div>
        {/if}
    </div>
</div>

<style>
    ::-webkit-scrollbar {
        width: 3px;
    }
    ::-webkit-scrollbar-thumb {
        background-color: rgba(128, 128, 128, 0.3);
    }
</style>
