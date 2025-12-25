<script>
    export let data = [];
    export let isLight = false;

    // Conteo de etiquetas
    $: conteoEtiquetas = data.reduce((acc, item) => {
        if (item.etiquetas) {
            item.etiquetas.split(",").forEach((et) => {
                const limpia = et.trim();
                if (limpia) acc[limpia] = (acc[limpia] || 0) + 1;
            });
        }
        return acc;
    }, {});

    $: etiquetasOrdenadas = Object.entries(conteoEtiquetas)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);

    $: totalSeminario = data.filter((d) => d.categoria === "Seminario").length;
    $: totalDigital = data.filter((d) => d.formato !== "físico").length;
    $: totalEscuela = data.filter(
        (d) => d.categoria === "Escuela Dominical",
    ).length;

    $: claseTarjeta = isLight
        ? "bg-[#fafaf9] border-stone-300 shadow-sm"
        : "bg-white/5 border-white/10";
    $: claseEtiqueta = isLight ? "text-stone-500" : "text-slate-400";
    $: claseTexto = isLight ? "text-stone-700" : "text-slate-300";
    $: gradienteNumero = isLight
        ? "from-stone-800 to-indigo-700"
        : "from-white to-indigo-300";
    $: fondoBarra = isLight ? "bg-stone-200" : "bg-white/10";
</script>

<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
    <!-- Resumen -->
    <div
        class="{claseTarjeta} border rounded-xl p-8 transition-colors duration-500"
    >
        <h3
            class="text-[9px] uppercase tracking-[0.3em] {claseEtiqueta} mb-6 font-bold"
        >
            Acervo Total
        </h3>
        <p
            class="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-br {gradienteNumero}"
        >
            {data.length}
        </p>
        <div class="grid grid-cols-3 gap-4 mt-8">
            <div class="flex flex-col">
                <span
                    class="text-[10px] uppercase font-bold tracking-widest opacity-40 mb-1"
                    >Seminario</span
                >
                <span class="text-sm font-bold">{totalSeminario}</span>
            </div>
            <div class="flex flex-col">
                <span
                    class="text-[10px] uppercase font-bold tracking-widest opacity-40 mb-1"
                    >Digital</span
                >
                <span class="text-sm font-bold">{totalDigital}</span>
            </div>
            <div class="flex flex-col">
                <span
                    class="text-[10px] uppercase font-bold tracking-widest opacity-40 mb-1"
                    >E. Dominical</span
                >
                <span class="text-sm font-bold">{totalEscuela}</span>
            </div>
        </div>
    </div>

    <!-- Tendencias -->
    <div
        class="{claseTarjeta} border rounded-xl p-8 transition-colors duration-500"
    >
        <h3
            class="text-[9px] uppercase tracking-[0.3em] {claseEtiqueta} mb-6 font-bold"
        >
            Ejes Temáticos
        </h3>
        <div class="space-y-4">
            {#each etiquetasOrdenadas as [nombre, total]}
                <div class="flex items-center gap-4 group">
                    <span
                        class="w-28 text-[11px] uppercase font-bold tracking-widest {claseTexto} shrink-0 truncate"
                        >{nombre}</span
                    >
                    <div
                        class="flex-1 h-1.5 {fondoBarra} rounded-full overflow-hidden"
                    >
                        <div
                            class="h-full bg-indigo-500 transition-all duration-700 group-hover:bg-indigo-400"
                            style="width: {(total / etiquetasOrdenadas[0][1]) *
                                100}%"
                        ></div>
                    </div>
                    <span
                        class="w-8 text-right text-[10px] font-mono opacity-50"
                        >{total}</span
                    >
                </div>
            {/each}
        </div>
    </div>
</div>
