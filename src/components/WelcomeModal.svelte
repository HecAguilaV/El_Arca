<script>
    import { fade, scale } from "svelte/transition";
    import { createEventDispatcher } from "svelte";
    import { User } from "phosphor-svelte";

    export let isLight = false;

    const dispatch = createEventDispatcher();
    let name = "";

    function handleSubmit() {
        if (!name.trim()) return;
        dispatch("save", name.trim());
    }

    function handleKeydown(e) {
        if (e.key === "Enter") handleSubmit();
    }
</script>

<div
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
    transition:fade
>
    <div
        class="w-full max-w-md p-8 rounded-xl shadow-2xl relative overflow-hidden transition-colors duration-300
        {isLight
            ? 'bg-[#fafaf9] text-stone-800'
            : 'bg-[#18181e] text-stone-200'}"
        transition:scale={{ start: 0.95 }}
    >
        <!-- Decorative Border -->
        <div
            class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-indigo-500 to-transparent opacity-50"
        ></div>

        <div class="text-center mb-8">
            <div
                class="mx-auto w-16 h-16 rounded-full flex items-center justify-center mb-4 {isLight
                    ? 'bg-stone-200'
                    : 'bg-white/5'}"
            >
                <User
                    size={32}
                    class={isLight ? "text-stone-500" : "text-stone-400"}
                    weight="duotone"
                />
            </div>

            <h2 class="text-2xl font-serif font-bold mb-2 tracking-tight">
                Bienvenido a bordo
            </h2>
            <p class="text-sm opacity-60 max-w-[260px] mx-auto leading-relaxed">
                Para personalizar su experiencia de estudio, indícame cómo te
                llamo
            </p>
        </div>

        <div class="space-y-6">
            <div class="relative group">
                <input
                    type="text"
                    bind:value={name}
                    on:keydown={handleKeydown}
                    placeholder="Su nombre..."
                    class="w-full px-4 py-3 text-center bg-transparent border-b-2 outline-none transition-all font-medium
                    {isLight
                        ? 'border-stone-300 focus:border-indigo-600 placeholder:text-stone-400'
                        : 'border-stone-700 focus:border-indigo-400 placeholder:text-stone-600'}"
                    autoFocus
                />
            </div>

            <button
                on:click={handleSubmit}
                disabled={!name.trim()}
                class="w-full py-3 px-4 rounded-lg font-medium text-sm tracking-wide transition-all duration-300 flex items-center justify-center gap-2
                {isLight
                    ? 'bg-stone-800 text-stone-200 hover:bg-stone-900 disabled:opacity-50 disabled:cursor-not-allowed'
                    : 'bg-stone-200 text-stone-900 hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed'}"
            >
                <span>COMENZAR ESTUDIO</span>
            </button>
        </div>
    </div>
</div>
