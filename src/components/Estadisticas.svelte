<script>
    export let datos = [];
    export let esClaro = false;

    $: esBibliotecaFisica = datos.length > 0 && "isbn" in datos[0];

    // Conteo de etiquetas / temas
    $: conteoTemas = datos.reduce((acc, item) => {
        const etiquetas = esBibliotecaFisica
            ? item.notas || ""
            : item.etiquetas || "";
        if (etiquetas) {
            etiquetas.split(/[ ,]+/).forEach((et) => {
                const limpia = et.trim().replace(/[.,]/g, "");
                if (limpia.length > 3) acc[limpia] = (acc[limpia] || 0) + 1;
            });
        }
        return acc;
    }, {});

    $: temasOrdenados = Object.entries(conteoTemas)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);

    $: totalPrimario = esBibliotecaFisica
        ? datos.filter((d) => d.ubicacion).length
        : datos.filter((d) => d.categoria === "Seminario").length;

    $: totalSecundario = esBibliotecaFisica
        ? datos.filter((d) => !d.ubicacion).length
        : datos.filter((d) => d.categoria === "Digital").length;

    $: totalTerciario = esBibliotecaFisica
        ? datos.length
        : datos.filter((d) => d.categoria === "Escuela Dominical").length;

    $: etiquetaPrimaria = esBibliotecaFisica ? "Ubicados" : "Seminario";
    $: etiquetaSecundaria = esBibliotecaFisica ? "Sin Ubicar" : "Digital";
    $: etiquetaTerciaria = esBibliotecaFisica ? "Total" : "E. Dominical";
    $: tituloSeccion = esBibliotecaFisica
        ? "Biblioteca Física"
        : "Acervo Total";

    $: claseTarjeta = esClaro
        ? "bg-[#fafaf9] border-stone-300 shadow-sm"
        : "bg-white/5 border-white/10";
    $: claseEtiqueta = esClaro ? "text-stone-500" : "text-slate-400";
    $: claseTexto = esClaro ? "text-stone-700" : "text-slate-300";
    $: gradienteNumero = esClaro
        ? "from-stone-800 to-indigo-700"
        : "from-white to-indigo-300";
    $: fondoBarra = esClaro ? "bg-stone-200" : "bg-white/10";
</script>

<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
    <!-- Resumen -->
    <div
        class="{claseTarjeta} border rounded-xl p-8 transition-colors duration-500"
    >
        <div class="flex justify-between items-center mb-6">
            <h3
                class="text-[9px] uppercase tracking-[0.3em] {claseEtiqueta} font-bold"
            >
                {tituloSeccion}
            </h3>
            {#if !esBibliotecaFisica}
                <button
                    on:click={async () => {
                        const { api } = await import("../lib/api");
                        const { cargarTodo } = await import("../lib/stores");
                        try {
                            import("svelte-french-toast").then((t) =>
                                t.default.loading("Conectando con Drive...", {
                                    duration: 2000,
                                }),
                            );
                            await api.libros.sincronizarDrive();
                            import("svelte-french-toast").then((t) =>
                                t.default.success(
                                    "Sincronización rápida iniciada. Los libros aparecerán en breve.",
                                ),
                            );
                            setTimeout(cargarTodo, 3000);
                        } catch (e) {
                            import("svelte-french-toast").then((t) =>
                                t.default.error(
                                    "Error: Acceso denegado o Drive no configurada",
                                ),
                            );
                        }
                    }}
                    class="text-[10px] uppercase font-bold tracking-widest px-4 py-2 border rounded-lg {esClaro
                        ? 'border-indigo-200 bg-indigo-50 text-indigo-700 hover:bg-indigo-100'
                        : 'border-indigo-500/30 bg-indigo-500/10 text-indigo-300 hover:bg-indigo-500/20'} transition-all shadow-sm"
                >
                    ☁️ Sincronizar Drive
                </button>
            {/if}
        </div>
        <p
            class="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-br {gradienteNumero}"
        >
            {datos.length}
        </p>
        <div class="grid grid-cols-3 gap-4 mt-8">
            <div class="flex flex-col">
                <span
                    class="text-[10px] uppercase font-bold tracking-widest opacity-40 mb-1"
                    >{etiquetaPrimaria}</span
                >
                <span class="text-sm font-bold">{totalPrimario}</span>
            </div>
            <div class="flex flex-col">
                <span
                    class="text-[10px] uppercase font-bold tracking-widest opacity-40 mb-1"
                    >{etiquetaSecundaria}</span
                >
                <span class="text-sm font-bold">{totalSecundario}</span>
            </div>
            <div class="flex flex-col">
                <span
                    class="text-[10px] uppercase font-bold tracking-widest opacity-40 mb-1"
                    >{etiquetaTerciaria}</span
                >
                <span class="text-sm font-bold">{totalTerciario}</span>
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
            Temáticas / Etiquetas
        </h3>
        <div class="space-y-4">
            {#each temasOrdenados as [nombre, total]}
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
                            style="width: {(total / temasOrdenados[0][1]) *
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
