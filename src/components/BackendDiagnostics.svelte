<script>
    import { onMount } from "svelte";
    import { fade, slide } from "svelte/transition";
    import {
        CheckCircle,
        Warning,
        Spinner,
        Database,
        Files,
        Cpu,
    } from "phosphor-svelte";
    import toast from "svelte-french-toast";

    export let isOpen = false;
    export let onClose;

    let status = "checking"; // checking, online, offline
    let scanResult = null;
    let analyzing = false;
    let analyzedCount = 0;

    // URL del Backend (Hardcoded por ahora para dev)
    const BACKEND_URL = "http://localhost:8000";

    async function checkStatus() {
        status = "checking";
        try {
            const res = await fetch(`${BACKEND_URL}/`);
            if (res.ok) {
                status = "online";
                scanLibrary();
            } else {
                status = "offline";
            }
        } catch (e) {
            status = "offline";
            console.error(e);
        }
    }

    async function scanLibrary() {
        try {
            const res = await fetch(`${BACKEND_URL}/scan`);
            scanResult = await res.json();
            toast.success("Biblioteca escaneada correctamente");
        } catch (e) {
            toast.error("Error al escanear biblioteca");
        }
    }

    async function analyzeDeeply() {
        if (!scanResult || !scanResult.files) return;
        analyzing = true;
        analyzedCount = 0;

        // Simulamos análisis real iterando sobre una muestra
        // En producción esto debería ser un Job de fondo o paginado
        const filesToAnalyze = scanResult.files.slice(0, 10); // Demo first 10

        for (const file of filesToAnalyze) {
            try {
                // Encode path safely
                const encodedPath = encodeURIComponent(file.path);
                // POST para analizar (enviar path relativo)
                await fetch(`${BACKEND_URL}/analyze?file_path=${encodedPath}`, {
                    method: "POST",
                });
                analyzedCount++;
            } catch (e) {
                console.error(e);
            }
        }
        analyzing = false;
        toast.success("Análisis de muestra completado");
    }

    onMount(() => {
        if (isOpen) checkStatus();
    });

    $: if (isOpen) checkStatus();
</script>

{#if isOpen}
    <div
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        transition:fade
    >
        <div
            class="bg-white dark:bg-[#1a1a20] w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]"
        >
            <!-- Header -->
            <div
                class="p-6 border-b border-gray-100 dark:border-white/5 flex justify-between items-center"
            >
                <h2
                    class="text-xl font-bold flex items-center gap-3 dark:text-white text-slate-800"
                >
                    <Cpu size={24} class="text-indigo-500" />
                    Diagnóstico del Sistema ("El Cerebro")
                </h2>
                <button
                    on:click={onClose}
                    class="p-2 hover:bg-gray-100 dark:hover:bg-white/5 rounded-full transition-colors"
                >
                    ✕
                </button>
            </div>

            <!-- Body -->
            <div class="p-6 flex-1 overflow-y-auto space-y-6">
                <!-- Status Section -->
                <div
                    class="flex items-center gap-4 p-4 rounded-xl border {status ===
                    'online'
                        ? 'bg-emerald-50 border-emerald-100 dark:bg-emerald-900/20 dark:border-emerald-500/30'
                        : 'bg-red-50 border-red-100 dark:bg-red-900/20 dark:border-red-500/30'}"
                >
                    {#if status === "checking"}
                        <Spinner
                            class="animate-spin text-indigo-500"
                            size={24}
                        />
                        <span class="font-medium text-indigo-500"
                            >Conectando con el Núcleo...</span
                        >
                    {:else if status === "online"}
                        <CheckCircle
                            class="text-emerald-500"
                            size={24}
                            weight="fill"
                        />
                        <div>
                            <h3
                                class="font-bold text-emerald-700 dark:text-emerald-400"
                            >
                                Sistema Operativo
                            </h3>
                            <p
                                class="text-xs text-emerald-600 dark:text-emerald-500"
                            >
                                Conexión establecida con Python Backend (v1.0.0)
                            </p>
                        </div>
                    {:else}
                        <Warning class="text-red-500" size={24} weight="fill" />
                        <div>
                            <h3
                                class="font-bold text-red-700 dark:text-red-400"
                            >
                                Sistema Desconectado
                            </h3>
                            <p class="text-xs text-red-600 dark:text-red-500">
                                Asegúrate de ejecutar <code
                                    >Start-Brain.ps1</code
                                >
                            </p>
                        </div>
                        <button
                            on:click={checkStatus}
                            class="text-xs bg-white border border-red-200 px-2 py-1 rounded ml-auto hover:bg-red-50 text-red-700"
                            >Reintentar</button
                        >
                    {/if}
                </div>

                <!-- Scan Results -->
                {#if scanResult}
                    <div class="grid grid-cols-2 gap-4" transition:slide>
                        <div
                            class="p-4 rounded-xl bg-gray-50 dark:bg-white/5 border dark:border-white/5"
                        >
                            <div
                                class="flex items-center gap-2 mb-2 text-slate-500 dark:text-slate-400 text-sm font-medium"
                            >
                                <Files size={18} /> Total Archivos Detectados
                            </div>
                            <div
                                class="text-3xl font-bold text-slate-800 dark:text-white"
                            >
                                {scanResult.count}
                            </div>
                        </div>
                        <div
                            class="p-4 rounded-xl bg-gray-50 dark:bg-white/5 border dark:border-white/5"
                        >
                            <div
                                class="flex items-center gap-2 mb-2 text-slate-500 dark:text-slate-400 text-sm font-medium"
                            >
                                <Database size={18} /> Tamaño Total (Est.)
                            </div>
                            <!-- Calculo simple de tamaño -->
                            <div
                                class="text-3xl font-bold text-slate-800 dark:text-white"
                            >
                                {(
                                    scanResult.files.reduce(
                                        (acc, curr) => acc + curr.size,
                                        0,
                                    ) /
                                    (1024 * 1024)
                                ).toFixed(1)} MB
                            </div>
                        </div>
                    </div>

                    <!-- Lista de Archivos (Preview) -->
                    <div>
                        <h3
                            class="text-sm font-bold uppercase tracking-wider text-slate-500 mb-3"
                        >
                            Muestra de Archivos (Últimos 100)
                        </h3>
                        <div
                            class="h-48 overflow-y-auto border rounded-lg bg-gray-50 dark:bg-black/20 text-xs font-mono p-2 space-y-1"
                        >
                            {#each scanResult.files as file}
                                <div
                                    class="flex justify-between text-slate-600 dark:text-slate-400 hover:bg-black/5 p-1 rounded cursor-pointer"
                                    title={file.full_path}
                                >
                                    <span class="truncate w-3/4"
                                        >{file.filename}</span
                                    >
                                    <span class="opacity-50"
                                        >{file.extension}</span
                                    >
                                </div>
                            {/each}
                        </div>
                    </div>

                    <!-- Deep Analysis Action -->
                    <div class="border-t pt-6 dark:border-white/10">
                        <h3
                            class="text-sm font-bold text-slate-800 dark:text-white mb-2"
                        >
                            Análisis Profundo (Contenido & Duplicados)
                        </h3>
                        <p class="text-xs text-slate-500 mb-4">
                            Esta operación lee el contenido real de los archivos
                            PDF/DOCX para indexarlos en la IA.
                        </p>

                        {#if analyzing}
                            <div
                                class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700 mb-2"
                            >
                                <div
                                    class="bg-indigo-600 h-2.5 rounded-full transition-all duration-300"
                                    style="width: {(analyzedCount / 10) * 100}%"
                                ></div>
                            </div>
                            <p
                                class="text-center text-xs text-indigo-400 animate-pulse"
                            >
                                Analizando documentos... ({analyzedCount}/10
                                Muestra)
                            </p>
                        {:else}
                            <button
                                on:click={analyzeDeeply}
                                class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold shadow-lg shadow-indigo-500/20 transition-all flex justify-center items-center gap-2"
                            >
                                <Cpu size={20} weight="fill" />
                                Ejecutar Análisis de Contenido
                            </button>
                        {/if}
                    </div>
                {/if}
            </div>
        </div>
    </div>
{/if}
