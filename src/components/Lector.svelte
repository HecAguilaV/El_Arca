<script>
    import { onMount, tick } from "svelte";
    import { archivoAbierto } from "../lib/stores";
    import toast from "svelte-french-toast";
    import mammoth from "mammoth";

    export let esClaro = false;

    const API_BASE_URL =
        import.meta.env.VITE_API_BASE_URL || "https://el-arca.onrender.com";

    let canvasRef;
    let containerRef;
    let pdfDoc = null;
    let pageNum = 1;
    let pageRendering = false;
    let pageNumPending = null;
    let scale = 1.0;
    let totalPages = 0;
    let cargando = true;
    let errorCarga = false;
    let errorMensaje = "";

    // Contenido HTML para DOCX
    let docxHtmlContent = "";
    // Estado para tipo de visor
    let tipoVisor = "pdf"; // pdf, docx, error

    // URLs de PDF.js (CDN)
    const PDFJS_URL =
        "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js";
    const WORKER_URL =
        "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

    function cerrar() {
        archivoAbierto.set(null);
    }

    $: if ($archivoAbierto) {
        cargarDocumento();
    }

    // Reactividad para estilos
    $: claseContenedor = esClaro ? "bg-stone-50" : "bg-[#1a1a1a]";
    $: claseTexto = esClaro ? "text-stone-800" : "text-stone-300";

    async function cargarDocumento() {
        if (!$archivoAbierto) return;

        cargando = true;
        errorCarga = false;
        errorMensaje = "";
        docxHtmlContent = "";
        pdfDoc = null;
        pageNum = 1;
        scale = 1.0;

        const urlArchivo = `${API_BASE_URL}/libros/ver/${$archivoAbierto.ruta}`;
        const extension = $archivoAbierto.formato?.toLowerCase() || "";

        try {
            if (extension === ".pdf") {
                tipoVisor = "pdf";
                await cargarPDF(urlArchivo);
            } else if (extension === ".docx") {
                tipoVisor = "docx";
                await cargarDOCX(urlArchivo);
            } else if (extension === ".pptx" || extension === ".ppt") {
                // Fallback mejorado para PPT
                throw new Error(
                    "PowerPoint requiere descarga o conversión externa.",
                );
            } else {
                throw new Error(
                    `Formato ${extension} no soportado por el visor web.`,
                );
            }
        } catch (e) {
            console.error("Error cargando documento:", e);
            errorCarga = true;
            errorMensaje = e.message;
            cargando = false;
            toast.error(
                "No se pudo cargar: " + (e.message || "Error desconocido"),
            );
        }
    }

    // --- LOGICA PDF ---
    async function cargarPDF(url) {
        if (!window.pdfjsLib) {
            await cargarScript(PDFJS_URL);
        }
        window.pdfjsLib.GlobalWorkerOptions.workerSrc = WORKER_URL;

        try {
            const loadingTask = window.pdfjsLib.getDocument(url);
            pdfDoc = await loadingTask.promise;
            totalPages = pdfDoc.numPages;
            cargando = false;
            // Esperar tick para que exista canvas
            await tick();
            setTimeout(() => renderPage(pageNum), 100);
        } catch (e) {
            throw new Error("Error leyendo estructura PDF: " + e.message);
        }
    }

    async function renderPage(num) {
        if (!pdfDoc || !canvasRef) return;

        pageRendering = true;
        try {
            const page = await pdfDoc.getPage(num);

            // Calculamos scale basado en el ancho del contenedor si existe
            let finalScale = scale;
            if (containerRef) {
                const viewportOriginal = page.getViewport({ scale: 1.0 });
                const containerWidth = containerRef.clientWidth - 40; // padding
                if (
                    containerWidth > 0 &&
                    viewportOriginal.width > containerWidth
                ) {
                    // Ajustar si es muy grande
                }
            }

            const viewport = page.getViewport({ scale: finalScale });
            const canvas = canvasRef;
            const context = canvas.getContext("2d");

            const outputScale = window.devicePixelRatio || 1;

            canvas.height = Math.floor(viewport.height * outputScale);
            canvas.width = Math.floor(viewport.width * outputScale);
            canvas.style.height = Math.floor(viewport.height) + "px";
            canvas.style.width = Math.floor(viewport.width) + "px";

            const transform =
                outputScale !== 1
                    ? [outputScale, 0, 0, outputScale, 0, 0]
                    : null;

            const renderContext = {
                canvasContext: context,
                transform: transform,
                viewport: viewport,
            };

            await page.render(renderContext).promise;
            pageRendering = false;

            if (pageNumPending !== null) {
                renderPage(pageNumPending);
                pageNumPending = null;
            }
        } catch (e) {
            console.error("Render error", e);
            pageRendering = false;
        }
    }

    function queueRenderPage(num) {
        if (pageRendering) {
            pageNumPending = num;
        } else {
            renderPage(num);
        }
    }

    function onPrevPage() {
        if (pageNum > 1) {
            pageNum--;
            queueRenderPage(pageNum);
        }
    }
    function onNextPage() {
        if (pageNum < totalPages) {
            pageNum++;
            queueRenderPage(pageNum);
        }
    }
    function onZoomIn() {
        scale += 0.2;
        renderPage(pageNum);
    }
    function onZoomOut() {
        if (scale > 0.4) {
            scale -= 0.2;
            renderPage(pageNum);
        }
    }

    // --- LOGICA DOCX ---
    async function cargarDOCX(url) {
        // Fetch del blob
        const response = await fetch(url);
        if (!response.ok)
            throw new Error("No se pudo descargar el archivo DOCX");
        const arrayBuffer = await response.arrayBuffer();

        // Convertir a HTML usando Mammoth
        const result = await mammoth.convertToHtml({
            arrayBuffer: arrayBuffer,
        });
        docxHtmlContent = result.value;
        if (result.messages.length > 0)
            console.warn("Mammoth warnings:", result.messages);

        cargando = false;
    }

    function cargarScript(src) {
        return new Promise((resolve, reject) => {
            if (document.querySelector(`script[src="${src}"]`))
                return resolve();
            const script = document.createElement("script");
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
</script>

<div
    class="flex flex-col h-full w-full {claseContenedor} animate-in fade-in duration-300 relative rounded-xl overflow-hidden shadow-2xl border border-white/5"
>
    <!-- Barra Superior -->
    <div
        class="flex-shrink-0 px-4 py-3 border-b border-black/5 dark:border-white/5 flex justify-between items-center bg-white/50 dark:bg-black/20 backdrop-blur-md z-10"
    >
        <div class="flex flex-col max-w-[40%]">
            <span class="text-[9px] uppercase font-bold opacity-40"
                >Visor de Documentos</span
            >
            <span
                class="text-xs font-bold truncate {$archivoAbierto
                    ? 'opacity-100'
                    : 'opacity-0'}"
            >
                {$archivoAbierto ? $archivoAbierto.nombre : "..."}
            </span>
        </div>

        <div class="flex items-center gap-2">
            {#if tipoVisor === "pdf" && !cargando && !errorCarga}
                <div
                    class="hidden md:flex items-center gap-1 bg-black/5 dark:bg-white/10 rounded-lg px-2 py-1 mr-2"
                >
                    <button
                        start-icon
                        on:click={onPrevPage}
                        disabled={pageNum <= 1}
                        class="p-1 hover:text-indigo-500 disabled:opacity-30"
                        >◀</button
                    >
                    <span class="text-[10px] font-mono min-w-[40px] text-center"
                        >{pageNum} / {totalPages}</span
                    >
                    <button
                        on:click={onNextPage}
                        disabled={pageNum >= totalPages}
                        class="p-1 hover:text-indigo-500 disabled:opacity-30"
                        >▶</button
                    >
                    <div class="w-px h-3 bg-current opacity-20 mx-1"></div>
                    <button
                        on:click={onZoomOut}
                        class="text-xs p-1 hover:text-indigo-500">−</button
                    >
                    <button
                        on:click={onZoomIn}
                        class="text-xs p-1 hover:text-indigo-500">+</button
                    >
                </div>
            {/if}

            <a
                href={$archivoAbierto
                    ? `${API_BASE_URL}/libros/ver/${$archivoAbierto.ruta}`
                    : "#"}
                download
                class="p-2 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
                title="Descargar Original"
            >
                ⬇️
            </a>

            <button
                on:click={cerrar}
                class="px-3 py-1.5 rounded-lg text-[10px] uppercase font-bold tracking-widest bg-red-500/10 text-red-500 hover:bg-red-500 hover:text-white transition-all"
            >
                Cerrar
            </button>
        </div>
    </div>

    <!-- Area Principal -->
    <div
        bind:this={containerRef}
        class="flex-1 w-full overflow-auto relative p-4"
    >
        {#if cargando}
            <div
                class="absolute inset-0 flex flex-col items-center justify-center gap-3"
            >
                <div
                    class="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"
                ></div>
                <span class="text-[10px] uppercase tracking-widest opacity-50"
                    >Procesando...</span
                >
            </div>
        {:else if errorCarga}
            <div
                class="flex flex-col items-center justify-center h-full text-center p-8 opacity-60"
            >
                <p class="text-3xl mb-2">📂</p>
                <p class="text-sm font-bold mb-1">
                    No se puede visualizar aquí
                </p>
                <p class="text-xs opacity-70 mb-4 max-w-md">{errorMensaje}</p>
                <a
                    href={`${API_BASE_URL}/libros/ver/${$archivoAbierto.ruta}`}
                    target="_blank"
                    class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-bold shadow-lg hover:bg-indigo-500 transition-all"
                >
                    Abrir / Descargar Externa
                </a>
            </div>
        {:else if tipoVisor === "pdf"}
            <div class="flex justify-center min-h-full">
                <canvas bind:this={canvasRef} class="shadow-lg max-w-full"
                ></canvas>
            </div>
        {:else if tipoVisor === "docx"}
            <div
                class="max-w-3xl mx-auto bg-white text-black p-8 md:p-12 shadow-xl min-h-full prose prose-sm md:prose-base"
            >
                {@html docxHtmlContent}
            </div>
        {/if}
    </div>
</div>

<style>
    /* Estilos basicos para el HTML de mammoth */
    :global(.prose p) {
        margin-bottom: 1em;
        line-height: 1.6;
    }
    :global(.prose h1, .prose h2, .prose h3) {
        margin-top: 1.5em;
        margin-bottom: 0.5em;
        font-weight: bold;
    }
    :global(.prose ul) {
        list-style-type: disc;
        padding-left: 1.5em;
    }
    :global(.prose ol) {
        list-style-type: decimal;
        padding-left: 1.5em;
    }
</style>
