<script>
    import { fade, scale } from "svelte/transition";
    import { createEventDispatcher } from "svelte";

    export let isLight = false;

    const dispatch = createEventDispatcher();
    let nombre = "";

    function manejarEnvio() {
        if (!nombre.trim()) return;
        dispatch("save", nombre.trim());
    }

    function manejarTecla(e) {
        if (e.key === "Enter") manejarEnvio();
    }
</script>

<div
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md"
    transition:fade
>
    <div
        class="w-full max-w-md p-10 rounded-xl shadow-2xl relative overflow-hidden transition-colors duration-300 {isLight
            ? 'bg-[#fafaf9] text-stone-800'
            : 'bg-[#18181e] text-stone-200'}"
        transition:scale={{ start: 0.95 }}
    >
        <div class="absolute top-0 left-0 w-full h-1 bg-indigo-600/30"></div>

        <div class="text-center mb-10">
            <h2 class="text-3xl font-bold mb-4 tracking-tighter uppercase">
                Identificación
            </h2>
            <p
                class="text-[10px] uppercase font-bold tracking-[0.2em] opacity-40 max-w-[280px] mx-auto leading-relaxed"
            >
                Establezca su perfil de investigador para la personalización de
                la biblioteca y el cuaderno.
            </p>
        </div>

        <div class="space-y-8">
            <div class="relative group">
                <input
                    type="text"
                    bind:value={nombre}
                    on:keydown={manejarTecla}
                    placeholder="Nombre del Investigador"
                    class="w-full px-4 py-4 text-center bg-transparent border-b border-stone-700/30 focus:border-indigo-600 outline-none transition-all font-bold text-lg uppercase tracking-widest {isLight
                        ? 'placeholder-stone-300'
                        : 'placeholder-stone-800'}"
                    autoFocus
                />
            </div>

            <button
                on:click={manejarEnvio}
                disabled={!nombre.trim()}
                class="w-full py-4 px-6 border {isLight
                    ? 'border-stone-800 text-stone-800 hover:bg-stone-800 hover:text-white'
                    : 'border-white/20 text-white hover:bg-white hover:text-black'} text-[10px] uppercase font-bold tracking-[0.3em] transition-all disabled:opacity-20 disabled:cursor-not-allowed"
            >
                Iniciar Sesión de Estudio
            </button>
        </div>
    </div>
</div>
