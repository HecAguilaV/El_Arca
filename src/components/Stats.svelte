<script>
    export let data = [];
    export let isLight = false;

    // Extraer todas las etiquetas y contarlas
    $: tagCounts = data.reduce((acc, item) => {
        if (item.tags) {
            item.tags.split(", ").forEach((k) => {
                if (k) acc[k] = (acc[k] || 0) + 1;
            });
        }
        return acc;
    }, {});

    $: sortedTags = Object.entries(tagCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5); // Top 5

    $: totalSeminary = data.filter((d) => d.category === "Seminario").length;
    $: totalPhysical = data.filter((d) => d.format === "fisico").length;
    $: totalSchool = data.filter(
        (d) => d.category === "Escuela Dominical",
    ).length;

    // Clases dinámicas
    $: cardClass = isLight
        ? "bg-[#fafaf9] border-stone-300 shadow-sm"
        : "bg-white/5 border-white/10";

    $: labelClass = isLight ? "text-stone-500" : "text-slate-400";
    $: textClass = isLight ? "text-stone-700" : "text-slate-300";
    $: numberGradient = isLight
        ? "from-stone-800 to-indigo-700"
        : "from-white to-indigo-300";
    $: barBg = isLight ? "bg-stone-200" : "bg-white/10";
</script>

<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
    <!-- Card: Resumen General -->
    <div
        class="{cardClass} border rounded-xl p-6 transition-colors duration-500"
    >
        <h3
            class="text-xs uppercase tracking-widest {labelClass} mb-4 font-semibold"
        >
            Total Documentos
        </h3>
        <p
            class="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-br {numberGradient}"
        >
            {data.length}
        </p>
        <div class="flex flex-wrap gap-4 mt-4 text-sm {textClass}">
            <div class="flex items-center gap-2">
                <span class="opacity-80">📜</span>
                {totalSeminary} Seminario
            </div>
            <div class="flex items-center gap-2">
                <span class="opacity-80">📖</span>
                {totalPhysical} Físicos
            </div>
            <div class="flex items-center gap-2">
                <span class="opacity-80">🎈</span>
                {totalSchool} E. Dominical
            </div>
        </div>
    </div>

    <!-- Card: Top Tags -->
    <div
        class="{cardClass} border rounded-xl p-6 transition-colors duration-500"
    >
        <h3
            class="text-xs uppercase tracking-widest {labelClass} mb-4 font-semibold"
        >
            Tendencia de Contenido
        </h3>
        <div class="space-y-3">
            {#each sortedTags as [key, count]}
                <div class="flex items-center gap-3 group">
                    <span class="w-24 text-sm {textClass} shrink-0 truncate"
                        >{key}</span
                    >
                    <div
                        class="flex-1 h-2 {barBg} rounded-full overflow-hidden"
                    >
                        <div
                            class="h-full bg-indigo-500 rounded-full transition-all duration-500 group-hover:bg-indigo-400"
                            style="width: {(count / sortedTags[0][1]) * 100}%"
                        ></div>
                    </div>
                    <span
                        class="w-8 text-right text-xs opacity-60 font-mono {textClass}"
                        >{count}</span
                    >
                </div>
            {/each}
        </div>
    </div>
</div>
