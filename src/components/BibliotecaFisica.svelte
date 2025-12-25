<script>
    import { onMount } from "svelte";
    import { api } from "../lib/api";
    import { librosFisicos } from "../lib/stores";
    import toast from "svelte-french-toast";

    export let esClaro = false;

    let isbnBusqueda = "";
    let libroEncontrado = null;
    let cargando = false;
    let guardando = false;

    // Campos adicionales para el registro
    let ubicacion = "";
    let notas = "";

    async function buscarISBN() {
        if (!isbnBusqueda.trim()) return;
        cargando = true;
        libroEncontrado = null;
        try {
            libroEncontrado = await api.fisicos.buscarISBN(isbnBusqueda);
            toast.success("Libro localizado");
        } catch (e) {
            toast.error("No se encontró el libro o error de conexión");
        } finally {
            cargando = false;
        }
    }

    async function registrarLibro() {
        if (!libroEncontrado) return;
        guardando = true;
        try {
            const nuevoLibro = {
                titulo: libroEncontrado.titulo,
                autor: libroEncontrado.autor,
                isbn: isbnBusqueda,
                ubicacion: ubicacion,
                notas: notas,
                portada_url: libroEncontrado.portada_url,
                paginas: libroEncontrado.paginas,
            };
            await api.fisicos.crear(nuevoLibro);
            toast.success("Libro registrado en la biblioteca física");

            // Limpiar y actualizar lista
            isbnBusqueda = "";
            libroEncontrado = null;
            ubicacion = "";
            notas = "";

            const listaActualizada = await api.fisicos.listar();
            librosFisicos.set(listaActualizada);
        } catch (e) {
            toast.error("Error al registrar el libro");
        } finally {
            guardando = false;
        }
    }

    function manejarTecla(e) {
        if (e.key === "Enter") buscarISBN();
    }

    $: claseTarjeta = esClaro
        ? "bg-[#fafaf9] border-stone-300 shadow-sm"
        : "bg-white/5 border-white/10";
    $: claseTexto = esClaro ? "text-stone-800" : "text-slate-200";
    $: claseInput = esClaro
        ? "bg-white border-stone-200 text-stone-800"
        : "bg-black/20 border-white/10 text-slate-200";
</script>

<div
    class="flex flex-col h-full {claseTarjeta} rounded-xl border overflow-hidden transition-colors duration-500"
>
    <!-- Cabecera -->
    <div
        class="px-6 py-4 border-b {esClaro
            ? 'border-stone-200 bg-stone-100/50'
            : 'border-white/10 bg-black/20'}"
    >
        <div class="flex flex-col gap-1 mb-4">
            <span
                class="text-[9px] uppercase font-bold tracking-[0.2em] opacity-40 {claseTexto}"
                >Patrimonio Físico</span
            >
            <span class="text-xs font-bold {claseTexto}">Registro por ISBN</span
            >
        </div>

        <div class="flex gap-2">
            <input
                type="text"
                bind:value={isbnBusqueda}
                on:keydown={manejarTecla}
                placeholder="ISBN (ej: 978...)"
                class="flex-1 px-4 py-2 text-xs font-bold uppercase tracking-widest rounded border focus:outline-none focus:ring-1 focus:ring-indigo-500/50 transition-all {claseInput}"
            />
            <button
                on:click={buscarISBN}
                disabled={cargando}
                class="px-6 py-2 bg-indigo-600 text-white text-[10px] uppercase font-bold tracking-widest rounded transition-all hover:bg-indigo-700 disabled:opacity-50"
            >
                {cargando ? "Buscando..." : "Buscar"}
            </button>
        </div>
    </div>

    <!-- Contenido -->
    <div class="flex-1 overflow-y-auto p-6">
        {#if libroEncontrado}
            <div
                class="flex flex-col md:flex-row gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500"
            >
                {#if libroEncontrado.portada_url}
                    <div
                        class="w-32 flex-shrink-0 shadow-2xl rounded-lg overflow-hidden border {esClaro
                            ? 'border-stone-200'
                            : 'border-white/10'}"
                    >
                        <img
                            src={libroEncontrado.portada_url}
                            alt="Portada"
                            class="w-full h-auto"
                        />
                    </div>
                {/if}

                <div class="flex-1">
                    <h3 class="text-xl font-bold mb-1 {claseTexto}">
                        {libroEncontrado.titulo}
                    </h3>
                    <p
                        class="text-xs uppercase tracking-widest opacity-50 mb-6"
                    >
                        {libroEncontrado.autor}
                    </p>

                    <div class="grid grid-cols-1 gap-4">
                        <div class="flex flex-col gap-1">
                            <label
                                class="text-[9px] uppercase font-bold tracking-widest opacity-40"
                                >Ubicación Física</label
                            >
                            <input
                                type="text"
                                bind:value={ubicacion}
                                placeholder="Ejem: Estantería B, Fila 3"
                                class="w-full px-3 py-2 text-[11px] rounded border {claseInput} focus:outline-none focus:ring-1 focus:ring-indigo-500/50"
                            />
                        </div>

                        <div class="flex flex-col gap-1">
                            <label
                                class="text-[9px] uppercase font-bold tracking-widest opacity-40"
                                >Notas / Comentarios</label
                            >
                            <textarea
                                bind:value={notas}
                                placeholder="Estado del libro, si está prestado, etc."
                                class="w-full px-3 py-2 text-[11px] rounded border {claseInput} focus:outline-none focus:ring-1 focus:ring-indigo-500/50 h-20 resize-none"
                            ></textarea>
                        </div>

                        <button
                            on:click={registrarLibro}
                            disabled={guardando}
                            class="w-full py-3 bg-emerald-600 text-white text-[11px] uppercase font-bold tracking-widest rounded-lg transition-all hover:bg-emerald-700 disabled:opacity-50 mt-2"
                        >
                            {guardando ? "Guardando..." : "Confirmar Registro"}
                        </button>
                    </div>
                </div>
            </div>
        {:else}
            <div
                class="h-full flex flex-col items-center justify-center opacity-10 text-center px-10"
            >
                <span class="text-[40px] font-serif mb-4 italic">ISBN</span>
                <p class="text-[10px] uppercase font-bold tracking-widest">
                    Ingrese el código ISBN para extraer metadatos de Google
                    Books e incorporar el libro a su colección física.
                </p>
            </div>
        {/if}
    </div>
</div>
