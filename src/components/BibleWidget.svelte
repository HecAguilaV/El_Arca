<script>
    import { onMount } from "svelte";
    import {
        BookOpen,
        ArrowClockwise,
        MagnifyingGlass,
        CaretRight,
    } from "phosphor-svelte";

    export let isLight = false;

    const API_KEY = import.meta.env.VITE_API_BIBLE_KEY;
    // Endpoint standard. Si falla, usar rest.api.bible
    const BASE_URL = "https://rest.api.bible/v1";

    let bibleId = null;
    let bibleName = "Cargando Biblia...";
    let passageContent = "";
    let passageReference = "Salmos 23"; // Default

    // Estado de Búsqueda
    let searchTerm = "";
    let searchResults = [];
    let isSearching = false;

    let loading = true;
    let error = null;

    // Lista de pasajes "semilla" para la demo
    const SEED_PASSAGES = [
        "PSA.23",
        "JHN.3.16",
        "PRO.3.5-6",
        "PHP.4.13",
        "ROM.8.28",
        "PSA.91",
    ];

    // 1. Obtener Biblia en Español (Preferimos RVR09 si está, o la primera que llegue)
    async function fetchBible() {
        try {
            const res = await fetch(`${BASE_URL}/bibles?language=spa`, {
                headers: { "api-key": API_KEY },
            });

            if (!res.ok) throw new Error("Error conectando a API.Bible");

            const data = await res.json();
            const bibles = data.data;

            if (bibles && bibles.length > 0) {
                // Buscar RVR09 por si acaso, sino la primera
                const rvr = bibles.find(
                    (b) =>
                        b.abbreviation.includes("RVR") ||
                        b.name.includes("Reina"),
                );
                const selected = rvr || bibles[0];

                bibleId = selected.id;
                bibleName = selected.nameLocal || selected.name;

                await fetchPassage(passageReference);
            } else {
                error = "No se encontraron biblias en español.";
            }
        } catch (e) {
            console.error(e);
            error = "Error de conexión. Verifica tu API Key.";
        }
    }

    // 2. Obtener Pasaje (Lectura)
    async function fetchPassage(passageId) {
        if (!bibleId) return;
        loading = true;
        error = null;
        isSearching = false; // Volver a modo lectura
        try {
            const res = await fetch(
                `${BASE_URL}/bibles/${bibleId}/passages/${passageId}?content-type=html&include-notes=false&include-chapter-numbers=false&include-verse-numbers=true`,
                {
                    headers: { "api-key": API_KEY },
                },
            );

            if (!res.ok) throw new Error("No se pudo cargar el pasaje.");

            const data = await res.json();
            passageContent = data.data.content; // Viene en HTML
            passageReference = data.data.reference;
        } catch (e) {
            error = e.message;
        } finally {
            loading = false;
        }
    }

    // 3. Buscar (Texto o Referencia)
    async function searchBible() {
        if (!bibleId || !searchTerm) return;
        loading = true;
        error = null;
        isSearching = true;
        searchResults = [];

        try {
            // Endpoint de búsqueda
            const res = await fetch(
                `${BASE_URL}/bibles/${bibleId}/search?query=${encodeURIComponent(searchTerm)}&limit=20`,
                {
                    headers: { "api-key": API_KEY },
                },
            );

            if (!res.ok) throw new Error("Error en la búsqueda.");

            const data = await res.json();
            if (data.data && data.data.verses) {
                searchResults = data.data.verses; // Array { reference, text, id, ... }
            } else {
                error = "No se encontraron resultados.";
            }
        } catch (e) {
            error = "Error al buscar: " + e.message;
        } finally {
            loading = false;
        }
    }

    function handleKeydown(e) {
        if (e.key === "Enter") searchBible();
    }

    function loadRandomPassage() {
        const random =
            SEED_PASSAGES[Math.floor(Math.random() * SEED_PASSAGES.length)];
        fetchPassage(random);
    }

    onMount(() => {
        fetchBible();
    });

    // Estilos Dinámicos
    $: cardClass = isLight
        ? "bg-[#fafaf9] border-stone-300 shadow-sm"
        : "bg-white/5 border-white/10";
    $: textClass = isLight ? "text-stone-800" : "text-slate-200";
    $: subTextClass = isLight ? "text-stone-500" : "text-slate-400";
    $: verseClass = isLight ? "prose-stone" : "prose-invert";

    // Estilos Input Búsqueda
    $: inputClass = isLight
        ? "bg-white border-stone-200 text-stone-800 placeholder-stone-400 focus:border-indigo-400"
        : "bg-black/20 border-white/10 text-slate-200 placeholder-slate-500 focus:border-indigo-500";
</script>

<div
    class="flex flex-col h-full {cardClass} rounded-xl overflow-hidden border transition-colors duration-500 relative"
>
    <!-- Header de la Card -->
    <div
        class="px-5 py-3 border-b {isLight
            ? 'border-stone-200 bg-stone-100/50'
            : 'border-white/10 bg-black/20'} flex flex-col gap-3 backdrop-blur-sm"
    >
        <!-- Top Row: Icon + Bible Name -->
        <div class="flex justify-between items-center">
            <div class="flex items-center gap-2">
                <BookOpen
                    size={18}
                    class={isLight ? "text-indigo-600" : "text-indigo-400"}
                />
                <div class="flex flex-col">
                    <span
                        class="text-[10px] uppercase font-bold tracking-widest {subTextClass}"
                        >Sagradas Escrituras</span
                    >
                    <span
                        class="text-[9px] truncate max-w-[150px] opacity-70 {textClass}"
                        >{bibleName}</span
                    >
                </div>
            </div>
            <button
                on:click={loadRandomPassage}
                class="p-1.5 rounded-lg transition-colors {isLight
                    ? 'hover:bg-stone-200 text-stone-600'
                    : 'hover:bg-white/10 text-slate-400'}"
                title="Pasaje Aleatorio"
            >
                <ArrowClockwise size={16} />
            </button>
        </div>

        <!-- Buscador -->
        <div class="relative w-full">
            <input
                type="text"
                bind:value={searchTerm}
                on:keydown={handleKeydown}
                placeholder="Buscar (ej. 'Juan 3:16' o 'Amor')..."
                class="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg border focus:outline-none focus:ring-1 focus:ring-indigo-500/50 transition-all {inputClass}"
            />
            <MagnifyingGlass
                size={14}
                class="absolute left-3 top-1/2 -translate-y-1/2 opacity-50 {textClass}"
            />
        </div>
    </div>

    <!-- Contenido Principal -->
    <div class="flex-1 overflow-y-auto p-6 relative">
        {#if loading}
            <div
                class="flex flex-col items-center justify-center h-full gap-3 opacity-60"
            >
                <div
                    class="animate-spin rounded-full h-8 w-8 border-b-2 {isLight
                        ? 'border-indigo-600'
                        : 'border-indigo-400'}"
                ></div>
                <span class="text-xs tracking-wider {subTextClass}"
                    >Consultando...</span
                >
            </div>
        {:else if error}
            <div
                class="flex flex-col items-center justify-center h-full text-center p-4"
            >
                <span class="text-amber-500 text-2xl mb-2">⚠️</span>
                <p class="text-sm {textClass}">{error}</p>
                <button
                    on:click={fetchBible}
                    class="mt-4 text-xs underline {subTextClass}"
                    >Recargar</button
                >
            </div>

            <!-- VISTA DE BÚSQUEDA -->
        {:else if isSearching}
            <h3
                class="text-xs metric tracking-widest uppercase mb-4 opacity-60 {textClass}"
            >
                Resultados para "{searchTerm}"
            </h3>
            <div class="space-y-3">
                {#each searchResults as result}
                    <button
                        on:click={() =>
                            fetchPassage(result.chapterId || result.id)}
                        class="w-full text-left p-3 rounded-lg border transition-all group {isLight
                            ? 'bg-white border-stone-200 hover:border-indigo-300'
                            : 'bg-white/5 border-white/5 hover:border-indigo-400/50'}"
                    >
                        <div class="flex items-center justify-between mb-1">
                            <span
                                class="font-bold text-sm {isLight
                                    ? 'text-indigo-700'
                                    : 'text-indigo-300'}"
                                >{result.reference}</span
                            >
                            <CaretRight
                                size={12}
                                class="opacity-0 group-hover:opacity-100 transition-opacity {subTextClass}"
                            />
                        </div>
                        <p
                            class="text-xs line-clamp-2 leading-relaxed opacity-80 {textClass}"
                        >
                            {result.text}
                        </p>
                    </button>
                {/each}
                {#if searchResults.length === 0}
                    <p class="text-sm text-center opacity-60 mt-10 {textClass}">
                        Sin resultados encontrados.
                    </p>
                {/if}
            </div>

            <!-- VISTA DE LECTURA -->
        {:else}
            <!-- Título del Pasaje -->
            <h2
                class="text-2xl font-serif font-bold mb-4 text-center {isLight
                    ? 'text-indigo-950'
                    : 'text-indigo-100'}"
            >
                {passageReference}
            </h2>

            <!-- Texto Bíblico (HTML inyectado) -->
            <div
                class="font-serif leading-relaxed text-lg text-justify {textClass} decoration-slice [&_span.v]:text-xs [&_span.v]:font-sans [&_span.v]:text-indigo-500 [&_span.v]:mr-1 [&_span.v]:relative [&_span.v]:-top-1"
            >
                {@html passageContent}
            </div>

            <div
                class="mt-8 text-center border-t pt-4 {isLight
                    ? 'border-stone-200'
                    : 'border-white/10'}"
            >
                <span
                    class="text-[10px] uppercase tracking-widest opacity-40 {textClass}"
                    >Soli Deo Gloria</span
                >
            </div>
        {/if}
    </div>

    <!-- Footer Decorativo -->
    <div
        class="h-1 w-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 opacity-30"
    ></div>
</div>

<style>
    /* Ajustes finos para el HTML de la API.Bible */
    :global(.p) {
        margin-bottom: 1rem;
    }
    :global(.q1, .q2) {
        margin-left: 1.5rem; /* Poesía indentada */
        font-style: italic;
    }
</style>
