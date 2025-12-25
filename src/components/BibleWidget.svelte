<script>
    import { onMount } from "svelte";

    export let isLight = false;

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

                await obtenerPasaje(referenciaPasaje);
            }
        } catch (e) {
            error = "Requiere configuración de clave API personalizada.";
        }
    }

    async function obtenerPasaje(idPasaje) {
        if (!idBiblia) return;
        cargando = true;
        error = null;
        estaBuscando = false;
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

    $: claseTarjeta = isLight
        ? "bg-[#fafaf9] border-stone-300 shadow-sm"
        : "bg-white/5 border-white/10";
    $: claseTexto = isLight ? "text-stone-800" : "text-slate-200";
    $: claseSubTexto = isLight ? "text-stone-500" : "text-slate-400";
    $: claseInput = isLight
        ? "bg-white border-stone-200 text-stone-800 placeholder-stone-400"
        : "bg-black/20 border-white/10 text-slate-200 placeholder-slate-500";
</script>

<div
    class="flex flex-col h-full {claseTarjeta} rounded-xl overflow-hidden border transition-colors duration-500 relative"
>
    <!-- Cabecera -->
    <div
        class="px-6 py-4 border-b {isLight
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
            <button
                on:click={cargarPasajeAleatorio}
                class="text-[10px] uppercase font-bold tracking-widest {isLight
                    ? 'text-stone-400 hover:text-stone-800'
                    : 'text-slate-500 hover:text-white'} transition-all"
            >
                Aleatorio
            </button>
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
                            obtenerPasaje(resultado.chapterId || resultado.id)}
                        class="w-full text-left p-4 border transition-all {isLight
                            ? 'bg-white border-stone-100 hover:border-indigo-300'
                            : 'bg-white/5 border-white/5 hover:border-indigo-500/50'}"
                    >
                        <div class="flex items-center justify-between mb-2">
                            <span
                                class="font-bold text-xs uppercase tracking-widest {isLight
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
                class="text-3xl font-bold mb-8 text-center uppercase tracking-tight {isLight
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
                class="mt-12 text-center border-t pt-6 {isLight
                    ? 'border-stone-100'
                    : 'border-white/5'} opacity-20"
            >
                <span class="text-[9px] uppercase font-bold tracking-[0.4em]"
                    >Soli Deo Gloria</span
                >
            </div>
        {/if}
    </div>
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
