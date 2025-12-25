<script>
    import { onMount, tick } from "svelte";

    export let esClaro = false;

    const API_KEY = import.meta.env.VITE_API_BIBLE_KEY;
    const BASE_URL = "https://rest.api.bible/v1";

    let idBiblia = null;
    let nombreBiblia = "Consultando Biblias...";
    let contenidoPasaje = "";
    let referenciaPasaje = "PSA.23";

    let terminoBusqueda = "";
    let resultadosBusqueda = [];
    let estaBuscando = false;

    let cargando = true;
    let error = null;

    // Navegación Estructural
    let libros = [];
    let capitulos = [];
    let libroSeleccionado = null;
    let capituloSeleccionado = null;
    let mostrarSelector = false;

    const PASAJES_SEMILLA = [
        "PSA.23",
        "JHN.3.16",
        "PRO.3.5-6",
        "PHP.4.13",
        "ROM.8.28",
        "PSA.91",
    ];

    async function obtenerBiblia() {
        try {
            const res = await fetch(`${BASE_URL}/bibles?language=spa`, {
                headers: { "api-key": API_KEY },
            });

            if (!res.ok)
                throw new Error("Conexión limitada con el servidor bíblico");

            const data = await res.json();
            const biblias = data.data;

            if (biblias && biblias.length > 0) {
                const rvr = biblias.find(
                    (b) =>
                        b.abbreviation.includes("RVR") ||
                        b.name.includes("Reina"),
                );
                const seleccionada = rvr || biblias[0];

                idBiblia = seleccionada.id;
                nombreBiblia = seleccionada.nameLocal || seleccionada.name;

                await obtenerLibros();
                await obtenerPasaje(referenciaPasaje);
            }
        } catch (e) {
            error = "Bible API Key no detectada o inválida (Error 403).";
        } finally {
            cargando = false;
        }
    }

    async function obtenerLibros() {
        if (!idBiblia) return;
        try {
            const res = await fetch(`${BASE_URL}/bibles/${idBiblia}/books`, {
                headers: { "api-key": API_KEY },
            });
            const data = await res.json();
            libros = data.data;
        } catch (e) {
            console.error("Error al obtener libros:", e);
        }
    }

    async function seleccionarLibro(idLibro) {
        libroSeleccionado = idLibro;
        capitulos = [];
        capituloSeleccionado = null;
        try {
            const res = await fetch(
                `${BASE_URL}/bibles/${idBiblia}/books/${idLibro}/chapters`,
                {
                    headers: { "api-key": API_KEY },
                },
            );
            const data = await res.json();
            capitulos = data.data;
        } catch (e) {
            console.error("Error al obtener capítulos:", e);
        }
    }

    async function obtenerPasaje(idPasaje) {
        if (!idBiblia) return;
        cargando = true;
        error = null;
        estaBuscando = false;
        mostrarSelector = false;
        try {
            const res = await fetch(
                `${BASE_URL}/bibles/${idBiblia}/passages/${idPasaje}?content-type=html&include-notes=false&include-chapter-numbers=false&include-verse-numbers=true`,
                {
                    headers: { "api-key": API_KEY },
                },
            );

            if (!res.ok) throw new Error("Pasaje no localizado.");

            const data = await res.json();
            contenidoPasaje = data.data.content;
            referenciaPasaje = data.data.reference;
        } catch (e) {
            error = e.message;
        } finally {
            cargando = false;
        }
    }

    async function buscarEnBiblia() {
        if (!idBiblia || !terminoBusqueda) return;
        cargando = true;
        error = null;
        estaBuscando = true;
        mostrarSelector = false;
        resultadosBusqueda = [];

        try {
            const res = await fetch(
                `${BASE_URL}/bibles/${idBiblia}/search?query=${encodeURIComponent(terminoBusqueda)}&limit=20`,
                {
                    headers: { "api-key": API_KEY },
                },
            );

            if (!res.ok) throw new Error("Error en la búsqueda.");

            const data = await res.json();
            if (data.data && data.data.verses) {
                resultadosBusqueda = data.data.verses;
            } else {
                error = "Sin resultados para su búsqueda.";
            }
        } catch (e) {
            error = "Error: " + e.message;
        } finally {
            cargando = false;
        }
    }

    function manejarTecla(e) {
        if (e.key === "Enter") buscarEnBiblia();
    }

    function cargarPasajeAleatorio() {
        const aleatorio =
            PASAJES_SEMILLA[Math.floor(Math.random() * PASAJES_SEMILLA.length)];
        obtenerPasaje(aleatorio);
    }

    onMount(() => {
        obtenerBiblia();
    });

    $: claseTarjeta = esClaro
        ? "bg-[#fafaf9] border-stone-300 shadow-sm"
        : "bg-white/5 border-white/10";
    $: claseTexto = esClaro ? "text-stone-800" : "text-slate-200";
    $: claseSubTexto = esClaro ? "text-stone-500" : "text-slate-400";
    $: claseInput = esClaro
        ? "bg-white border-stone-200 text-stone-800 placeholder-stone-400"
        : "bg-black/20 border-white/10 text-slate-200 placeholder-slate-500";
</script>

<div
    class="flex flex-col h-full {claseTarjeta} rounded-xl overflow-hidden border transition-colors duration-500 relative"
>
    <!-- Cabecera -->
    <div
        class="px-6 py-4 border-b {esClaro
            ? 'border-stone-200 bg-stone-100/50'
            : 'border-white/10 bg-black/20'} flex flex-col gap-4"
    >
        <div class="flex justify-between items-center">
            <div class="flex flex-col">
                <span
                    class="text-[9px] uppercase font-bold tracking-[0.2em] {claseSubTexto}"
                    >Sagradas Escrituras</span
                >
                <span class="text-xs font-bold opacity-70 {claseTexto}"
                    >{nombreBiblia}</span
                >
            </div>
            <div class="flex gap-4">
                <button
                    on:click={() => (mostrarSelector = !mostrarSelector)}
                    class="text-[10px] uppercase font-bold tracking-widest {mostrarSelector
                        ? 'text-indigo-500'
                        : esClaro
                          ? 'text-stone-400 hover:text-stone-800'
                          : 'text-slate-500 hover:text-white'} transition-all"
                >
                    Explorar
                </button>
                <button
                    on:click={cargarPasajeAleatorio}
                    class="text-[10px] uppercase font-bold tracking-widest {esClaro
                        ? 'text-stone-400 hover:text-stone-800'
                        : 'text-slate-500 hover:text-white'} transition-all"
                >
                    Aleatorio
                </button>
            </div>
        </div>

        <div class="relative w-full">
            <input
                type="text"
                bind:value={terminoBusqueda}
                on:keydown={manejarTecla}
                placeholder="Introduzca cita o concepto..."
                class="w-full px-4 py-2 text-[11px] font-bold uppercase tracking-widest rounded border focus:outline-none focus:ring-1 focus:ring-indigo-500/50 transition-all {claseInput}"
            />
        </div>
    </div>

    <!-- Navegación Estructural (Selector) -->
    {#if mostrarSelector}
        <div class="flex-1 flex overflow-hidden bg-black/10 backdrop-blur-sm">
            <!-- Libros -->
            <div
                class="w-2/3 overflow-y-auto border-r border-white/5 p-4 space-y-1"
            >
                <span
                    class="text-[9px] uppercase font-bold tracking-widest opacity-30 mb-2 block"
                    >Libros</span
                >
                {#each libros as libro}
                    <button
                        on:click={() => seleccionarLibro(libro.id)}
                        class="w-full text-left px-3 py-2 text-[11px] uppercase font-bold tracking-wider transition-all {libroSeleccionado ===
                        libro.id
                            ? 'bg-indigo-600 text-white'
                            : 'opacity-50 hover:opacity-100 hover:bg-white/5'}"
                    >
                        {libro.name}
                    </button>
                {/each}
            </div>
            <!-- Capítulos -->
            <div class="w-1/3 overflow-y-auto p-4 space-y-1">
                <span
                    class="text-[9px] uppercase font-bold tracking-widest opacity-30 mb-2 block"
                    >Capítulos</span
                >
                {#if libroSeleccionado}
                    <div class="grid grid-cols-2 gap-1">
                        {#each capitulos as cap}
                            {#if cap.number !== "intro"}
                                <button
                                    on:click={() => obtenerPasaje(cap.id)}
                                    class="w-full text-center py-2 text-[11px] font-mono border border-transparent transition-all hover:bg-white/5 hover:border-white/10"
                                >
                                    {cap.number}
                                </button>
                            {/if}
                        {/each}
                    </div>
                {:else}
                    <div
                        class="text-[10px] opacity-20 uppercase font-bold tracking-widest text-center mt-10"
                    >
                        Seleccione un libro
                    </div>
                {/if}
            </div>
        </div>
    {:else}
        <!-- Lectura -->
        <div class="flex-1 overflow-y-auto p-8 relative">
            {#if cargando}
                <div
                    class="flex flex-col items-center justify-center h-full opacity-30"
                >
                    <span
                        class="text-[10px] uppercase font-bold tracking-[0.5em] animate-pulse"
                        >Sincronizando...</span
                    >
                </div>
            {:else if error}
                <div
                    class="flex flex-col items-center justify-center h-full text-center p-6 opacity-40"
                >
                    <p class="text-xs uppercase font-bold tracking-widest mb-4">
                        {error}
                    </p>
                    <button
                        on:click={obtenerBiblia}
                        class="text-[10px] uppercase font-bold tracking-widest underline"
                        >Reintentar</button
                    >
                </div>
            {:else if estaBuscando}
                <h3
                    class="text-[10px] uppercase tracking-widest font-bold mb-6 opacity-40"
                >
                    Resultados encontrados: {resultadosBusqueda.length}
                </h3>
                <div class="space-y-4">
                    {#each resultadosBusqueda as resultado}
                        <button
                            on:click={() =>
                                obtenerPasaje(
                                    resultado.chapterId || resultado.id,
                                )}
                            class="w-full text-left p-4 border transition-all {esClaro
                                ? 'bg-white border-stone-100 hover:border-indigo-300'
                                : 'bg-white/5 border-white/5 hover:border-indigo-500/50'}"
                        >
                            <div class="flex items-center justify-between mb-2">
                                <span
                                    class="font-bold text-xs uppercase tracking-widest {esClaro
                                        ? 'text-indigo-900'
                                        : 'text-indigo-400'}"
                                >
                                    {resultado.reference}
                                </span>
                            </div>
                            <p
                                class="text-[11px] leading-relaxed opacity-60 {claseTexto}"
                            >
                                {resultado.text}
                            </p>
                        </button>
                    {/each}
                </div>
            {:else}
                <h2
                    class="text-3xl font-bold mb-8 text-center uppercase tracking-tight {esClaro
                        ? 'text-indigo-950'
                        : 'text-indigo-100'}"
                >
                    {referenciaPasaje}
                </h2>

                <div
                    class="font-serif leading-loose text-lg text-justify {claseTexto} [&_span.v]:text-[10px] [&_span.v]:font-sans [&_span.v]:font-bold [&_span.v]:text-indigo-500/50 [&_span.v]:mr-2"
                >
                    {@html contenidoPasaje}
                </div>

                <div
                    class="mt-12 text-center border-t pt-6 {esClaro
                        ? 'border-stone-100'
                        : 'border-white/5'} opacity-20"
                >
                    <span
                        class="text-[9px] uppercase font-bold tracking-[0.4em]"
                        >Soli Deo Gloria</span
                    >
                </div>
            {/if}
        </div>
    {/if}
</div>

<style>
    :global(.p) {
        margin-bottom: 1.5rem;
    }
    :global(.q1, .q2) {
        margin-left: 1.5rem;
        font-style: italic;
    }
</style>
