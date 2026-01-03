<script>
    import { fade, scale } from "svelte/transition";
    import { createEventDispatcher } from "svelte";
    import { loginWithGoogle } from "../lib/firebase";
    import toast from "svelte-french-toast";

    export let esClaro = false;

    async function manejarLoginGoogle() {
        try {
            await loginWithGoogle();
            // App.svelte detectará el cambio de auth y cerrará el modal
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
                    />
                    <path
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                        fill="#EA4335"
                    />
                </svg>
                <span class="text-sm font-bold tracking-wide uppercase"
                    >Continuar con Google</span
                >
            </button>

            <!-- Separador -->
            <div class="flex items-center gap-4 opacity-30">
                <div class="h-px bg-current flex-1"></div>
                <span class="text-[9px] uppercase tracking-widest"
                    >O prefiere</span
                >
                <div class="h-px bg-current flex-1"></div>
            </div>

            <!-- Opción 2: Invitado (Secundaria) -->
            <div class="text-center">
                <button
                    on:click={manejarInvitado}
                    class="text-[10px] uppercase font-bold tracking-[0.2em] opacity-50 hover:opacity-100 transition-opacity border-b border-transparent hover:border-current pb-1"
                >
                    Continuar como Invitado (Sin Sincronización)
                </button>
                <p
                    class="text-[9px] mt-3 opacity-30 max-w-[260px] mx-auto leading-relaxed"
                >
                    ⚠️ Modo Invitado: Las notas se guardan solo en este
                    navegador. Si borras cookies o cambias de dispositivo, se
                    perderán.
                </p>
            </div>
        </div>
    </div>
</div>
