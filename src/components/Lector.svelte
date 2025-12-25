<script>
    import { archivoAbierto } from "../lib/stores";

    export let esClaro = false;

    const API_BASE_URL =
        import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

    function cerrar() {
        archivoAbierto.set(null);
    }

    $: urlArchivo = $archivoAbierto
        ? `${API_BASE_URL}/libros/ver/${$archivoAbierto.ruta}`
        : "";
    $: claseContenedor = esClaro ? "bg-stone-200" : "bg-black/40";
</script>

{#if $archivoAbierto}
    <div
        class="flex flex-col h-full w-full {claseContenedor} animate-in fade-in zoom-in duration-300"
    >
        <!-- Barra de Herramientas del Visor -->
        <div
            class="flex-shrink-0 px-6 py-3 border-b {esClaro
                ? 'border-stone-300 bg-stone-100'
                : 'border-white/10 bg-black/20'} flex justify-between items-center"
        >
            <div class="flex flex-col overflow-hidden">
                <span
                    class="text-[9px] uppercase font-bold tracking-[0.2em] opacity-40 {esClaro
                        ? 'text-stone-800'
                        : 'text-slate-200'}">Lector de Documentos</span
                >
                <span
                    class="text-xs font-bold truncate {esClaro
                        ? 'text-stone-900'
                        : 'text-white'}"
                >
                    {$archivoAbierto.nombre}
                </span>
            </div>

            <button
                on:click={cerrar}
                class="px-4 py-1.5 rounded-lg text-[10px] uppercase font-bold tracking-widest border {esClaro
                    ? 'border-stone-300 text-stone-600 hover:bg-stone-200'
                    : 'border-white/10 text-slate-400 hover:bg-white/5'} transition-all"
            >
                Cerrar Visor
            </button>
        </div>

        <!-- Visor -->
        <div class="flex-1 w-full bg-white relative">
            {#if $archivoAbierto.formato === ".pdf"}
                <iframe
                    src="{urlArchivo}#toolbar=0"
                    title="Visor PDF"
                    class="w-full h-full border-none"
                ></iframe>
            {:else}
                <div
                    class="h-full flex flex-col items-center justify-center p-10 text-center"
                >
                    <div
                        class="text-[40px] font-serif mb-4 italic text-stone-300"
                    >
                        Formato No Soportado
                    </div>
                    <p
                        class="text-[10px] uppercase font-bold tracking-widest text-stone-400 mb-6"
                    >
                        El visor integrado solo admite archivos PDF actualmente.
                    </p>
                    <a
                        href={urlArchivo}
                        download
                        class="px-6 py-2 bg-indigo-600 text-white text-[11px] uppercase font-bold tracking-widest rounded-lg hover:bg-indigo-700 transition-all"
                    >
                        Descargar Manualmente
                    </a>
                </div>
            {/if}
        </div>
    </div>
{/if}
