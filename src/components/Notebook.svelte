<script>
    import { onMount, onDestroy } from "svelte";
    import { Editor } from "@tiptap/core";
    import StarterKit from "@tiptap/starter-kit";
    import { Table } from "@tiptap/extension-table";
    import { TableRow } from "@tiptap/extension-table-row";
    import { TableCell } from "@tiptap/extension-table-cell";
    import { TableHeader } from "@tiptap/extension-table-header";
    import Placeholder from "@tiptap/extension-placeholder";
    import CharacterCount from "@tiptap/extension-character-count";
    import toast from "svelte-french-toast";

    import { api } from "../lib/api";
    import { notas, cargando, sincronizarNotas } from "../lib/stores";

    export let isLight = false;

    // Estado: 'lista' | 'editor'
    let vista = "lista";
    let notaActualId = null;
    let instanciaEditor;
    let elementoEditor;

    onMount(async () => {
        // Los datos ya deberían estar cargados por el store global,
        // pero podemos forzar una sincronización si es necesario.
        if ($notas.length === 0) {
            await sincronizarNotas();
        }
    });

    function extraerPrevisualizacion(html) {
        if (!html) return "Sin contenido...";
        const tmp = document.createElement("DIV");
        tmp.innerHTML = html;
        return tmp.textContent.substring(0, 100) + "...";
    }

    async function crearNuevaNota() {
        try {
            const nueva = await api.notas.crear({
                titulo: "Nuevo Estudio Teológico",
                contenido_html:
                    "<h1>Título del Estudio</h1><p>Comience su investigación aquí...</p>",
                previsualización: "Nuevo estudio...",
                palabras_clave: "",
            });
            await sincronizarNotas();
            abrirNota(nueva.id);
            toast.success("Estudio iniciado");
        } catch (error) {
            toast.error("Error al crear nota");
        }
    }

    function abrirNota(id) {
        notaActualId = id;
        vista = "editor";
        setTimeout(() => inicializarEditor(), 50);
    }

    async function cerrarEditor() {
        if (instanciaEditor) {
            await guardarNotaActual(instanciaEditor.getHTML());
            instanciaEditor.destroy();
            instanciaEditor = null;
        }
        vista = "lista";
        await sincronizarNotas();
    }

    let tiempoGuardado;
    async function guardarNotaActual(contenido) {
        const nota = $notas.find((n) => n.id === notaActualId);
        if (!nota) return;

        // Extraer primer H1 para el título dinámico
        let titulo = nota.titulo;
        const coincidenciaH1 = contenido.match(/<h1>(.*?)<\/h1>/);
        if (coincidenciaH1 && coincidenciaH1[1]) {
            titulo = coincidenciaH1[1].replace(/<[^>]*>/g, "");
        }

        const datosActualizados = {
            titulo: titulo,
            contenido_html: contenido,
            previsualización: extraerPrevisualizacion(contenido),
            palabras_clave: nota.palabras_clave,
        };

        clearTimeout(tiempoGuardado);
        tiempoGuardado = setTimeout(async () => {
            try {
                await api.notas.actualizar(notaActualId, datosActualizados);
            } catch (error) {
                console.error("Error al auto-guardar:", error);
            }
        }, 1500);
    }

    function inicializarEditor() {
        const nota = $notas.find((n) => n.id === notaActualId);
        if (!nota || !elementoEditor) return;

        instanciaEditor = new Editor({
            element: elementoEditor,
            extensions: [
                StarterKit,
                Table.configure({ resizable: true }),
                TableRow,
                TableHeader,
                TableCell,
                Placeholder.configure({
                    placeholder:
                        "El estudio de la verdad requiere diligencia. Use H1 para el título.",
                }),
                CharacterCount,
            ],
            content: nota.contenido_html,
            onUpdate: ({ editor }) => {
                guardarNotaActual(editor.getHTML());
            },
            onTransaction: () => {
                instanciaEditor = instanciaEditor;
            },
            editorProps: {
                attributes: {
                    class: "prose max-w-none focus:outline-none min-h-[500px] p-8",
                },
            },
        });

        instanciaEditor.commands.focus("end");
    }

    function imprimirPDF() {
        window.print();
    }

    $: claseContenedor = isLight
        ? "bg-white border-stone-200"
        : "bg-white/5 border-white/10";
    $: claseToolbar = isLight
        ? "bg-stone-50 border-stone-200"
        : "bg-black/20 border-white/10";
    $: claseTarjeta = isLight
        ? "bg-white border-stone-200 hover:border-indigo-300"
        : "bg-[#1a1a20] border-white/5 hover:border-indigo-500/30";
    $: claseBotonBarra = isLight
        ? "text-stone-500 hover:bg-stone-100"
        : "text-slate-400 hover:bg-white/10";
</script>

<div
    class="flex flex-col h-full {claseContenedor} backdrop-blur-md rounded-xl border overflow-hidden relative transition-colors duration-500 notebook-container"
>
    {#if vista === "lista"}
        <!-- LISTADO DE ESTUDIOS -->
        <div class="p-6 h-full flex flex-col">
            <div class="flex justify-between items-center mb-10">
                <div class="flex flex-col">
                    <h2
                        class="text-xs uppercase font-bold tracking-[0.3em] opacity-40"
                    >
                        Mis Estudios
                    </h2>
                    <span
                        class="text-2xl font-bold {isLight
                            ? 'text-stone-900'
                            : 'text-white'}">Cuaderno Teológico</span
                    >
                </div>
                <button
                    on:click={crearNuevaNota}
                    class="px-6 py-2 border {isLight
                        ? 'border-stone-800 text-stone-900'
                        : 'border-white/40 text-white'} text-[10px] uppercase font-bold tracking-widest hover:bg-indigo-600 hover:text-white hover:border-indigo-600 transition-all"
                >
                    Iniciar Nuevo Estudio
                </button>
            </div>

            <div
                class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 overflow-y-auto pb-10"
            >
                {#each $notas as nota (nota.id)}
                    <button
                        on:click={() => abrirNota(nota.id)}
                        class="{claseTarjeta} text-left p-6 border transition-all flex flex-col h-48 group"
                    >
                        <span
                            class="text-[9px] uppercase font-bold tracking-widest opacity-30 mb-2"
                        >
                            {new Date(
                                nota.fecha_actualizacion,
                            ).toLocaleDateString()}
                        </span>
                        <h3
                            class="font-bold text-lg mb-3 line-clamp-2 {isLight
                                ? 'text-stone-800'
                                : 'text-stone-100'} group-hover:text-indigo-500 transition-colors"
                        >
                            {nota.titulo}
                        </h3>
                        <p
                            class="text-[11px] leading-relaxed opacity-50 line-clamp-3"
                        >
                            {nota.previsualización}
                        </p>
                    </button>
                {/each}

                {#if $notas.length === 0 && !$cargando}
                    <div
                        class="col-span-full py-20 text-center opacity-30 text-[10px] uppercase font-bold tracking-[0.4em]"
                    >
                        El cuaderno está en espera de su pluma
                    </div>
                {/if}
            </div>
        </div>
    {:else}
        <!-- EDITOR DE ESTUDIO -->
        <div class="flex flex-col h-full">
            <!-- Barra de Herramientas -->
            <div
                class="flex gap-2 p-3 border-b items-center overflow-x-auto whitespace-nowrap scrollbar-hide flex-shrink-0 {claseToolbar}"
            >
                <button
                    on:click={cerrarEditor}
                    class="px-4 py-2 text-[10px] uppercase font-bold tracking-widest {claseBotonBarra} border-r border-white/10 mr-2"
                >
                    Cerrar
                </button>

                {#if instanciaEditor}
                    <div class="flex gap-1">
                        <button
                            on:click={() =>
                                instanciaEditor
                                    .chain()
                                    .focus()
                                    .toggleHeading({ level: 1 })
                                    .run()}
                            class="px-3 py-2 text-[10px] uppercase font-bold {claseBotonBarra} {instanciaEditor.isActive(
                                'heading',
                                { level: 1 },
                            )
                                ? 'text-indigo-500'
                                : ''}"
                        >
                            Título
                        </button>
                        <button
                            on:click={() =>
                                instanciaEditor
                                    .chain()
                                    .focus()
                                    .toggleHeading({ level: 2 })
                                    .run()}
                            class="px-3 py-2 text-[10px] uppercase font-bold {claseBotonBarra} {instanciaEditor.isActive(
                                'heading',
                                { level: 2 },
                            )
                                ? 'text-indigo-500'
                                : ''}"
                        >
                            Subtítulo
                        </button>
                        <button
                            on:click={() =>
                                instanciaEditor
                                    .chain()
                                    .focus()
                                    .setParagraph()
                                    .run()}
                            class="px-3 py-2 text-[10px] uppercase font-bold {claseBotonBarra} {instanciaEditor.isActive(
                                'paragraph',
                            )
                                ? 'text-indigo-500'
                                : ''}"
                        >
                            Párrafo
                        </button>
                    </div>

                    <div class="w-px h-4 bg-white/10 mx-2"></div>

                    <div class="flex gap-1">
                        <button
                            on:click={() =>
                                instanciaEditor
                                    .chain()
                                    .focus()
                                    .toggleBold()
                                    .run()}
                            class="px-3 py-2 text-[10px] uppercase font-bold {claseBotonBarra} {instanciaEditor.isActive(
                                'bold',
                            )
                                ? 'text-indigo-500'
                                : ''}"
                        >
                            Negrita
                        </button>
                        <button
                            on:click={() =>
                                instanciaEditor
                                    .chain()
                                    .focus()
                                    .toggleItalic()
                                    .run()}
                            class="px-3 py-2 text-[10px] uppercase font-bold {claseBotonBarra} {instanciaEditor.isActive(
                                'italic',
                            )
                                ? 'text-indigo-500'
                                : ''}"
                        >
                            Cursiva
                        </button>
                        <button
                            on:click={() =>
                                instanciaEditor
                                    .chain()
                                    .focus()
                                    .toggleBulletList()
                                    .run()}
                            class="px-3 py-2 text-[10px] uppercase font-bold {claseBotonBarra} {instanciaEditor.isActive(
                                'bulletList',
                            )
                                ? 'text-indigo-500'
                                : ''}"
                        >
                            Lista
                        </button>
                    </div>

                    <div class="flex-1"></div>

                    <button
                        on:click={imprimirPDF}
                        class="px-4 py-2 text-[10px] uppercase font-bold tracking-widest {claseBotonBarra}"
                    >
                        Exportar PDF
                    </button>
                {/if}
            </div>

            <!-- Área de Escritura -->
            <div
                class="flex-1 overflow-y-auto cursor-text outline-none {isLight
                    ? 'prose-stone'
                    : 'prose-invert'}"
                on:click={() => instanciaEditor?.commands.focus()}
            >
                <div bind:this={elementoEditor}></div>
            </div>

            <!-- Estado -->
            <div
                class="px-6 py-3 text-[9px] uppercase font-bold tracking-[0.2em] flex justify-between items-center border-t {claseToolbar} opacity-40"
            >
                <span>Persistencia activa en base de datos</span>
                <span
                    >{instanciaEditor?.storage.characterCount.words() || 0} palabras</span
                >
            </div>
        </div>
    {/if}
</div>

<style>
    /* Estilos del Editor */
    :global(.ProseMirror) {
        min-height: 100%;
        outline: none;
    }
    :global(.ProseMirror h1) {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        margin-bottom: 2rem !important;
    }
    :global(.ProseMirror h2) {
        font-size: 1.5rem !important;
        margin-top: 2rem !important;
    }
    :global(.ProseMirror p) {
        line-height: 1.8 !important;
    }

    /* MEDIA PRINT: EXPORTACIÓN PROFESIONAL A PDF */
    @media print {
        @page {
            margin: 2cm;
            size: A4;
        }

        /* 1. Reset Global - Ocultamos todo lo que no sea el área de impresión */
        :global(body),
        :global(#app),
        :global(main),
        :global(.min-h-screen) {
            background: white !important;
            visibility: hidden !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
            height: auto !important;
        }

        /* 2. Mostrar solo el contenedor específico de la nota */
        :global(.notebook-container) {
            visibility: visible !important;
            display: block !important;
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
            width: 100% !important;
            height: auto !important;
            border: 0 none !important; /* Forzamos eliminación total de bordes */
            outline: none !important;
            box-shadow: none !important;
            background: white !important;
            color: black !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
        }

        :global(.notebook-container *) {
            visibility: visible !important;
        }

        /* 3. Limpieza de elementos de interfaz */
        .border-b,
        .border-t,
        button,
        span.uppercase,
        .flex-none,
        .flex-shrink-0 {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
        }

        /* 4. Formato Editorial para el Texto (Georgia/Serif) */
        :global(.ProseMirror) {
            padding: 0 !important;
            margin: 0 !important;
            color: black !important;
            font-family: serif !important; /* Fallback universal */
            font-size: 12pt !important;
            line-height: 1.6 !important;
            text-align: justify !important;
            border: none !important;
            box-shadow: none !important;
        }

        :global(.ProseMirror h1) {
            font-family: sans-serif !important;
            font-size: 24pt !important;
            font-weight: bold !important;
            color: black !important;
            border-bottom: 2pt solid #000 !important;
            padding-bottom: 8pt !important;
            margin-bottom: 15pt !important;
            margin-top: 0 !important;
        }

        :global(.ProseMirror h2) {
            font-family: sans-serif !important;
            font-size: 18pt !important;
            margin-top: 15pt !important;
            margin-bottom: 8pt !important;
            color: #333 !important;
        }

        /* Asegurar tablas limpias */
        :global(.ProseMirror table) {
            border-collapse: collapse !important;
            border: 1pt solid black !important;
            margin: 10pt 0 !important;
        }
        :global(.ProseMirror td),
        :global(.ProseMirror th) {
            border: 1pt solid black !important;
            padding: 4pt !important;
        }
    }
</style>
