<script>
    import { onMount, tick } from "svelte";
    import { aiService } from "../lib/gemini";
    import { scale, fade, slide } from "svelte/transition";
    import toast from "svelte-french-toast";
    import {
        PaperPlaneRight,
        ChalkboardTeacher,
        User,
        Trash,
        WarningCircle,
        ChatCircleText,
    } from "phosphor-svelte";

    // ... (previous imports)

    export let isLight = false; // Prop recibida desde App.svelte

    let messages = [];
    let userInput = "";
    let isLoading = false;
    let chatContainer;
    let showConfig = false;

    // Mapa de nombres bonitos para la UI
    const personaLabels = {
        reformado: "Teólogo Reformado",
        puritano: "Puritano Clásico",
        bautista: "Bautista (1689)",
        pentecostal: "Pentecostal",
        academico: "Erudito Bíblico",
        pastoral: "Consejero Pastoral",
        neofito: "Mentor Básico",
    };

    // Cargar historial
    onMount(() => {
        const saved = localStorage.getItem("arca_chat_history");
        if (saved) messages = JSON.parse(saved);

        // Verificar API Key al inicio (silencioso)
        if (!aiService.apiKey) {
            messages = [
                ...messages,
                {
                    role: "system",
                    text: "⚠️ El sistema de IA no está configurado. Contacte al administrador.",
                },
            ];
        }
    });

    async function scrollToBottom() {
        await tick();
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    async function sendMessage() {
        if (!userInput.trim() || isLoading) return;

        if (!aiService.apiKey) {
            toast.error("Error de Configuración: API Key no encontrada.", {
                style: "background: #1e1e24; color: #fff; border: 1px solid #ef4444;",
            });
            return;
        }

        const text = userInput;
        userInput = ""; // Limpiar input inmediatamente
        isLoading = true;

        // Usuario
        messages = [...messages, { role: "user", text }];
        scrollToBottom();

        try {
            // LLamada a Gemini con la persona seleccionada
            const response = await aiService.sendMessage(text, currentPersona);

            // Respuesta IA
            messages = [...messages, { role: "model", text: response }];
            saveHistory();
        } catch (error) {
            console.error(error);
            messages = [
                ...messages,
                {
                    role: "error",
                    text: "Lo siento, hubo un error al conectar con el servicio de teología. Por favor revisa tu conexión.",
                },
            ];
        } finally {
            isLoading = false;
            scrollToBottom();
        }
    }

    function saveHistory() {
        localStorage.setItem("arca_chat_history", JSON.stringify(messages));
    }

    function clearHistory() {
        if (confirm("¿Borrar toda la conversación?")) {
            messages = [];
            localStorage.removeItem("arca_chat_history");
            toast.success("Historial borrado");
        }
    }

    function handleKeydown(e) {
        // Permitir Enter normal para salto de línea, NO enviar.
        return;
    }

    // ... (inside div wrapper) ...
    function setPersona(p) {
        aiService.setPersona(p);
        toast.success(`Modo: ${personaLabels[p]}`);
        showConfig = false;
    }
</script>

<div
    class="flex flex-col h-full {isLight
        ? 'bg-white'
        : 'bg-[#0f0f13]'} relative overflow-hidden transition-colors duration-500"
>
    <!-- Header del Chat -->
    <div
        class="flex items-center justify-between p-4 border-b {isLight
            ? 'border-slate-200 bg-slate-50'
            : 'border-white/5 bg-[#14141a]'}"
    >
        <div class="flex items-center gap-3">
            <!-- Icon Container -->
            <div
                class="w-10 h-10 rounded-lg flex items-center justify-center border {isLight
                    ? 'bg-indigo-100 border-indigo-200'
                    : 'bg-indigo-900/30 border-indigo-500/20'}"
            >
                <ChalkboardTeacher
                    size={24}
                    class={isLight ? "text-indigo-700" : "text-indigo-400"}
                />
            </div>
            <div>
                <h2
                    class="text-sm font-bold leading-tight {isLight
                        ? 'text-slate-800'
                        : 'text-slate-200'}"
                >
                    Asistente Teológico
                </h2>
                <!-- ... Status ... -->
            </div>
        </div>

        <div class="flex items-center gap-2">
            <button
                on:click={clearHistory}
                class="p-2 rounded-lg transition-colors {isLight
                    ? 'text-slate-400 hover:text-red-600 hover:bg-slate-200'
                    : 'text-slate-500 hover:text-red-400 hover:bg-white/5'}"
                title="Borrar Historial"
            >
                <Trash size={18} />
            </button>
            <button
                on:click={() => (showConfig = !showConfig)}
                class="p-2 rounded-lg transition-colors {isLight
                    ? 'text-slate-400 hover:text-indigo-600 hover:bg-slate-200'
                    : 'text-slate-500 hover:text-indigo-400 hover:bg-white/5'} {showConfig
                    ? isLight
                        ? 'text-indigo-600 bg-slate-200'
                        : 'text-indigo-400 bg-white/5'
                    : ''}"
                title="Cambiar Especialista"
            >
                <ChatCircleText size={18} />
            </button>
        </div>
    </div>

    <!-- Configuración de Persona (Dropdown) -->
    {#if showConfig}
        <div
            transition:slide={{ duration: 200 }}
            class="border-b p-4 z-10 shadow-xl {isLight
                ? 'bg-white border-slate-200'
                : 'bg-[#1a1a20] border-white/5'}"
        >
            <h3
                class="text-xs font-bold uppercase tracking-widest mb-3 {isLight
                    ? 'text-slate-500'
                    : 'text-slate-400'}"
            >
                Seleccionar Enfoque Teológico
            </h3>
            <div class="grid grid-cols-2 gap-2">
                {#each Object.entries(personaLabels) as [key, label]}
                    <button
                        on:click={() => setPersona(key)}
                        class="text-left px-3 py-2 rounded-lg text-xs font-medium border transition-all
                        {aiService.currentPersona === key
                            ? isLight
                                ? 'bg-indigo-50 border-indigo-200 text-indigo-700'
                                : 'bg-indigo-600/20 border-indigo-500/50 text-indigo-300'
                            : isLight
                              ? 'border-slate-100 bg-slate-50 text-slate-600 hover:bg-slate-100'
                              : 'border-white/5 hover:bg-white/5 text-slate-400 hover:text-slate-200'}"
                    >
                        {label}
                    </button>
                {/each}
            </div>
        </div>
    {/if}

    <!-- Area de Mensajes -->
    <div
        bind:this={chatContainer}
        class="flex-1 overflow-y-auto p-4 space-y-6 scroll-smooth"
    >
        {#if messages.length === 0}
            <div
                in:fade
                class="h-full flex flex-col items-center justify-center text-center p-8 opacity-50"
            >
                <ChalkboardTeacher
                    size={48}
                    class="{isLight ? 'text-slate-300' : 'text-slate-600'} mb-4"
                />
                <p
                    class="{isLight
                        ? 'text-slate-400'
                        : 'text-slate-500'} text-sm max-w-[250px]"
                >
                    Hola. Soy tu asistente de investigación. ¿En qué tema
                    teológico estás trabajando hoy?
                </p>
            </div>
        {/if}

        {#each messages as msg}
            <div
                class="flex gap-4 {msg.role === 'user'
                    ? 'flex-row-reverse'
                    : ''}"
                in:scale={{ duration: 200, start: 0.95 }}
            >
                <!-- Avatar -->
                <div
                    class="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold shadow-lg
          {msg.role === 'user'
                        ? isLight
                            ? 'bg-indigo-600 text-white'
                            : 'bg-indigo-900/50 text-indigo-200 ring-1 ring-indigo-500/30'
                        : msg.role === 'error'
                          ? 'bg-red-500 text-white'
                          : isLight
                            ? 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                            : 'bg-emerald-900/30 text-emerald-300 ring-1 ring-emerald-500/20'}"
                >
                    {#if msg.role === "user"}
                        <User size={14} />
                    {:else if msg.role === "error"}
                        <WarningCircle size={14} />
                    {:else}
                        <ChalkboardTeacher size={14} />
                    {/if}
                </div>

                <!-- Burbuja de Texto -->
                <div
                    class="max-w-[85%] rounded-2xl px-5 py-3.5 text-sm leading-relaxed shadow-sm
          {msg.role === 'user'
                        ? (isLight
                              ? 'bg-indigo-600 text-white border-indigo-700'
                              : 'bg-[#1e1e28] text-indigo-100/90 border-indigo-500/10') +
                          ' rounded-tr-sm border'
                        : msg.role === 'error'
                          ? 'bg-red-50 border-red-200 text-red-700'
                          : (isLight
                                ? 'bg-white text-slate-700 border-slate-200'
                                : 'bg-[#18181e] text-slate-300 border-white/5') +
                            ' rounded-tl-sm border font-serif'}"
                >
                    {@html window.marked?.parse(msg.text) || msg.text}
                </div>
            </div>
        {/each}

        <!-- Loading State -->
        {#if isLoading}
            <!-- ... (Adjust loading colors similarly) ... -->
            <div class="flex gap-4" in:fade>
                <div
                    class="w-8 h-8 rounded-full flex items-center justify-center {isLight
                        ? 'bg-emerald-50'
                        : 'bg-emerald-900/30 ring-1 ring-emerald-500/20'}"
                >
                    <ChalkboardTeacher
                        size={14}
                        class="{isLight
                            ? 'text-emerald-500'
                            : 'text-emerald-300'} animate-pulse"
                    />
                </div>
                <div
                    class="px-4 py-3 rounded-2xl rounded-tl-sm flex gap-1 items-center border {isLight
                        ? 'bg-white border-slate-200'
                        : 'bg-[#18181e] border-white/5'}"
                >
                    <div
                        class="w-1.5 h-1.5 {isLight
                            ? 'bg-slate-400'
                            : 'bg-slate-500'} rounded-full animate-bounce"
                    ></div>
                    <div
                        class="w-1.5 h-1.5 {isLight
                            ? 'bg-slate-400'
                            : 'bg-slate-500'} rounded-full animate-bounce delay-75"
                    ></div>
                    <div
                        class="w-1.5 h-1.5 {isLight
                            ? 'bg-slate-400'
                            : 'bg-slate-500'} rounded-full animate-bounce delay-150"
                    ></div>
                </div>
            </div>
        {/if}
    </div>

    <!-- Input Area -->
    <div
        class="p-4 border-t {isLight
            ? 'bg-slate-50 border-slate-200'
            : 'bg-[#14141a] border-white/5'}"
    >
        <div
            class="relative flex flex-col border rounded-xl transition-all shadow-inner
            {isLight
                ? 'bg-white border-slate-200 focus-within:border-indigo-500 focus-within:ring-indigo-500/20'
                : 'bg-[#0a0a0c] border-white/10 focus-within:border-indigo-500/50 focus-within:ring-indigo-500/20'}"
        >
            <textarea
                bind:value={userInput}
                on:keydown={handleKeydown}
                placeholder="Escribe tu consulta teológica aquí..."
                rows="3"
                class="w-full bg-transparent text-sm p-4 outline-none resize-none font-sans {isLight
                    ? 'text-slate-700 placeholder:text-slate-400'
                    : 'text-slate-200 placeholder:text-slate-600'}"
            ></textarea>

            <div class="flex justify-between items-center px-2 pb-2 mt-[-5px]">
                <span
                    class="text-[10px] ml-2 font-medium {isLight
                        ? 'text-slate-400'
                        : 'text-slate-600'}">Enter para nueva línea</span
                >
                <button
                    on:click={sendMessage}
                    class="p-2 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg flex items-center gap-2 pr-4 pl-3
                    {isLight
                        ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-indigo-200'
                        : 'bg-indigo-600 text-white hover:bg-indigo-500 shadow-indigo-900/20'}"
                    disabled={!userInput.trim() || isLoading}
                >
                    <span class="text-xs font-bold tracking-wide">ENVIAR</span>
                    <PaperPlaneRight size={16} weight="fill" />
                </button>
            </div>
        </div>
    </div>
</div>
