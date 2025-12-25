<script>
    import { createEventDispatcher } from "svelte";
    import {
        Presentation,
        FilePdf,
        Book,
        Tag,
        User,
        Funnel,
    } from "phosphor-svelte";

    export let data = [];

    const dispatch = createEventDispatcher();

    // -- Procesar Datos --
    $: authors = extractTop(data, "author", 5); // Necesitaremos extraer autor del nombre si no hay campo
    $: categories = extractTop(data, "category");
    $: formats = extractTop(data, "format");
    $: tags = extractTags(data, 8);

    function extractTop(items, field, limit = 5) {
        const counts = items.reduce((acc, item) => {
            let val = item[field];
            // Intento básico de extraer autor del nombre si no hay campo explícito "author"
            // Asumiendo formato "Autor - Titulo" o similar si field == 'author'
            if (field === "author" && !val) {
                const parts = item.filename.split(" - ");
                if (parts.length > 1) val = parts[0];
                else return acc; // No autor detectable
            }

            if (val) {
                acc[val] = (acc[val] || 0) + 1;
            }
            return acc;
        }, {});

        return Object.entries(counts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, limit);
    }

    function extractTags(items, limit = 10) {
        const counts = items.reduce((acc, item) => {
            if (item.tags) {
                item.tags.split(", ").forEach((tag) => {
                    if (tag.trim()) {
                        acc[tag.trim()] = (acc[tag.trim()] || 0) + 1;
                    }
                });
            }
            return acc;
        }, {});
        return Object.entries(counts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, limit);
    }

    function handleFilter(type, value) {
        dispatch("filter", { type, value });
    }

    // Iconos por formato
    const icons = {
        pptx: Presentation,
        pdf: FilePdf,
        epub: Book,
        fisico: Book,
    };
</script>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
    <!-- Panel de Categorías -->
    <div
        class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-md flex flex-col"
    >
        <h3
            class="text-xs uppercase tracking-widest text-slate-400 mb-3 font-semibold flex items-center gap-2"
        >
            <Funnel size={14} /> Categorías
        </h3>
        <div class="space-y-2 overflow-y-auto max-h-40 scrollbar-hide">
            {#each categories as [cat, count]}
                <button
                    on:click={() => handleFilter("category", cat)}
                    class="w-full flex justify-between items-center text-sm text-slate-300 hover:text-indigo-400 hover:bg-white/5 p-1.5 rounded transition-colors group text-left"
                >
                    <span>{cat}</span>
                    <span
                        class="text-[10px] bg-white/10 px-1.5 py-0.5 rounded-full text-slate-500 group-hover:text-indigo-300"
                        >{count}</span
                    >
                </button>
            {/each}
        </div>
    </div>

    <!-- Panel de Autores (Detectados) -->
    <div
        class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-md flex flex-col"
    >
        <h3
            class="text-xs uppercase tracking-widest text-slate-400 mb-3 font-semibold flex items-center gap-2"
        >
            <User size={14} /> Autores Top
        </h3>
        <div class="space-y-2 overflow-y-auto max-h-40 scrollbar-hide">
            {#each authors as [auth, count]}
                <button
                    on:click={() => handleFilter("author", auth)}
                    class="w-full flex justify-between items-center text-sm text-slate-300 hover:text-emerald-400 hover:bg-white/5 p-1.5 rounded transition-colors group text-left"
                >
                    <span class="truncate pr-2">{auth}</span>
                    <span
                        class="text-[10px] bg-white/10 px-1.5 py-0.5 rounded-full text-slate-500 group-hover:text-emerald-300"
                        >{count}</span
                    >
                </button>
            {/each}
            {#if authors.length === 0}
                <div class="text-xs text-slate-600 italic py-2">
                    No se detectaron autores en los nombres de archivo.
                </div>
            {/if}
        </div>
    </div>

    <!-- Panel de Formatos -->
    <div
        class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-md flex flex-col"
    >
        <h3
            class="text-xs uppercase tracking-widest text-slate-400 mb-3 font-semibold flex items-center gap-2"
        >
            <Presentation size={14} /> Formatos
        </h3>
        <div class="space-y-2">
            {#each formats as [fmt, count]}
                <button
                    on:click={() => handleFilter("format", fmt)}
                    class="w-full flex justify-between items-center text-sm text-slate-300 hover:text-amber-400 hover:bg-white/5 p-1.5 rounded transition-colors group text-left"
                >
                    <span class="uppercase">{fmt}</span>
                    <span
                        class="text-[10px] bg-white/10 px-1.5 py-0.5 rounded-full text-slate-500 group-hover:text-amber-300"
                        >{count}</span
                    >
                </button>
            {/each}
        </div>
    </div>

    <!-- Panel de Etiquetas (Tags) -->
    <div
        class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-md flex flex-col"
    >
        <h3
            class="text-xs uppercase tracking-widest text-slate-400 mb-3 font-semibold flex items-center gap-2"
        >
            <Tag size={14} /> Temas (Tags)
        </h3>
        <div
            class="flex flex-wrap gap-2 overflow-y-auto max-h-40 scrollbar-hide content-start"
        >
            {#each tags as [tag, count]}
                <button
                    on:click={() => handleFilter("tag", tag)}
                    class="text-xs px-2 py-1 rounded border border-white/5 bg-white/5 text-slate-400 hover:text-white hover:border-indigo-500/50 hover:bg-indigo-500/20 transition-all"
                >
                    #{tag}
                </button>
            {/each}
        </div>
    </div>
</div>
