<script>
    import { createEventDispatcher } from 'svelte';
    import { fade, scale } from 'svelte/transition';

    export let isOpen = false;
    export let title = "¿Estás seguro?";
    export let message = "Esta acción no se puede deshacer.";
    export let confirmText = "Confirmar";
    export let cancelText = "Cancelar";
    export let type = "danger"; // danger | info

    const dispatch = createEventDispatcher();

    function confirm() {
        dispatch('confirm');
    }

    function cancel() {
        dispatch('cancel');
    }
</script>

{#if isOpen}
    <div 
        class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        transition:fade={{ duration: 200 }}
    >
        <div 
            class="bg-[#1e1e24] border border-white/10 rounded-2xl shadow-2xl max-w-sm w-full p-6 relative overflow-hidden"
            transition:scale={{ duration: 200, start: 0.95 }}
        >
            <!-- Glow Effect -->
            <div class="absolute top-0 left-0 w-full h-1 {type === 'danger' ? 'bg-gradient-to-r from-red-500 to-orange-500' : 'bg-gradient-to-r from-indigo-500 to-cyan-500'}"></div>

            <h3 class="text-xl font-bold text-white mb-2">{title}</h3>
            <p class="text-slate-400 text-sm mb-6 leading-relaxed">
                {message}
            </p>

            <div class="flex justify-end gap-3">
                <button 
                    on:click={cancel}
                    class="px-4 py-2 rounded-xl text-sm font-medium text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
                >
                    {cancelText}
                </button>
                <button 
                    on:click={confirm}
                    class="px-4 py-2 rounded-xl text-sm font-medium text-white shadow-lg transition-transform active:scale-95
                    {type === 'danger' 
                        ? 'bg-red-600 hover:bg-red-500 shadow-red-500/20' 
                        : 'bg-indigo-600 hover:bg-indigo-500 shadow-indigo-500/20'}"
                >
                    {confirmText}
                </button>
            </div>
        </div>
    </div>
{/if}
