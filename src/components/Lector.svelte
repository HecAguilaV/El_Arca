<script>
    import { onMount, onDestroy } from "svelte";
    import { archivoAbierto } from "../lib/stores";
    import toast from "svelte-french-toast";

    export let esClaro = false;

    const API_BASE_URL =
        import.meta.env.VITE_API_BASE_URL || "https://el-arca.onrender.com";

    let canvasRef;
    let pdfDoc = null;
    let pageNum = 1;
    let pageRendering = false;
    let pageNumPending = null;
    let scale = 1.0; // Escala más manejable para móviles
    let totalPages = 0;
    let cargando = true;
    let errorCarga = false;
    let errorMensaje = "";

    // Importamos PDF.js desde CDN para no engrosar build
    const PDFJS_URL =
        "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js";
    const WORKER_URL =
        "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

    function cerrar() {
        archivoAbierto.set(null);
    }

    $: urlArchivo = $archivoAbierto
        ? `${API_BASE_URL}/libros/ver/${$archivoAbierto.ruta}`
        : "";
    $: claseContenedor = esClaro ? "bg-stone-200" : "bg-black/95";

    onMount(async () => {
        if (
            !$archivoAbierto ||
            ($archivoAbierto.formato !== ".pdf" &&
                $archivoAbierto.formato !== "gdoc")
        ) {
            cargando = false;
            errorCarga = true;
            errorMensaje =
                "Formato no visualizable (" + $archivoAbierto.formato + ")";
            return;
        }

        try {
            // Cargar librería dinámicamente si no existe
            if (!window.pdfjsLib) {
                await cargarScript(PDFJS_URL);
            }
            window.pdfjsLib.GlobalWorkerOptions.workerSrc = WORKER_URL;

            // Instanciar document loading task
            const loadingTask = window.pdfjsLib.getDocument(urlArchivo);

            // Añadir listener de progreso opcional si se desea

            pdfDoc = await loadingTask.promise;
            totalPages = pdfDoc.numPages;
            cargando = false; // Solo aquí dejamos de cargar

            // Renderizar primera página
            renderPage(pageNum);
        } catch (e) {
            console.error("Error crítico cargando PDF:", e);
            errorCarga = true;
            errorMensaje = e.message || "Error desconocido";
            cargando = false;
            toast.error("Error cargando PDF: " + errorMensaje);
        }
    });

    function cargarScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement("script");
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    async function renderPage(num) {
        pageRendering = true;

        try {
            const page = await pdfDoc.getPage(num);

            // Ajustar escala al ancho del contenedor si es posible, sino default
            // Por simplicidad usamos scale fijo responsive después
            const viewport = page.getViewport({ scale: scale });
            const canvas = canvasRef;
            const context = canvas.getContext("2d");

            // HiDPI support
            const outputScale = window.devicePixelRatio || 1;

            canvas.height = Math.floor(viewport.height * outputScale);
            canvas.width = Math.floor(viewport.width * outputScale);

            // CSS scaling
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

            const renderTask = page.render(renderContext);

            await renderTask.promise;
            pageRendering = false;

            if (pageNumPending !== null) {
                renderPage(pageNumPending);
                pageNumPending = null;
            }
        } catch (e) {
            console.error("Error renderizando página:", e);
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
        if (pageNum <= 1) return;
        pageNum--;
        queueRenderPage(pageNum);
    }

    function onNextPage() {
        if (pageNum >= pdfDoc.numPages) return;
        pageNum++;
        queueRenderPage(pageNum);
    }

    function onZoomIn() {
        scale += 0.2;
        renderPage(pageNum);
    }

    function onZoomOut() {
        if (scale <= 0.4) return;
        scale -= 0.2;
        renderPage(pageNum);
    }
</script>

{#if $archivoAbierto}
    <div
        class="absolute inset-0 z-20 flex flex-col h-full w-full {claseContenedor} animate-in fade-in zoom-in duration-300"
    >
        <!-- Barra Superior -->
        <div
            class="flex-shrink-0 px-4 py-3 border-b {esClaro
                ? 'border-stone-300 bg-stone-100'
                : 'border-white/10 bg-[#1a1a20]'} flex justify-between items-center shadow-lg z-10"
        >
            <div class="flex flex-col overflow-hidden max-w-[50%]">
                <span
                    class="text-[9px] uppercase font-bold tracking-[0.2em] opacity-40 {esClaro
                        ? 'text-stone-800'
                        : 'text-slate-200'}">Lector PDF.js</span
                >
                <span
                    class="text-xs font-bold truncate {esClaro
                        ? 'text-stone-900'
                        : 'text-white'}"
                >
                    {$archivoAbierto.nombre}
                </span>
            </div>

            <div class="flex items-center gap-2">
                <!-- Controles de Paginación -->
                {#if !cargando && !errorCarga}
                    <div
                        class="hidden md:flex items-center gap-2 bg-black/10 rounded-lg px-2 py-1 mr-2"
                    >
                        <button
                            on:click={onPrevPage}
                            disabled={pageNum <= 1}
                            class="p-1 hover:text-indigo-500 disabled:opacity-30"
                            >◀</button
                        >
                        <span
                            class="text-[10px] font-mono min-w-[50px] text-center"
                            >{pageNum} / {totalPages}</span
                        >
                        <button
                            on:click={onNextPage}
                            disabled={pageNum >= totalPages}
                            class="p-1 hover:text-indigo-500 disabled:opacity-30"
                            >▶</button
                        >
                    </div>
                    <div
                        class="hidden md:flex items-center gap-2 bg-black/10 rounded-lg px-2 py-1 mr-4"
                    >
                        <button
                            on:click={onZoomOut}
                            class="text-xs font-bold p-1 hover:text-indigo-500"
                            >−</button
                        >
                        <button
                            on:click={onZoomIn}
                            class="text-xs font-bold p-1 hover:text-indigo-500"
                            >+</button
                        >
                    </div>
                {/if}

                <button
                    on:click={cerrar}
                    class="px-3 py-1.5 rounded-lg text-[10px] uppercase font-bold tracking-widest border {esClaro
                        ? 'border-stone-300 text-stone-600 hover:bg-stone-200'
                        : 'border-white/10 text-slate-400 hover:bg-white/5 bg-red-500/10 hover:bg-red-500/20 text-red-400'} transition-all"
                >
                    ✕ Cerrar
                </button>
            </div>
        </div>

        <!-- Área de Contenido -->
        <div
            class="flex-1 w-full relative overflow-auto flex justify-center bg-[#2a2a2e] p-4"
        >
            {#if cargando}
                <div
                    class="absolute inset-0 flex items-center justify-center text-white/50 flex-col gap-4"
                >
                    <div
                        class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"
                    ></div>
                    <span
                        class="text-[10px] uppercase font-bold tracking-widest"
                        >Cargando Documento...</span
                    >
                </div>
            {:else if errorCarga}
                <div
                    class="flex flex-col items-center justify-center text-center text-white/50 gap-4 mt-20"
                >
                    <p class="text-stone-300 font-serif text-xl italic mb-2">
                        Vista Previa No Disponible
                    </p>
                    <div
                        class="bg-black/30 p-4 rounded-xl border border-white/5 max-w-[80%]"
                    >
                        <p
                            class="text-xs uppercase font-bold tracking-widest opacity-60 mb-2"
                        >
                            Razón:
                        </p>
                        <code class="text-xs text-red-300 block mb-4"
                            >{errorMensaje ||
                                "Formato no soportado por el visor web"}</code
                        >
                        <p class="text-[10px] opacity-50">
                            Archivos Word, Powerpoint o imágenes deben
                            descargarse.
                        </p>
                    </div>

                    <a
                        href={urlArchivo}
                        download
                        class="mt-4 px-6 py-3 bg-indigo-600 text-white rounded-xl text-xs uppercase font-bold tracking-widest hover:bg-indigo-500 transition-all shadow-lg hover:shadow-indigo-500/20"
                        >Descargar Archivo</a
                    >
                </div>
            {:else}
                <!-- Canvas Wrapper -->
                <div class="relative shadow-2xl">
                    <canvas
                        bind:this={canvasRef}
                        class="max-w-full h-auto bg-white"
                    ></canvas>
                </div>

                <!-- Controles Móviles Flotantes -->
                <div
                    class="md:hidden fixed bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-4 bg-black/80 text-white px-4 py-2 rounded-full backdrop-blur-md shadow-xl border border-white/10 z-50"
                >
                    <button
                        on:click={onPrevPage}
                        disabled={pageNum <= 1}
                        class="text-xl p-2 active:scale-95 disabled:opacity-30"
                        >‹</button
                    >
                    <span class="text-xs font-mono">{pageNum}/{totalPages}</span
                    >
                    <button
                        on:click={onNextPage}
                        disabled={pageNum >= totalPages}
                        class="text-xl p-2 active:scale-95 disabled:opacity-30"
                        >›</button
                    >
                </div>
            {/if}
        </div>
    </div>
{/if}
