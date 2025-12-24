<script>
    import { onMount } from "svelte";
    import { aiService } from "../lib/gemini";

    let messages = [];
    let input = "";
    let isLoading = false;
    let selectedPersona = "neofito";

    // Referencia al chat para auto-scroll
    let chatContainer;

    function scrollToBottom() {
        setTimeout(() => {
            if (chatContainer)
                chatContainer.scrollTop = chatContainer.scrollHeight;
        }, 100);
    }

    async function send() {
        if (!input.trim() || isLoading) return;

        const userMsg = { role: "user", text: input };
        messages = [...messages, userMsg];
        const question = input;
        input = "";
        isLoading = true;
        scrollToBottom();

        try {
            const context = localStorage.getItem("arca_notebook_content") || "";
            const response = await aiService.sendMessage(
                question,
                selectedPersona,
                context,
            );
            messages = [...messages, { role: "model", text: response }];
        } catch (error) {
            messages = [
                ...messages,
                { role: "error", text: `Error: ${error.message}` },
            ];
            if (error.message === "API_KEY_MISSING") {
                messages = [
                    ...messages,
                    {
                        role: "error",
                        text: "Error de Configuración: Contacte al administrador (API Key no encontrada).",
                    },
                ];
            } else {
                messages = [
                    ...messages,
                    { role: "error", text: `Error: ${error.message}` },
                ];
            }
        } finally {
            isLoading = false;
            scrollToBottom();
        }
    }

    // Mapa de nombres bonitos para la UI
    const labels = {
        neofito: "🌱 Neófito (Básico)",
        puritano: "🎩 Puritano",
        reformado: "🏰 Reformado",
        bautista: "💧 Bautista",
        pentecostal: "🔥 Pentecostal",
        academico: "🎓 Académico",
        pastoral: "❤️ Pastoral",
    };
</script>

<div
    class="flex flex-col h-full bg-[#1a1a20] rounded-xl border border-white/10 overflow-hidden relative"
>
    <!-- Header del Asistente -->
    <div
        class="flex items-center justify-between p-3 border-b border-white/10 bg-black/20"
    >
        <div class="flex items-center gap-3">
            <!-- Icono Mejorado: Pergamino Antiguo -->
            <div
                class="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30"
            >
                <span class="text-lg">📜</span>
            </div>
            <div class="flex flex-col">
                <span class="text-sm font-bold text-slate-200"
                    >Consejero Teológico</span
                >
                <span
                    class="text-[10px] text-emerald-400 font-mono flex items-center gap-1"
                >
                    <span
                        class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"
                    ></span>
                    Online
                </span>
            </div>
        </div>
    </div>

    <!-- Selector de Persona -->
    <div
        class="p-2 bg-white/5 border-b border-white/10 flex gap-2 overflow-x-auto scrollbar-hide"
    >
        {#each Object.keys(labels) as persona}
            <button
                on:click={() => (selectedPersona = persona)}
                class="px-3 py-1.5 rounded-lg text-xs font-medium border transition-all whitespace-nowrap flex items-center gap-1
                {selectedPersona === persona
                    ? 'bg-indigo-600 text-white border-indigo-500 shadow-md'
                    : 'border-transparent bg-black/20 text-slate-400 hover:bg-white/10 hover:text-white'}"
            >
                {labels[persona]}
            </button>
        {/each}
    </div>

    <!-- Chat Area -->
    <div
        class="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth"
        bind:this={chatContainer}
    >
        {#if messages.length === 0}
            <div
                class="flex flex-col items-center justify-center h-full text-slate-600 text-center opacity-60"
            >
                <span class="text-4xl mb-3 grayscale opacity-50">🕊️</span>
                <p class="text-sm font-medium text-slate-400">
                    Paz sea contigo.
                </p>
                <p class="text-xs mt-1">
                    Selecciona un enfoque y haz tu pregunta.
                </p>
            </div>
        {/if}

        {#each messages as msg}
            <div
                class="flex flex-col {msg.role === 'user'
                    ? 'items-end'
                    : 'items-start'} animate-in fade-in slide-in-from-bottom-2 duration-300"
            >
                <div
                    class="max-w-[85%] rounded-2xl p-3.5 text-sm shadow-sm
                    {msg.role === 'user'
                        ? 'bg-indigo-600 text-white rounded-br-none'
                        : msg.role === 'error'
                          ? 'bg-red-900/50 text-red-100 border border-red-500/30'
                          : 'bg-white/10 text-slate-200 rounded-bl-none border border-white/5'}"
                >
                    {@html msg.text.replace(/\n/g, "<br>")}
                </div>
                <span class="text-[10px] text-slate-600 mt-1 px-1 font-medium">
                    {msg.role === "user" ? "Tú" : "Consejero"}
                </span>
            </div>
        {/each}

        {#if isLoading}
            <div class="flex items-start">
                <div
                    class="bg-white/5 rounded-2xl rounded-bl-none p-4 text-sm flex gap-2 items-center"
                >
                    <span
                        class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce"
                    ></span>
                    <span
                        class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce delay-100"
                    ></span>
                    <span
                        class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce delay-200"
                    ></span>
                </div>
            </div>
        {/if}
    </div>

    <!-- Input Area -->
    <div class="p-3 bg-black/20 border-t border-white/10 backdrop-blur-md">
        <form on:submit|preventDefault={send} class="flex gap-2">
            <input
                type="text"
                bind:value={input}
                placeholder="Escribe tu duda teológica..."
                class="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:bg-white/10 transition-all shadow-inner"
                disabled={isLoading}
            />
            <button
                type="submit"
                disabled={isLoading || !input.trim()}
                class="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl transition-all font-medium shadow-lg shadow-indigo-500/20 hover:scale-105 active:scale-95"
            >
                <span class="text-base">➤</span>
            </button>
        </form>
    </div>
</div>
