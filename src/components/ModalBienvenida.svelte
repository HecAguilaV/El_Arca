<script>
    import { fade, scale } from "svelte/transition";
    import { createEventDispatcher } from "svelte";
    import { loginWithGoogle } from "../lib/firebase";
    import toast from "svelte-french-toast";

    export let esClaro = false;

    const dispatch = createEventDispatcher();

    async function manejarLoginGoogle() {
        try {
            await loginWithGoogle();
        } catch (e) {
            toast.error("Error al iniciar con Google");
        }
    }
</script>

<div
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md"
    transition:fade
>
    <div
        class="w-full max-w-md p-10 rounded-xl shadow-2xl relative overflow-hidden transition-colors duration-300 {esClaro
            ? 'bg-[#fafaf9] text-stone-800'
            : 'bg-[#18181e] text-stone-200'}"
        transition:scale={{ start: 0.95 }}
    >
        <div class="absolute top-0 left-0 w-full h-1 bg-indigo-600/30"></div>

        <div class="text-center mb-10">
            <h2
                class="text-3xl font-black mb-4 tracking-tighter uppercase {esClaro
                    ? 'text-indigo-950'
                    : 'text-white'}"
            >
                Bienvenido a El Arca
            </h2>
            <p
                class="text-[10px] uppercase font-bold tracking-[0.2em] {esClaro
                    ? 'text-stone-600 opacity-80'
                    : 'text-stone-300 opacity-70'} max-w-[280px] mx-auto leading-relaxed"
            >
                Biblioteca Digital Privada
            </p>
        </div>

        <div class="space-y-6">
            <button
                on:click={manejarLoginGoogle}
                class="w-full py-4 px-6 bg-white hover:bg-gray-50 text-gray-900 font-bold rounded-lg border border-gray-200 flex items-center justify-center gap-3 transition-all transform hover:scale-[1.02] active:scale-95 shadow-lg group"
            >
                <svg
                    class="w-5 h-5"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <path
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                        fill="#4285F4"
                    />
                    <path
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                        fill="#34A853"
                    />
                    <path
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                        fill="#FBBC05"
                    />
                    <path
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                        fill="#EA4335"
                    />
                </svg>
                <span>Acceder con Google</span>
            </button>
        </div>

        <div class="mt-8 text-center">
            <p class="text-xs opacity-40">v2.1.0 - Acceso Restringido</p>
        </div>
    </div>
</div>
