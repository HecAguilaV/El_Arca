<script>
  import { onMount, onDestroy } from "svelte";
  import Stats from "./components/Stats.svelte";
  import Table from "./components/Table.svelte";
  import { Toaster } from "svelte-french-toast";
  import Notebook from "./components/Notebook.svelte";
  import AiAssistant from "./components/AiAssistant.svelte";
  import ArcaLogo from "./components/ArcaLogo.svelte";

  // Importar música local
  import ambientMusic from "./assets/Jafar Idris - His Eye Is on the Sparrow.mp3";

  let data = [];
  let loading = true;

  // Tabs Principales (Móvil)
  let activeTab = "library"; // 'library' | 'notebook'
  // Tabs Columna Derecha (Desktop)
  let rightTab = "notebook"; // 'notebook' | 'assistant'

  // Tiempo y Fecha
  let currentTime = new Date();
  let timeInterval;

  // Tema Dinámico
  let theme = "night"; // 'morning' | 'afternoon' | 'night'

  // Temporizador
  let timerActive = false;
  let timerSeconds = 45 * 60; // 45 min default
  let timerInterval;

  // Música
  let isPaused = true;
  $: isPlaying = !isPaused;

  function updateTheme(hour) {
    if (hour >= 6 && hour < 12) theme = "morning";
    else if (hour >= 12 && hour < 21) theme = "afternoon";
    else theme = "night";
  }

  onMount(async () => {
    timeInterval = setInterval(() => {
      currentTime = new Date();
      updateTheme(currentTime.getHours());
    }, 1000);
    updateTheme(currentTime.getHours());

    try {
      const res = await fetch("/data.json");
      data = await res.json();
    } catch (e) {
      console.error("Error loading data:", e);
    } finally {
      loading = false;
    }
  });

  onDestroy(() => {
    clearInterval(timeInterval);
    stopTimer();
  });

  // Lógica del Temporizador
  function toggleTimer() {
    if (timerActive) {
      stopTimer();
    } else {
      timerActive = true;
      timerInterval = setInterval(() => {
        if (timerSeconds > 0) timerSeconds--;
        else stopTimer(); // Alarma visual aquí
      }, 1000);
    }
  }

  function stopTimer() {
    timerActive = false;
    clearInterval(timerInterval);
    if (timerSeconds === 0) timerSeconds = 45 * 60; // Reset
  }

  function formatTimer(sec) {
    const m = Math.floor(sec / 60)
      .toString()
      .padStart(2, "0");
    const s = (sec % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  }

  // Clases dinámicas de fondo
  $: bgClass =
    theme === "morning"
      ? "from-amber-900/40 to-orange-900/40"
      : theme === "afternoon"
        ? "from-blue-900/40 to-cyan-900/40"
        : "from-indigo-900/40 to-purple-900/40"; // Night default
</script>

<div
  class="min-h-screen transition-colors duration-1000 bg-gradient-to-br {bgClass} text-slate-200 font-sans selection:bg-indigo-500/30"
>
  <div
    class="max-w-[1920px] mx-auto p-4 md:p-6 lg:p-8 flex flex-col h-screen overflow-hidden"
  >
    <!-- HEADER -->
    <header
      class="flex flex-col md:flex-row justify-between items-center mb-6 gap-4 flex-shrink-0"
    >
      <!-- Logo & Nav -->
      <div
        class="flex items-center gap-6 w-full md:w-auto justify-between md:justify-start"
      >
        <div class="flex items-center gap-3">
          <ArcaLogo size="w-10 h-10" color="text-white" />
          <div>
            <h1
              class="text-2xl md:text-3xl font-bold text-white tracking-tight leading-none"
            >
              El Arca
            </h1>
            <span
              class="text-[10px] md:text-xs text-white/50 uppercase tracking-widest"
              >Biblioteca Digital</span
            >
          </div>
        </div>

        <!-- Navigation Tabs (SOLO MÓVIL) -->
        <nav
          class="flex md:hidden bg-black/20 p-1 rounded-xl backdrop-blur-md border border-white/5"
        >
          <button
            on:click={() => (activeTab = "library")}
            class="px-4 py-1.5 rounded-lg text-xs font-medium transition-all {activeTab ===
            'library'
              ? 'bg-white/10 text-white shadow-sm'
              : 'text-slate-400'}"
          >
            Biblioteca
          </button>
          <button
            on:click={() => (activeTab = "notebook")}
            class="px-4 py-1.5 rounded-lg text-xs font-medium transition-all {activeTab ===
            'notebook'
              ? 'bg-white/10 text-white shadow-sm'
              : 'text-slate-400'}"
          >
            Cuaderno
          </button>
        </nav>
      </div>

      <!-- Widgets -->
      <div class="flex items-center gap-4 md:gap-6">
        <!-- Ambient Music Widget -->
        <div class="flex items-center gap-2">
          <button
            on:click={() => (isPaused = !isPaused)}
            class="group flex items-center gap-2 bg-black/20 hover:bg-black/30 px-3 py-1.5 md:px-4 md:py-2 rounded-xl text-sm font-mono transition-all border border-white/5 hover:border-white/20 {isPlaying
              ? 'ring-2 ring-emerald-500/50'
              : ''}"
            title={isPlaying ? "Pausar Ambiente" : "Reproducir Ambiente"}
          >
            <span
              class={isPlaying
                ? "animate-pulse text-emerald-400"
                : "text-slate-500"}>🎵</span
            >
          </button>
          <audio bind:paused={isPaused} loop src={ambientMusic}></audio>
        </div>

        <!-- Timer Widget -->
        <button
          on:click={toggleTimer}
          class="group flex items-center gap-2 md:gap-3 bg-black/20 hover:bg-black/30 px-3 py-1.5 md:px-4 md:py-2 rounded-xl text-sm font-mono transition-all border border-white/5 hover:border-white/20 {timerActive
            ? 'ring-2 ring-indigo-500/50'
            : ''}"
        >
          <span
            class={timerActive
              ? "animate-pulse text-indigo-400"
              : "text-slate-500"}>⏱️</span
          >
          <span
            class="text-lg md:text-xl font-bold {timerActive
              ? 'text-indigo-100'
              : 'text-slate-300'}"
          >
            {formatTimer(timerSeconds)}
          </span>
        </button>

        <!-- Clock Widget -->
        <div class="text-right hidden md:block">
          <div class="text-2xl font-bold text-white leading-none">
            {currentTime.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
          <div
            class="text-xs text-slate-400 font-medium uppercase tracking-wider mt-1"
          >
            {currentTime.toLocaleDateString([], {
              weekday: "long",
              day: "numeric",
              month: "short",
            })}
          </div>
        </div>
      </div>
    </header>

    <!-- CONTENT GRID -->
    <main class="flex-1 overflow-hidden grid md:grid-cols-2 gap-6 relative">
      <!-- COLUMN 1: LIBRARY (Visible in Mobile if Tab=Library, Always in Desktop) -->
      <div
        class="flex-col gap-6 overflow-hidden h-full {activeTab === 'library'
          ? 'flex'
          : 'hidden md:flex'}"
      >
        {#if loading}
          <div class="flex-1 flex items-center justify-center">
            <div class="text-xl text-white/50 animate-pulse font-light">
              Cargando la cuenca de datos...
            </div>
          </div>
        {:else}
          <!-- Stats Compactos -->
          <div class="flex-shrink-0">
            <Stats {data} />
          </div>
          <!-- Tabla con Scroll Independiente -->
          <div
            class="flex-1 overflow-hidden rounded-xl border border-white/10 bg-black/10 backdrop-blur-sm"
          >
            <Table {data} />
          </div>
        {/if}
      </div>

      <!-- COLUMN 2: RIGHT PANEL (Notebook & AI) -->
      <div
        class="flex-col gap-4 overflow-hidden h-full {activeTab === 'notebook'
          ? 'flex'
          : 'hidden md:flex'}"
      >
        <!-- Pestañas Superiores para el Panel Derecho -->
        <div
          class="flex bg-black/20 p-1 rounded-xl backdrop-blur-md border border-white/5 shrink-0 self-start"
        >
          <button
            on:click={() => (rightTab = "notebook")}
            class="px-4 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-2 {rightTab ===
            'notebook'
              ? 'bg-white/10 text-white shadow-sm'
              : 'text-slate-400 hover:text-white'}"
          >
            <span>📝</span> Cuaderno
          </button>
          <button
            on:click={() => (rightTab = "assistant")}
            class="px-4 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-2 {rightTab ===
            'assistant'
              ? 'bg-white/10 text-white shadow-sm'
              : 'text-slate-400 hover:text-white'}"
          >
            <span>🤖</span> Asistente IA
          </button>
        </div>

        <div class="flex-1 h-full relative overflow-hidden">
          {#if rightTab === "notebook"}
            <div class="h-full w-full absolute inset-0">
              <Notebook />
            </div>
          {:else}
            <div class="h-full w-full absolute inset-0">
              <AiAssistant />
            </div>
          {/if}
        </div>
      </div>
    </main>

    <!-- FOOTER -->
    <footer
      class="mt-4 text-center text-[10px] text-slate-400 font-medium tracking-wide flex items-center justify-center gap-2 opacity-80 hover:opacity-100 transition-opacity pb-2"
    >
      <span>&copy; {new Date().getFullYear()} Héctor Aguila</span>
      <span>•</span>
      <span class="flex items-center gap-1">
        Un Soñador con Poca Ram
        <span class="text-base" title="Dev Mode">👨🏻‍💻</span>
      </span>
    </footer>
  </div>
</div>

<Toaster />

<style>
  /* Scrollbar estilizado */
  ::-webkit-scrollbar {
    width: 8px;
  }
  ::-webkit-scrollbar-track {
    background: transparent;
  }
  ::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
</style>
