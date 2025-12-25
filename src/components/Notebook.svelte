<script>
    import { onMount, onDestroy } from "svelte";
    import { Editor } from "@tiptap/core";
    import StarterKit from "@tiptap/starter-kit";
    import { Table } from "@tiptap/extension-table";
    import { TableRow } from "@tiptap/extension-table-row";
    import { TableCell } from "@tiptap/extension-table-cell";
    import { TableHeader } from "@tiptap/extension-table-header";
    import Placeholder from "@tiptap/extension-placeholder";
    import CharacterCount from "@tiptap/extension-character-count"; // Importar extensión
    import toast from "svelte-french-toast";
    import ConfirmModal from "./ConfirmModal.svelte";

    export let isLight = false; // Fix: Recibir prop para tema dinámico

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
                CharacterCount, // Agregar a extensiones
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
    class="flex flex-col h-full {isLight
        ? 'bg-white border-slate-200'
        : 'bg-white/5 border-white/10'} backdrop-blur-md rounded-xl border overflow-hidden notebook-container relative transition-colors duration-500"
>
    {#if view === "list"}
        <!-- VISTA DE GALERÍA -->
        <div class="p-6 h-full flex flex-col">
            <div class="flex justify-between items-center mb-6">
                <h2
                    class="text-xl font-bold flex items-center gap-2 {isLight
                        ? 'text-slate-800'
                        : 'text-white'}"
                >
                    📚 Mis Estudios
                    <span
                        class="text-xs px-2 py-0.5 rounded-full font-normal {isLight
                            ? 'bg-slate-100 text-slate-500'
                            : 'bg-white/10 text-slate-400'}"
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
                        class="group relative border p-5 rounded-xl cursor-pointer transition-all hover:translate-y-[-2px] hover:shadow-xl
                        {isLight
                            ? 'bg-white border-slate-200 hover:border-indigo-300 hover:shadow-indigo-100/50'
                            : 'bg-[#1a1a20] border-white/5 hover:border-indigo-500/30'}"
                    >
                        <h3
                            class="font-bold mb-2 line-clamp-1 transition-colors {isLight
                                ? 'text-slate-700 group-hover:text-indigo-600'
                                : 'text-slate-200 group-hover:text-indigo-400'}"
                        >
                            {note.title}
                        </h3>
                        <p
                            class="text-xs text-slate-500 mb-4 line-clamp-3 h-10"
                        >
                            {note.preview}
                        </p>
                        <div class="flex justify-between items-end mt-2">
                            <span
                                class="text-[10px] font-mono {isLight
                                    ? 'text-slate-400'
                                    : 'text-slate-600'}"
                            >
                                {new Date(note.updatedAt).toLocaleDateString(
                                    [],
                                    { day: "2-digit", month: "short" },
                                )}
                            </span>
                            <button
                                on:click|stopPropagation={(e) =>
                                    confirmDelete(e, note.id)}
                                class="p-1.5 rounded-md transition-colors opacity-0 group-hover:opacity-100 {isLight
                                    ? 'text-slate-400 hover:text-red-500 hover:bg-red-50'
                                    : 'text-slate-600 hover:text-red-400 hover:bg-white/5'}"
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
                class="flex gap-2 p-3 border-b items-center overflow-x-auto whitespace-nowrap scrollbar-hide flex-shrink-0 transition-colors
                {isLight
                    ? 'bg-slate-50 border-slate-200'
                    : 'bg-black/20 border-white/10'}"
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
                                .toggleHeading({ level: 1 })
                                .run()}
                        class="px-3 py-1.5 rounded-lg text-xs font-serif transition-all
                {editor.isActive('heading', { level: 1 })
                            ? isLight
                                ? 'bg-indigo-100 text-indigo-700'
                                : 'bg-white/20 text-white shadow-sm'
                            : isLight
                              ? 'text-slate-600 hover:bg-slate-200'
                              : 'text-slate-400 hover:bg-white/10 hover:text-white'}"
                    >
                        H1
                    </button>
                    <button
                        on:click={() =>
                            editor
                                .chain()
                                .focus()
                                .toggleHeading({ level: 2 })
                                .run()}
                        class="px-3 py-1.5 rounded-lg text-xs font-serif transition-all font-bold
                {editor.isActive('heading', { level: 2 })
                            ? isLight
                                ? 'bg-indigo-100 text-indigo-700'
                                : 'bg-white/20 text-white shadow-sm'
                            : isLight
                              ? 'text-slate-600 hover:bg-slate-200'
                              : 'text-slate-400 hover:bg-white/10 hover:text-white'}"
                    >
                        H2
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

                    <div
                        class="w-px h-4 {isLight
                            ? 'bg-slate-300'
                            : 'bg-white/10'} mx-1"
                    ></div>

                    <button
                        on:click={() =>
                            editor.chain().focus().toggleBold().run()}
                        class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5
                {editor.isActive('bold')
                            ? isLight
                                ? 'bg-indigo-100 text-indigo-700'
                                : 'bg-white/20 text-white shadow-sm'
                            : isLight
                              ? 'text-slate-600 hover:bg-slate-200'
                              : 'text-slate-400 hover:bg-white/10 hover:text-white'}"
                    >
                        Negrita
                    </button>

                    <button
                        on:click={() =>
                            editor.chain().focus().toggleItalic().run()}
                        class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5
                {editor.isActive('italic')
                            ? isLight
                                ? 'bg-indigo-100 text-indigo-700'
                                : 'bg-white/20 text-white shadow-sm'
                            : isLight
                              ? 'text-slate-600 hover:bg-slate-200'
                              : 'text-slate-400 hover:bg-white/10 hover:text-white'}"
                    >
                        Cursiva
                    </button>

                    <button
                        on:click={() =>
                            editor.chain().focus().toggleBulletList().run()}
                        class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all font-mono
                {editor.isActive('bulletList')
                            ? isLight
                                ? 'bg-indigo-100 text-indigo-700'
                                : 'bg-white/20 text-white shadow-sm'
                            : isLight
                              ? 'text-slate-600 hover:bg-slate-200'
                              : 'text-slate-400 hover:bg-white/10 hover:text-white'}"
                    >
                        Lista
                    </button>

                    <div class="flex-1"></div>

                    <button
                        on:click={savePDF}
                        class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5
                {isLight
                            ? 'text-slate-500 hover:text-red-600 hover:bg-red-50'
                            : 'text-slate-400 hover:text-white hover:bg-white/10'}"
                        title="Imprimir PDF"
                    >
                        <span>🖨️ PDF</span>
                    </button>

                    <button
                        on:click={downloadBackup}
                        class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5
                {isLight
                            ? 'text-slate-500 hover:text-emerald-600 hover:bg-emerald-50'
                            : 'text-slate-400 hover:text-white hover:bg-white/10'}"
                        title="Descargar Respaldo JSON"
                    >
                        <span>💾 Backup</span>
                    </button>
                {/if}
            </div>

            <!-- Editor Area -->
            <div
                class="flex-1 overflow-y-auto cursor-text p-6 md:p-8 outline-none"
                on:click={() => editor?.commands.focus()}
            >
                <div
                    bind:this={element}
                    class="prose prose-sm md:prose-base max-w-none h-full outline-none
            {isLight ? 'prose-slate' : 'prose-invert'}
             prose-p:leading-relaxed prose-headings:font-serif prose-headings:tracking-tight
             prose-a:text-indigo-400 prose-blockquote:border-l-4 prose-blockquote:border-indigo-500/50 prose-blockquote:pl-4 prose-blockquote:italic
            "
                ></div>
            </div>

            <!-- Status Bar -->
            <div
                class="px-4 py-2 text-[10px] flex justify-between items-center border-t select-none transition-colors
        {isLight
                    ? 'bg-slate-50 border-slate-200 text-slate-400'
                    : 'bg-black/20 border-white/5 text-slate-500'}"
            >
                <span>
                    {notes.length} nota{notes.length !== 1 ? "s" : ""} en tu cuaderno
                </span>
                <span class="font-mono opacity-50">
                    {editor?.storage.characterCount.words() || 0} palabras
                </span>
            </div>
        </div>
    {/if}
</div>

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

    /* FIX HEADINGS: Estilos por defecto (Dark Mode) - Se sobrescriben inline o por clase padre */
    :global(.ProseMirror h1) {
        font-size: 2.25rem !important;
        font-weight: 800 !important;
        margin-bottom: 1rem !important;
        line-height: 1.2;
    }
    :global(.ProseMirror h2) {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
        line-height: 1.3;
    }
    :global(.ProseMirror h3) {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        margin-top: 1.25rem !important;
        margin-bottom: 0.5rem !important;
        line-height: 1.4;
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

    /* Adaptación a Light Mode para tablas */
    :global(.light-theme .ProseMirror th) {
        background-color: #f1f5f9; /* Slate 100 */
        border-color: #cbd5e1; /* Slate 300 */
        color: #1e293b;
    }
    :global(.light-theme .ProseMirror td) {
        border-color: #cbd5e1;
        color: #334155;
    }

    /* Media Print para exportación limpia */
    @media print {
        @page {
            margin: 2cm;
            size: auto;
        }

        /* 1. RESET Y OCULTAMIENTO GLOBAL */
        :global(body),
        :global(#app) {
            background: white !important;
            margin: 0 !important;
            padding: 0 !important;
            visibility: hidden !important; /* Ocultar todo por defecto */
            height: auto !important;
            overflow: visible !important;
        }

        /* 2. MOSTRAR SOLO EL NOTEBOOK */
        :global(.notebook-container) {
            visibility: visible !important;
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
            background: white !important;
            display: block !important;
            box-shadow: none !important;
        }

        /* 3. PROPAGAR VISIBILIDAD A HIJOS */
        :global(.notebook-container *) {
            visibility: visible !important;
        }

        /* 4. OCULTAR UI INTERNA DEL NOTEBOOK (Botones, barras, etc.) */
        .toolbar,
        .flex.gap-2.p-3, /* Toolbar container class approximation */
        .flex.items-center.gap-2, /* Botones */
        .flex.justify-between.items-center.border-t, /* Status Bar */
        button {
            display: none !important;
        }

        /* Asegurar que el área del editor sea visible y limpia */
        .prose {
            padding: 0 !important;
            margin: 0 !important;
        }

        /* ... (rest of typo styles) ... */
        :global(.ProseMirror) {
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            box-shadow: none !important;
            color: black !important;
            font-family: "Georgia", "Times New Roman", serif !important;
            font-size: 11pt !important;
            line-height: 1.5 !important;
        }

        :global(.ProseMirror p) {
            color: black !important;
            margin-bottom: 0.3cm !important;
            text-align: justify !important;
        }

        :global(.ProseMirror h1) {
            font-family: "Arial", sans-serif !important;
            font-size: 18pt !important;
            font-weight: bold !important;
            color: black !important;
            margin-bottom: 0.5cm !important;
            border-bottom: 2px solid #000 !important;
            padding-bottom: 0.2cm !important;
        }
        :global(.ProseMirror h2) {
            font-family: "Arial", sans-serif !important;
            font-size: 14pt !important;
            margin-top: 0.5cm !important;
            color: #333 !important;
        }
        :global(.ProseMirror h3) {
            font-size: 12pt !important;
        }

        :global(.ProseMirror blockquote) {
            border-left: 3px solid #666 !important;
            margin-left: 0 !important;
            padding-left: 0.5cm !important;
            font-style: italic !important;
        }

        /* Ajustes de tabla para impresión */
        :global(.ProseMirror table),
        :global(.ProseMirror td),
        :global(.ProseMirror th) {
            border: 1px solid black !important;
            color: black !important;
            page-break-inside: avoid;
        }
    }
</style>
