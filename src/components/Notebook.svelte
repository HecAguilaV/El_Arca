<script>
    import { onMount, onDestroy } from "svelte";
    import { Editor } from "@tiptap/core";
    import StarterKit from "@tiptap/starter-kit";
    import { Table } from "@tiptap/extension-table";
    import { TableRow } from "@tiptap/extension-table-row";
    import { TableCell } from "@tiptap/extension-table-cell";
    import { TableHeader } from "@tiptap/extension-table-header";
    import Placeholder from "@tiptap/extension-placeholder";
    import toast from "svelte-french-toast";
    import ConfirmModal from "./ConfirmModal.svelte";

    // Estado: 'list' (Galería) | 'editor' (Edición)
    let view = "list";
    let notes = [];
    let currentNoteId = null;
    let editor;
    let element;

    // Estado del Modal
    let isModalOpen = false;
    let noteToDeleteId = null;

    onMount(() => {
        loadNotes();
    });

    function loadNotes() {
        const saved = localStorage.getItem("arca_notes");
        if (saved) {
            notes = JSON.parse(saved).sort(
                (a, b) => new Date(b.updatedAt) - new Date(a.updatedAt),
            );
        } else {
            // Migración de la versión anterior (si existe)
            const oldContent = localStorage.getItem("arca_notebook_content");
            if (oldContent) {
                const newNote = createNoteObject("Nota Migrada", oldContent);
                notes = [newNote];
                saveNotes();
                localStorage.removeItem("arca_notebook_content");
            }
        }
    }

    function saveNotes() {
        localStorage.setItem("arca_notes", JSON.stringify(notes));
    }

    function createNoteObject(title, content) {
        return {
            id: Date.now().toString(),
            title: title || "Sin Título",
            content: content || "",
            updatedAt: new Date().toISOString(),
            preview: content ? extractPreview(content) : "Nueva nota...",
        };
    }

    function extractPreview(html) {
        const tmp = document.createElement("DIV");
        tmp.innerHTML = html;
        return tmp.textContent.substring(0, 100) + "...";
    }

    // --- Acciones de Nota ---

    function createNewNote() {
        const newNote = createNoteObject("Nuevo Estudio", "");
        notes = [newNote, ...notes];
        saveNotes();
        openNote(newNote.id);
        toast.success("Nueva nota creada");
    }

    function openNote(id) {
        currentNoteId = id;
        view = "editor";
        // El editor se inicializa reactivamente cuando 'view' cambia y el DOM se actualiza
        setTimeout(() => initEditor(), 50);
    }

    function confirmDelete(e, id) {
        e.stopPropagation();
        noteToDeleteId = id;
        isModalOpen = true;
    }

    function executeDelete() {
        if (noteToDeleteId) {
            notes = notes.filter((n) => n.id !== noteToDeleteId);
            saveNotes();
            toast.success("Nota eliminada correctamente", {
                icon: "🗑️",
                style: "background: #1e1e24; color: #fff; border: 1px solid #333;",
            });
        }
        isModalOpen = false;
        noteToDeleteId = null;
    }

    function cancelDelete() {
        isModalOpen = false;
        noteToDeleteId = null;
    }

    function closeEditor() {
        if (editor) {
            // Guardar última versión antes de salir
            updateCurrentNote(editor.getHTML());
            editor.destroy();
            editor = null;
        }
        view = "list";
        loadNotes(); // Recargar para actualizar orden/previsualización
    }

    let saveTimeout;

    function updateCurrentNote(content) {
        const noteIndex = notes.findIndex((n) => n.id === currentNoteId);
        if (noteIndex !== -1) {
            notes[noteIndex].content = content;
            notes[noteIndex].updatedAt = new Date().toISOString();
            notes[noteIndex].preview = extractPreview(content);

            // Extraer primer H1 como título
            const match = content.match(/<h1>(.*?)<\/h1>/);
            if (match && match[1]) {
                notes[noteIndex].title = match[1].replace(/<[^>]*>/g, "");
            }

            // Debounce para guardar en LocalStorage (esperar 1s de inactividad)
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                saveNotes();
            }, 1000);
        }
    }

    // --- Configuración Tiptap ---

    function initEditor() {
        const note = notes.find((n) => n.id === currentNoteId);
        if (!note || !element) return;

        editor = new Editor({
            element: element,
            extensions: [
                StarterKit,
                Table.configure({ resizable: true }),
                TableRow,
                TableHeader,
                TableCell,
                Placeholder.configure({
                    placeholder:
                        "Escribe aquí... Usa H1 para el título de la nota.",
                }),
            ],
            content: note.content || `<h1>${note.title}</h1><p></p>`,
            onUpdate: ({ editor }) => {
                updateCurrentNote(editor.getHTML());
            },
            onTransaction: () => {
                // Forzar actualización de Svelte para que los botones de la toolbar reaccionen
                editor = editor;
            },
            editorProps: {
                attributes: {
                    class: "prose prose-invert max-w-none focus:outline-none min-h-[500px] p-8 prose-li:marker:text-indigo-400 prose-ul:list-disc prose-ol:list-decimal",
                },
            },
        });

        editor.commands.focus("end");
    }

    function savePDF() {
        window.print();
        toast.success("Preparando impresión...", {
            icon: "🖨️",
            style: "background: #1e1e24; color: #fff;",
        });
    }

    // Backup Manual para prevenir borrados por CCleaner
    function downloadBackup() {
        const dataStr =
            "data:text/json;charset=utf-8," +
            encodeURIComponent(JSON.stringify(notes, null, 2));
        const downloadAnchorNode = document.createElement("a");
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute(
            "download",
            `respaldo_arca_${new Date().toISOString().slice(0, 10)}.json`,
        );
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
        toast.success("Copia de seguridad descargada", {
            icon: "💾",
            style: "background: #1e1e24; color: #fff;",
        });
    }
</script>

<div
    class="flex flex-col h-full bg-white/5 backdrop-blur-md rounded-xl border border-white/10 overflow-hidden notebook-container relative"
>
    {#if view === "list"}
        <!-- VISTA DE GALERÍA -->
        <div class="p-6 h-full flex flex-col">
            <div class="flex justify-between items-center mb-6">
                <h2
                    class="text-xl font-bold text-white flex items-center gap-2"
                >
                    📚 Mis Estudios
                    <span
                        class="text-xs bg-white/10 px-2 py-0.5 rounded-full text-slate-400 font-normal"
                        >{notes.length}</span
                    >
                </h2>
                <button
                    on:click={createNewNote}
                    class="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 shadow-lg shadow-indigo-500/20"
                >
                    + Nueva Nota
                </button>
            </div>

            <!-- Aviso CCleaner (Discreto) -->
            <div class="px-1 mb-4 flex justify-end">
                <button
                    on:click={downloadBackup}
                    class="text-xs text-slate-600 hover:text-indigo-400 flex items-center gap-1 transition-colors"
                    title="Exportar archivo de seguridad (backup)"
                >
                    📩 Exportar Datos
                </button>
            </div>

            <div
                class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-4 overflow-y-auto pr-2 pb-4"
            >
                {#each notes as note (note.id)}
                    <div
                        on:click={() => openNote(note.id)}
                        class="group relative bg-[#1a1a20] border border-white/5 hover:border-indigo-500/30 p-5 rounded-xl cursor-pointer transition-all hover:translate-y-[-2px] hover:shadow-xl"
                    >
                        <h3
                            class="font-bold text-slate-200 mb-2 line-clamp-1 group-hover:text-indigo-400 transition-colors"
                        >
                            {note.title}
                        </h3>
                        <p
                            class="text-xs text-slate-500 mb-4 line-clamp-3 h-10"
                        >
                            {note.preview}
                        </p>
                        <div class="flex justify-between items-end mt-2">
                            <span class="text-[10px] text-slate-600 font-mono">
                                {new Date(note.updatedAt).toLocaleDateString(
                                    [],
                                    { day: "2-digit", month: "short" },
                                )}
                            </span>
                            <button
                                on:click|stopPropagation={(e) =>
                                    confirmDelete(e, note.id)}
                                class="text-slate-600 hover:text-red-400 p-1.5 rounded-md hover:bg-white/5 transition-colors opacity-0 group-hover:opacity-100"
                                title="Eliminar"
                            >
                                🗑️
                            </button>
                        </div>
                    </div>
                {/each}

                {#if notes.length === 0}
                    <div
                        class="col-span-full py-12 text-center text-slate-500 italic"
                    >
                        No hay notas aún. ¡Crea la primera! ✨
                    </div>
                {/if}
            </div>
        </div>

        <ConfirmModal
            isOpen={isModalOpen}
            title="Eliminar Nota"
            message="¿Estás seguro de que quieres eliminar esta nota? Esta acción no se puede deshacer."
            confirmText="Sí, Eliminar"
            cancelText="Cancelar"
            on:confirm={executeDelete}
            on:cancel={cancelDelete}
        />
    {:else}
        <!-- VISTA DE EDITOR -->
        <div class="flex flex-col h-full">
            <!-- Toolbar -->
            <div
                class="flex gap-2 p-3 border-b border-white/10 bg-black/20 items-center overflow-x-auto whitespace-nowrap scrollbar-hide flex-shrink-0"
            >
                <button
                    on:click={closeEditor}
                    class="mr-2 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1"
                    title="Volver a la lista"
                >
                    <span>←</span> <span class="hidden sm:inline">Volver</span>
                </button>

                <div class="w-px h-6 bg-white/10 mx-1"></div>

                {#if editor}
                    <!-- Botones Semánticos -->
                    <button
                        on:click={() =>
                            editor
                                .chain()
                                .focus()
                                .toggleHeading({ level: 1 })
                                .run()}
                        class="px-3 py-1.5 rounded hover:bg-white/10 text-xs font-medium transition-colors {editor.isActive(
                            'heading',
                            { level: 1 },
                        )
                            ? 'bg-white/20 text-indigo-400'
                            : 'text-slate-400'}"
                    >
                        Título
                    </button>

                    <button
                        on:click={() =>
                            editor
                                .chain()
                                .focus()
                                .toggleHeading({ level: 2 })
                                .run()}
                        class="px-3 py-1.5 rounded hover:bg-white/10 text-xs font-medium transition-colors {editor.isActive(
                            'heading',
                            { level: 2 },
                        )
                            ? 'bg-white/20 text-indigo-400'
                            : 'text-slate-400'}"
                    >
                        Subtítulo
                    </button>

                    <button
                        on:click={() =>
                            editor.chain().focus().setParagraph().run()}
                        class="px-3 py-1.5 rounded hover:bg-white/10 text-xs font-medium transition-colors {editor.isActive(
                            'paragraph',
                        )
                            ? 'bg-white/20 text-indigo-400'
                            : 'text-slate-400'}"
                    >
                        Párrafo
                    </button>

                    <div class="w-px h-6 bg-white/10 mx-1"></div>

                    <button
                        on:click={() =>
                            editor.chain().focus().toggleBold().run()}
                        class="px-3 py-1.5 rounded hover:bg-white/10 text-xs font-medium transition-colors {editor.isActive(
                            'bold',
                        )
                            ? 'bg-white/20 text-indigo-400'
                            : 'text-slate-400'}"
                        title="Negrita"
                    >
                        Negrita
                    </button>

                    <button
                        on:click={() =>
                            editor.chain().focus().toggleItalic().run()}
                        class="px-3 py-1.5 rounded hover:bg-white/10 text-xs font-medium transition-colors {editor.isActive(
                            'italic',
                        )
                            ? 'bg-white/20 text-indigo-400'
                            : 'text-slate-400'}"
                        title="Cursiva"
                    >
                        Cursiva
                    </button>

                    <button
                        on:click={() =>
                            editor.chain().focus().toggleBulletList().run()}
                        class="px-3 py-1.5 rounded hover:bg-white/10 text-xs font-medium transition-colors {editor.isActive(
                            'bulletList',
                        )
                            ? 'bg-white/20 text-indigo-400'
                            : 'text-slate-400'}"
                        title="Lista de Puntos"
                    >
                        Lista
                    </button>

                    <div class="flex-1"></div>

                    <button
                        on:click={savePDF}
                        class="px-3 py-1.5 bg-indigo-600/20 text-indigo-300 hover:bg-indigo-600 hover:text-white rounded-md text-xs font-medium transition-colors flex items-center gap-2"
                    >
                        <span>🖨️</span> PDF
                    </button>
                {/if}
            </div>

            <!-- Editor Area -->
            <div
                class="flex-1 overflow-auto bg-[#1e1e24] scroll-smooth relative"
            >
                <div
                    bind:this={element}
                    class="h-full w-full outline-none prose prose-invert max-w-none p-8"
                ></div>
            </div>
        </div>
    {/if}
</div>
```

<style>
    /* Estilos específicos para Tiptap en Svelte */
    :global(.ProseMirror) {
        min-height: 100%;
        outline: none;
    }

    /* FIX LISTAS: Asegurar que las listas tengan estilo visible */
    :global(.ProseMirror ul) {
        list-style-type: disc !important;
        padding-left: 1.5rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    :global(.ProseMirror li) {
        margin-bottom: 0.25rem !important;
    }

    /* FIX HEADINGS: Asegurar tamaños visibles en vivo */
    :global(.ProseMirror h1) {
        font-size: 2.25rem !important;
        font-weight: 800 !important;
        margin-bottom: 1rem !important;
        color: white !important;
    }
    :global(.ProseMirror h2) {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
        color: #e2e8f0 !important;
    }

    :global(.ProseMirror p.is-editor-empty:first-child::before) {
        color: #6b7280;
        content: attr(data-placeholder);
        float: left;
        height: 0;
        pointer-events: none;
    }

    /* Estilos de tabla básicos para el editor */
    :global(.ProseMirror table) {
        border-collapse: collapse;
        margin: 0;
        overflow: hidden;
        table-layout: fixed;
        width: 100%;
    }

    :global(.ProseMirror td),
    :global(.ProseMirror th) {
        border: 1px solid #4b5563;
        box-sizing: border-box;
        min-width: 1em;
        padding: 6px 8px;
        position: relative;
        vertical-align: top;
    }

    :global(.ProseMirror th) {
        font-weight: bold;
        text-align: left;
        background-color: rgba(255, 255, 255, 0.05);
    }

    /* Media Print para exportación limpia */
    @media print {
        /* Estrategia de Visibilidad: Ocultar todo visualmente pero mantener layout básico */
        :global(body) {
            visibility: hidden !important;
            background: white !important;
            color: black !important;
        }

        /* Hacer visible EXPLICITAMENTE el contenedor del notebook y sus hijos */
        :global(.notebook-container),
        :global(.notebook-container *) {
            visibility: visible !important;
        }

        /* Posicionar el notebook para ocupar toda la página física */
        :global(.notebook-container) {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            margin: 0 !important;
            padding: 2cm !important; /* Margen de impresión */
            background: white !important;
            color: black !important;
            z-index: 999999 !important;
            overflow: visible !important;
            border: none !important;
            display: block !important;
        }

        /* Ocultar elementos de UI internos que no deben imprimirse */
        .notebook-container > div:first-child, /* Toolbar */
        .flex.justify-end /* Botón Backup */ {
            display: none !important;
        }

        /* Estilos del contenido (ProseMirror) para impresión */
        :global(.ProseMirror) {
            font-family: "Georgia", serif !important;
            font-size: 12pt !important;
            line-height: 1.6 !important;
            color: black !important;
            background: white !important;
            width: 100% !important;
            height: auto !important;
            overflow: visible !important;
        }

        :global(.ProseMirror h1) {
            font-size: 24pt !important;
            margin-bottom: 24pt !important;
            color: black !important;
            page-break-after: avoid;
        }

        :global(.ProseMirror h2) {
            font-size: 18pt !important;
            margin-top: 20pt !important;
            margin-bottom: 12pt !important;
            color: black !important;
            page-break-after: avoid;
        }

        :global(.ProseMirror p) {
            margin-bottom: 12pt !important;
            color: black !important;
        }

        :global(.ProseMirror ul),
        :global(.ProseMirror ol) {
            margin-bottom: 12pt !important;
            padding-left: 20pt !important;
            color: black !important;
        }

        :global(.ProseMirror li) {
            margin-bottom: 4pt !important;
            color: black !important;
        }

        /* Reset general de colores */
        :global(.ProseMirror *) {
            color: black !important;
            background: transparent !important;
            text-shadow: none !important;
        }
    }
</style>
