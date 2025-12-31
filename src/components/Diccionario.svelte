<script>
    import { api } from "../lib/api";
    import toast from "svelte-french-toast";

    export let esClaro = false;

    let termino = "";
    let definicion = "";
    let cargando = false;
    let perspectiva = "academico_global"; // Valor fijo interno para la API

    async function consultar() {
        if (!termino.trim()) return;
        cargando = true;
        definicion = "";
        try {
            const data = await api.diccionario.consultar(termino, perspectiva);
            definicion = data.definicion;
        } catch (e) {
            toast.error("Error al consultar el diccionario");
            console.error(e);
        } finally {
            cargando = false;
        }
    }

    function manejarTecla(e) {
        if (e.key === "Enter") consultar();
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
                >Hermenéutica</span
            >
            <span class="text-xs font-bold {claseTexto}"
                >Diccionario Teológico</span
            >
        </div>

            <input
                type="text"
                bind:value={termino}
                on:keydown={manejarTecla}
                placeholder="Concepto teológico..."
                class="w-full px-4 py-2 text-xs font-bold uppercase tracking-widest rounded border focus:outline-none focus:ring-1 focus:ring-indigo-500/50 transition-all {claseInput}"
            />
        </div>
    </div>

    <!-- Contenido -->
    <div class="flex-1 overflow-y-auto p-6 relative">
        {#if cargando}
            <div class="flex items-center justify-center h-full opacity-30">
                <span
                    class="text-[10px] uppercase font-bold tracking-[0.5em] animate-pulse"
                    >Analizando...</span
                >
            </div>
        {:else if definicion}
            <div
                class="prose prose-sm max-w-none {esClaro
                    ? 'prose-stone'
                    : 'prose-invert'}"
            >
                <div
                    class="font-serif leading-relaxed text-[15px] {claseTexto} whitespace-pre-wrap"
                >
                    {definicion}
                </div>
            </div>
        {:else}
            <div
                class="flex flex-col items-center justify-center h-full opacity-10 text-center px-10"
            >
                <span class="text-[40px] font-serif mb-4 italic">Lexicon</span>
                <p class="text-[10px] uppercase font-bold tracking-widest">
                    Ingrese un concepto doctrinal para consultar su definición
                    formal.
                </p>
            </div>
        {/if}
    </div>
</div>

<style>
    .scrollbar-hide::-webkit-scrollbar {
        display: none;
    }
    .scrollbar-hide {
        -ms-overflow-style: none;
        scrollbar-width: none;
    }
</style>
