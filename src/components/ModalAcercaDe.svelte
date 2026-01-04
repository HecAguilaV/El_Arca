<script>
    import { fade, scale } from "svelte/transition";
    import { createEventDispatcher, onMount } from "svelte";
    import { X, Info, BookOpen } from "phosphor-svelte";
    import { parse } from "marked";

    export let esClaro = false;

    const dispatch = createEventDispatcher();
    let pestañaActiva = "bienvenida"; // "bienvenida" | "manual"
    let contenidoManual = "";
    let cargandoManual = false;

    function cerrar() {
        dispatch("close");
    }

    async function cargarManual() {
        if (contenidoManual) return; // Ya cargado
        cargandoManual = true;
        try {
            const res = await fetch("/manual.md");
            if (res.ok) {
                contenidoManual = await res.text();
            } else {
                contenidoManual = "No se pudo cargar el manual.";
            }
        } catch (e) {
            contenidoManual = "Error de conexión al cargar el manual.";
        } finally {
            cargandoManual = false;
        }
    }

    function cambiarPestaña(tab) {
        pestañaActiva = tab;
        if (tab === "manual") {
            cargarManual();
        }
    }
</script>

<div
    class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/90 backdrop-blur-sm"
    transition:fade
    on:click={cerrar}
>
    <!-- Contenido del Modal -->
    <div
        class="w-full max-w-4xl h-[90vh] flex flex-col rounded-2xl shadow-2xl relative overflow-hidden transition-colors duration-300 {esClaro
            ? 'bg-[#fafaf9] text-stone-800'
            : 'bg-[#18181e] text-stone-200'}"
        transition:scale={{ start: 0.95 }}
        on:click|stopPropagation
    >
        <!-- Decoración Superior -->
        <div
            class="absolute top-0 left-0 w-full h-1 bg-amber-500/50 z-10"
        ></div>

        <!-- Botón Cerrar -->
        <button
            on:click={cerrar}
            class="absolute top-4 right-4 p-2 rounded-full hover:bg-black/10 transition-colors opacity-50 hover:opacity-100 z-20"
        >
            <X size={20} />
        </button>

        <!-- Cabecera / Pestañas -->
        <div
            class="flex-none p-6 pb-0 border-b {esClaro
                ? 'border-stone-200'
                : 'border-white/5'}"
        >
            <h2
                class="text-xl font-black tracking-tighter uppercase mb-4 {esClaro
                    ? 'text-indigo-950'
                    : 'text-white'}"
            >
                Información del Sistema
            </h2>

            <div class="flex gap-6">
                <button
                    class="pb-3 text-xs font-bold tracking-widest uppercase transition-colors border-b-2 {pestañaActiva ===
                    'bienvenida'
                        ? 'border-amber-500 text-amber-500'
                        : 'border-transparent opacity-40 hover:opacity-100'}"
                    on:click={() => cambiarPestaña("bienvenida")}
                >
                    Bienvenida
                </button>
                <button
                    class="pb-3 text-xs font-bold tracking-widest uppercase transition-colors border-b-2 {pestañaActiva ===
                    'manual'
                        ? 'border-indigo-500 text-indigo-500'
                        : 'border-transparent opacity-40 hover:opacity-100'}"
                    on:click={() => cambiarPestaña("manual")}
                >
                    Manual de Usuario
                </button>
            </div>
        </div>

        <!-- Contenido Scrollable -->
        <div class="flex-1 overflow-y-auto p-8 custom-scrollbar">
            {#if pestañaActiva === "bienvenida"}
                <div
                    in:fade
                    class="prose prose-sm max-w-none text-justify {esClaro
                        ? 'prose-stone'
                        : 'prose-invert'} leading-relaxed opacity-90 mx-auto max-w-2xl"
                >
                    <h3
                        class="font-bold text-amber-500 text-center text-lg mb-6"
                    >
                        Saludo de Bienvenida
                    </h3>

                    <p>
                        A quienes lleguen a este rincón, quiero contarles que
                        esta idea nace de la necesidad de un lugar de <em
                            >inmersión</em
                        > en el estudio de la Palabra. Si bien el estudio tradicional
                        suele ser físico, hoy la digitalización nos permite llevar
                        esa experiencia a todas partes.
                    </p>

                    <p>
                        Inspirado por herramientas como <strong>Logos</strong> o
                        <strong>e-Sword</strong>, creé <strong>El Arca</strong>.
                        Es una biblioteca digital que comienza con
                        <strong>1,199 archivos</strong> recopilados a lo largo de
                        los años entre familiares y amigos, incluyendo libros, manualidades
                        y material teológico.
                    </p>

                    <p>
                        Actualmente, trabajo en indexar y etiquetar cada recurso
                        para que puedas relacionar temas fácilmente. Por ahora,
                        mi enfoque está en categorizar y renombrar correctamente
                        cada archivo para que tus búsquedas sean más precisas.
                    </p>

                    <p
                        class="font-medium text-center mt-8 text-amber-500 italic"
                    >
                        "Un soñador con poca RAM" 👨🏻‍💻
                    </p>
                </div>
            {:else}
                <div in:fade class="mx-auto max-w-3xl">
                    {#if cargandoManual}
                        <div class="flex justify-center py-20 opacity-50">
                            Cargando manual...
                        </div>
                    {:else}
                        <div
                            class="prose prose-sm max-w-none {esClaro
                                ? 'prose-stone'
                                : 'prose-invert'} prose-headings:font-bold prose-h1:text-indigo-500 prose-a:text-indigo-400"
                        >
                            {@html parse(contenidoManual)}
                        </div>
                    {/if}
                </div>
            {/if}
        </div>

        <!-- Footer -->
        <div
            class="flex-none p-4 border-t {esClaro
                ? 'border-stone-200'
                : 'border-white/5'} bg-opacity-50 text-center"
        >
            <div class="text-[10px] font-medium tracking-tight opacity-50">
                &copy; {new Date().getFullYear()} Héctor Aguila &bull; Desarrollado
                para el Servicio de Apoyo a la Iglesia
            </div>
        </div>
    </div>
</div>

<style>
    .custom-scrollbar::-webkit-scrollbar {
        width: 6px;
    }
    .custom-scrollbar::-webkit-scrollbar-track {
        background: transparent;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
        background: rgba(120, 113, 108, 0.2);
        border-radius: 10px;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
        background: rgba(120, 113, 108, 0.4);
    }
</style>
