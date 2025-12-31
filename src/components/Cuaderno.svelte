<script>
    import { onMount, onDestroy } from "svelte";
    import { get } from "svelte/store";
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

    export let esClaro = false;

    // Estado: 'lista' | 'editor'
    let vista = "lista";
    let notaActualId = null;
    let instanciaEditor;
    let elementoEditor;

    onMount(async () => {
        // Usamos get() explícito para evitar problemas de compatibilidad en el parser
        const valorNotas = get(notas);
        if (valorNotas.length === 0) {
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

    async function eliminarNotaActual() {
        if (
            !confirm(
                "¿Está seguro de que desea eliminar este estudio teológico? Esta acción no se puede deshacer.",
            )
        )
            return;

        try {
            await api.notas.eliminar(notaActualId);
            toast.success("Estudio eliminado");
            if (instanciaEditor) {
                instanciaEditor.destroy();
                instanciaEditor = null;
            }
            vista = "lista";
            await sincronizarNotas();
        } catch (error) {
            toast.error("Error al eliminar nota");
        }
    }

    async function eliminarNotaDesdeLista(id, e) {
        e.stopPropagation();
        if (!confirm("¿Eliminar este estudio?")) return;

        try {
            await api.notas.eliminar(id);
            toast.success("Eliminado");
            await sincronizarNotas();
        } catch (error) {
            toast.error("Error al eliminar");
        }
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
                // STARTER KIT ya incluye BulletList y ListItem
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
        if (!instanciaEditor) return;

        const contenidoHTML = instanciaEditor.getHTML();

        // Crear un iframe invisible
        const iframe = document.createElement("iframe");
        iframe.style.position = "absolute";
        iframe.style.width = "0";
        iframe.style.height = "0";
        iframe.style.border = "none";

        document.body.appendChild(iframe);

        const doc = iframe.contentWindow.document;
        doc.open();
        doc.write(`
            <html>
            <head>
                <title>Imprimir Estudio</title>
                <style>
                    body {
                        font-family: 'Georgia', serif;
                        font-size: 12pt;
                        line-height: 1.5;
                        color: #000;
                        margin: 2.5cm; /* Márgenes de hoja */
                        background: white;
                    }
                    h1 {
                        font-family: sans-serif;
                        font-size: 24pt;
                        border-bottom: 2px solid #000;
                        margin-bottom: 20px;
                        padding-bottom: 10px;
                    }
                    h2 {
                        font-family: sans-serif;
                        font-size: 18pt;
                        margin-top: 20px;
                        margin-bottom: 10px;
                    }
                    p, li {
                        text-align: justify;
                        margin-bottom: 10px;
                    }
                    ul, ol {
                        padding-left: 20px;
                    }
                    /* Asegurar que las imágenes no se salgan */
                    img {
                        max-width: 100%;
                        height: auto;
                    }
                </style>
            </head>
            <body>
                ${contenidoHTML}
            </body>
            </html>
        `);
        doc.close();

        // Esperar a que cargue y llamar a imprimir
        iframe.contentWindow.focus();
        setTimeout(() => {
            iframe.contentWindow.print();
            // Eliminar el iframe después de imprimir (darle tiempo al diálogo)
            setTimeout(() => {
                document.body.removeChild(iframe);
            }, 500);
        }, 250);
    }

    $: claseContenedor = esClaro
        ? "bg-white border-stone-200"
        : "bg-white/5 border-white/10";
    $: claseToolbar = esClaro
        ? "bg-stone-50 border-stone-200"
        : "bg-black/20 border-white/10";
    $: claseTarjeta = esClaro
        ? "bg-white border-stone-200 hover:border-indigo-300"
        : "bg-[#1a1a20] border-white/5 hover:border-indigo-500/30";
    $: claseBotonBarra = esClaro
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
                        class="text-2xl font-bold {esClaro
                            ? 'text-stone-900'
                            : 'text-white'}">Cuaderno Teológico</span
                    >
                </div>
                <button
                    on:click={crearNuevaNota}
                    class="px-6 py-2 border {esClaro
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
                    <div
                        class="{claseTarjeta} text-left p-6 border transition-all flex flex-col h-48 group cursor-pointer hover:shadow-lg hover:scale-[1.02]"
                        on:click={() => abrirNota(nota.id)}
                    >
                        <span
                            class="text-[9px] uppercase font-bold tracking-widest opacity-50 mb-2"
                        >
                            {new Date(
                                nota.fecha_actualizacion,
                            ).toLocaleDateString()}
                        </span>
                        <h3
                            class="font-bold text-lg mb-3 line-clamp-2 {esClaro
                                ? 'text-stone-800'
                                : 'text-stone-100'} group-hover:text-indigo-500 transition-colors"
                        >
                            {nota.titulo}
                        </h3>
                        <p
                            class="text-[11px] leading-relaxed opacity-60 line-clamp-3 mb-4"
                        >
                            {nota.previsualización}
                        </p>

                        <div
                            class="mt-auto flex justify-end opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                            <button
                                on:click|stopPropagation={(e) =>
                                    eliminarNotaDesdeLista(nota.id, e)}
                                class="text-[9px] uppercase font-bold tracking-widest text-red-500 hover:bg-red-500/10 rounded px-2 py-1 transition-colors"
                            >
                                Eliminar
                            </button>
                        </div>
                    </div>
                {/each}

                {#if $notas.length === 0 && !$cargando}
                    <div
                        class="col-span-full flex flex-col items-center justify-center py-20 text-center gap-4"
                    >
                        <span class="text-4xl opacity-20">✍️</span>
                        <p
                            class="text-[10px] uppercase font-bold tracking-[0.3em] opacity-40"
                        >
                            Su cuaderno está vacío
                        </p>
                        <button
                            on:click={crearNuevaNota}
                            class="px-8 py-3 bg-indigo-600 text-white rounded-lg shadow-lg hover:bg-indigo-500 transition-all text-xs font-bold uppercase tracking-widest"
                        >
                            Crear primer estudio
                        </button>
                    </div>
                {/if}
            </div>
        </div>
    {:else}
        <!-- EDITOR DE ESTUDIO -->
        <div class="flex flex-col h-full">
            <!-- Barra de Herramientas -->
            <div
                class="flex gap-2 p-3 border-b items-center flex-wrap flex-shrink-0 {claseToolbar}"
            >
                <button
                    on:click={cerrarEditor}
                    class="px-4 py-2 text-[10px] uppercase font-bold tracking-widest {claseBotonBarra} border-r border-white/10 mr-2"
                >
                    Volver
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
                        class="px-4 py-2 text-[10px] uppercase font-bold tracking-widest {claseBotonBarra} border-l border-white/10 ml-2"
                    >
                        Exportar PDF
                    </button>

                    <button
                        on:click={eliminarNotaActual}
                        class="px-4 py-2 text-[10px] uppercase font-bold tracking-widest text-red-400 hover:bg-red-500/10 transition-colors"
                    >
                        Eliminar
                    </button>
                {/if}
            </div>

            <!-- Área de Escritura -->
            <div
                class="flex-1 overflow-y-auto cursor-text outline-none {esClaro
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
    /* Estilos del Editor en Pantalla */
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

    /* VISTA EN PANTALLA: Ocultar área de impresión */
    @media screen {
        .area-impresion {
            display: none;
        }
    }

    /* VISTA EN IMPRESIÓN: Usar SOLO el área de impresión */
    @media print {
        @page {
            margin: 2.5cm;
            size: A4;
        }

        /* 1. Ocultar TODO lo de la aplicación original */
        :global(body > *),
        :global(#app > *) {
            display: none !important;
        }

        /* 2. Asegurar que html y body sean blancos y visibles */
        :global(html),
        :global(body) {
            background-color: white !important;
            visibility: visible !important;
            overflow: visible !important;
            height: auto !important;
        }

        /* 3. Mostrar y estilizar el ÁREA DE IMPRESIÓN DEDICADA */
        .area-impresion {
            display: block !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            z-index: 99999;
            background-color: white !important;
        }

        /* 4. Estilos Editoriales Limpios (sin Tailwind prose classes) */
        .area-impresion :global(h1) {
            font-family: sans-serif;
            font-size: 24pt;
            border-bottom: 2px solid black;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            color: black;
        }

        .area-impresion :global(p),
        .area-impresion :global(li) {
            font-family: "Georgia", serif;
            font-size: 12pt;
            line-height: 1.5;
            color: black;
            text-align: justify;
            margin-bottom: 1rem;
        }

        .area-impresion :global(ul) {
            list-style-type: disc;
            padding-left: 1.5rem;
        }
    }
</style>
