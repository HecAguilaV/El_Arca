<script>
    import { onMount, tick } from "svelte";
    import { api } from "../lib/api";
    import { fade, slide } from "svelte/transition";
    import toast from "svelte-french-toast";
    import { parse } from "marked";

    export let esClaro = false;
    export let nombreUsuario = "Estudiante";

    let mensajes = [];
    let entradaUsuario = "";
    let cargandoRespuesta = false;
    let contenedorChat;
    let especialistaActual = "reformado";
    let mostrarConfiguracion = false;

    const etiquetasEspecialistas = {
        reformado: "Perspectiva Reformada",
        puritano: "Tradición Puritana",
        bautista: "Confesionalidad 1689",
        pentecostal: "Perspectiva Pentecostal",
        neopuritano: "Neo-Puritanismo",
        bautista_moderno: "Bautismo Moderno",
        academico: "Erudición Académica",
        pastoral: "Consejería Pastoral",
        neofito: "Inducción Básica",
    };

    onMount(() => {
        const historial = localStorage.getItem("arca_historial_chat");
        if (historial) mensajes = JSON.parse(historial);
    });

    async function desplazarAlFinal() {
        await tick();
        if (contenedorChat) {
            contenedorChat.scrollTop = contenedorChat.scrollHeight;
        }
    }

    async function enviarMensaje() {
        if (!entradaUsuario.trim() || cargandoRespuesta) return;

        const texto = entradaUsuario;
        entradaUsuario = "";
        cargandoRespuesta = true;

        mensajes = [...mensajes, { rol: "usuario", texto }];
        desplazarAlFinal();

        try {
            const data = await api.asistente.preguntar(texto);
            const respuesta = data.respuesta;

            mensajes = [...mensajes, { rol: "modelo", texto: respuesta }];
            guardarHistorial();
        } catch (error) {
            mensajes = [
                ...mensajes,
                {
                    rol: "error",
                    texto: "Se produjo una interrupción en la consulta teológica. Verifique su conexión.",
                },
            ];
        } finally {
            cargandoRespuesta = false;
            desplazarAlFinal();
        }
    }

    function guardarHistorial() {
        localStorage.setItem("arca_historial_chat", JSON.stringify(mensajes));
    }

    function borrarHistorial() {
        if (confirm("¿Desea eliminar el hilo actual de conversación?")) {
            mensajes = [];
            localStorage.removeItem("arca_historial_chat");
            toast.success("Conversación finalizada");
        }
    }

    function cambiarEspecialista(p) {
        especialistaActual = p;
        mostrarConfiguracion = false;
        toast.success(`Modo: ${etiquetasEspecialistas[p]}`);
    }

    function manejarTeclas(e) {
        // Enviar con Enter, permitir salto con Shift+Enter
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            enviarMensaje();
        }
    }

    $: claseFondo = esClaro ? "bg-white" : "bg-[#0f0f13]";
    $: claseCabecera = esClaro
        ? "border-stone-200 bg-stone-50"
        : "border-white/5 bg-[#14141a]";
    $: claseTextoBurbujaIA = esClaro
        ? "bg-stone-100 text-stone-800 border-stone-200"
        : "bg-[#18181e] text-stone-200 border-white/5";
    $: claseTextoBurbujaUser = esClaro
        ? "bg-indigo-600 text-white border-indigo-700"
        : "bg-[#1e1e28] text-indigo-100 border-indigo-500/10";
</script>

<div
    class="flex flex-col h-full {claseFondo} relative overflow-hidden transition-colors duration-500"
>
    <!-- Cabecera del Asistente -->
    <div class="flex items-center justify-between p-4 border-b {claseCabecera}">
        <div class="flex flex-col">
            <span
                class="text-[9px] uppercase font-bold tracking-[0.2em] opacity-40"
                >Consultoría</span
            >
            <h2
                class="text-sm font-bold {esClaro
                    ? 'text-stone-800'
                    : 'text-stone-200'}"
            >
                Asistente Teológico
            </h2>
        </div>

        <div class="flex gap-4">
            <button
                on:click={() => (mostrarConfiguracion = !mostrarConfiguracion)}
                class="text-[10px] uppercase font-bold tracking-widest opacity-50 hover:opacity-100 transition-all"
            >
                {etiquetasEspecialistas[especialistaActual]}
            </button>
            <button
                on:click={borrarHistorial}
                class="text-[10px] uppercase font-bold tracking-widest text-red-500/60 hover:text-red-500 transition-all"
            >
                Limpiar
            </button>
        </div>
    </div>

    {#if mostrarConfiguracion}
        <div
            transition:slide
            class="border-b p-6 {esClaro ? 'bg-stone-50' : 'bg-[#1a1a20]'}"
        >
            <h3
                class="text-[9px] uppercase font-bold tracking-widest mb-4 opacity-40"
            >
                Seleccionar Enfoque
            </h3>
            <div class="grid grid-cols-2 gap-3">
                {#each Object.entries(etiquetasEspecialistas) as [key, label]}
                    <button
                        on:click={() => cambiarEspecialista(key)}
                        class="text-left px-4 py-2 text-[10px] uppercase font-bold border {especialistaActual ===
                        key
                            ? 'border-indigo-500 text-indigo-500'
                            : 'border-transparent opacity-50 hover:opacity-100'} transition-all"
                    >
                        {label}
                    </button>
                {/each}
            </div>
        </div>
    {/if}

    <!-- Mensajes -->
    <div
        bind:this={contenedorChat}
        class="flex-1 overflow-y-auto p-6 space-y-8 scroll-smooth"
    >
        {#if mensajes.length === 0}
            <div
                in:fade
                class="h-full flex flex-col items-center justify-center text-center p-10 opacity-20"
            >
                <span
                    class="text-[10px] uppercase font-bold tracking-[0.5em] max-w-[300px]"
                >
                    El diálogo teológico espera su consulta
                </span>
            </div>
        {/if}

        {#each mensajes as msg}
            <div
                class="flex flex-col {msg.rol === 'usuario'
                    ? 'items-end'
                    : 'items-start'}"
            >
                <span
                    class="text-[9px] uppercase font-bold tracking-widest opacity-20 mb-2"
                >
                    {msg.rol === "usuario"
                        ? nombreUsuario
                        : etiquetasEspecialistas[especialistaActual]}
                </span>
                <div
                    class="max-w-[95%] md:max-w-[80%] px-4 py-3 md:px-5 md:py-4 border text-sm leading-relaxed prose prose-sm max-w-none
                    {msg.rol === 'usuario'
                        ? claseTextoBurbujaUser
                        : claseTextoBurbujaIA}"
                >
                    {@html parse(msg.texto)}
                </div>
            </div>
        {/each}

        {#if cargandoRespuesta}
            <div class="flex flex-col items-start" in:fade>
                <span
                    class="text-[9px] uppercase font-bold tracking-widest opacity-20 mb-2 animate-pulse"
                    >Pensando...</span
                >
                <div class="px-5 py-3 border {claseTextoBurbujaIA} opacity-50">
                    <span class="text-[10px] tracking-widest animate-pulse"
                        >...</span
                    >
                </div>
            </div>
        {/if}
    </div>

    <!-- Entrada -->
    <div class="p-4 md:p-6 border-t {claseCabecera}">
        <div
            class="relative flex flex-col border {esClaro
                ? 'bg-white border-stone-200'
                : 'bg-black/20 border-white/10'} rounded-lg"
        >
            <textarea
                bind:value={entradaUsuario}
                on:keydown={manejarTeclas}
                placeholder="Introduzca su consulta..."
                rows="1"
                class="w-full bg-transparent text-sm p-3 md:p-4 outline-none resize-none {esClaro
                    ? 'text-stone-800'
                    : 'text-stone-200'} min-h-[40px] max-h-[150px]"
            ></textarea>

            <div
                class="flex justify-between items-center p-2 md:p-3 border-t {esClaro
                    ? 'border-stone-100'
                    : 'border-white/5'}"
            >
                <span
                    class="text-[8px] md:text-[9px] uppercase font-bold tracking-widest opacity-30 px-2 italic hidden md:inline"
                    >Reflexión Continua</span
                >
                <button
                    on:click={enviarMensaje}
                    class="px-4 py-2 text-[9px] md:text-[10px] uppercase font-bold tracking-[0.2em] bg-indigo-600 text-white hover:bg-indigo-700 transition-all disabled:opacity-30 rounded ml-auto md:ml-0"
                    disabled={!entradaUsuario.trim() || cargandoRespuesta}
                >
                    Enviar
                </button>
            </div>
        </div>
    </div>
</div>
