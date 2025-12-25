<script>
  import { onMount, onDestroy } from "svelte";
  import Stats from "./components/Stats.svelte";
  import Table from "./components/Table.svelte";
  import { Toaster } from "svelte-french-toast";
  import Notebook from "./components/Notebook.svelte";
  import AiAssistant from "./components/AiAssistant.svelte";
  import BibleWidget from "./components/BibleWidget.svelte";
  import ArcaLogo from "./components/ArcaLogo.svelte";
  import BackendDiagnostics from "./components/BackendDiagnostics.svelte";
  import {
    MusicNotes,
    Timer,
    NotePencil,
    ChatCircleText,
    BookOpen,
    Books,
    Laptop,
    Sun,
    Moon,
    MagicWand as Auto,
    CloudArrowUp,
  } from "phosphor-svelte";

  const DRIVE_URL =
    import.meta.env.VITE_GOOGLE_DRIVE_URL || "https://drive.google.com";

  // Música local (referencia directa a public/)
  const ambientMusic = "/ambient.mp3";

  let data = [];
  let loading = true;
  let showDiagnostics = false;
  let userName = localStorage.getItem("arca_username") || "";

  // Tabs Principales (Móvil)
  let activeTab = "library"; // 'library' | 'notebook'
  // Tabs Columna Derecha (Desktop)
  let rightTab = "notebook"; // 'notebook' | 'assistant'

  // Tiempo y Fecha
  let currentTime = new Date();
  let timeInterval;

  // Tema Dinámico
  let theme = "night"; // 'morning' | 'afternoon' | 'night'
  let manualOverride = null; // null (Auto) | 'light' | 'dark'

  // Temporizador
  let timerActive = false;
  let timerSeconds = 45 * 60; // 45 min default
  let timerInterval;

  // Música
  let isPaused = true;
  $: isPlaying = !isPaused;
  let audioElement;
  let volume = 0; // Control de volumen reactivo
  let fadeInterval;

  // Lógica de Fade-In Real
  function toggleMusic() {
    if (isPaused) {
      // Iniciar reproducción
      isPaused = false;
      // volume = 0; // Ya se controla en el intervalo si hiciera falta resetear
      // Resetear volumen a 0 para fade in
      if (audioElement) {
        audioElement.volume = 0;
        volume = 0;
      }

      // Ramp up
      clearInterval(fadeInterval);
      fadeInterval = setInterval(() => {
        if (audioElement && audioElement.volume < 0.5) {
          // Max volumen 50%
          let newVol = Math.min(0.5, audioElement.volume + 0.02);
          audioElement.volume = newVol;
          volume = newVol; // Sync local state variable just in case
        } else {
          clearInterval(fadeInterval);
        }
      }, 100);
    } else {
      // Pausa inmediata
      isPaused = true;
      clearInterval(fadeInterval);
    }
  }

  function updateTheme(hour) {
    if (hour >= 6 && hour < 12) theme = "morning";
    else if (hour >= 12 && hour < 21) theme = "afternoon";
    else theme = "night";
  }

  // Lógica de Toggle Manual
  function toggleTheme() {
    if (manualOverride === null) manualOverride = "light";
    else if (manualOverride === "light") manualOverride = "dark";
    else manualOverride = null; // Back to Auto
  }

  import WelcomeModal from "./components/WelcomeModal.svelte";

  // UI State
  let showMobileMenu = false;
  let showStats = false;
  let showWelcomeModal = false;

  onMount(async () => {
    // Verificar Nombre
    setTimeout(() => {
      if (!userName || userName === "Estudiante" || userName.trim() === "") {
        showWelcomeModal = true;
      }
    }, 500);

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

  function handleWelcomeSave(event) {
    userName = event.detail;
    localStorage.setItem("arca_username", userName);
    showWelcomeModal = false;
  }

  onDestroy(() => {
    clearInterval(timeInterval);
    stopTimer();
    clearInterval(fadeInterval);
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

  // Clases dinámicas de fondo (Estilo "Logos Lite" + "Night Mode")
  $: effectiveTheme = manualOverride || theme;
  $: isLight =
    effectiveTheme === "morning" ||
    effectiveTheme === "afternoon" ||
    effectiveTheme === "light";

  // Fondo: Día = Stone-200 (Cálido y mate, evita el resplandor) / Noche = Indigo Profundo
  $: bgClass = isLight
    ? "bg-[#e7e5e4]" // Stone-200: Un gris cálido estilo "papel reciclado" que no quema la vista
    : "bg-[#0f0f13]";

  // Icono del botón de tema
  $: ThemeIcon =
    manualOverride === "light" ? Sun : manualOverride === "dark" ? Moon : Auto;

  // Textos Base (Stone-800 para suavizar el negro puro)
  $: textClass = isLight ? "text-stone-800" : "text-slate-200";
  // Textos Secundarios
  $: subTextClass = isLight ? "text-stone-500" : "text-slate-400";
  // Bordes / Separadores
  $: borderClass = isLight ? "border-stone-300" : "border-white/10";
  // Contenedores (Stone-50: Blanco roto)
  $: cardClass = isLight
    ? "bg-[#fafaf9] border-stone-300 shadow-sm" // Stone-50
    : "bg-white/5 border-white/10";
  // Hover botones
  $: hoverClass = isLight ? "hover:bg-slate-100" : "hover:bg-white/5";
</script>

<div
  class="min-h-screen transition-colors duration-700 {bgClass} {textClass} font-sans selection:bg-indigo-500/30"
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
          <!-- Logo adaptable al tema -->
          <ArcaLogo
            size="w-10 h-10"
            color={isLight ? "text-indigo-900" : "text-white"}
          />
          <div>
            <h1
              class="text-2xl md:text-3xl font-bold tracking-tight leading-none {isLight
                ? 'text-indigo-950'
                : 'text-white'}"
            >
              El Arca
            </h1>
            <span
              class="text-[10px] md:text-xs uppercase tracking-widest {subTextClass}"
              >Biblioteca Digital {userName ? `- ${userName}` : ""}</span
            >
          </div>
        </div>

        <!-- Navigation Tabs (SOLO MÓVIL) -->
        <nav
          class="flex md:hidden p-1 rounded-xl backdrop-blur-md border {borderClass} {isLight
            ? 'bg-white/50'
            : 'bg-black/20'}"
        >
          <button
            on:click={() => (activeTab = "library")}
            class="px-4 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-2 {activeTab ===
            'library'
              ? isLight
                ? 'bg-indigo-100 text-indigo-900 shadow-sm'
                : 'bg-white/10 text-white shadow-sm'
              : subTextClass}"
          >
            <Books size={16} /> Biblioteca
          </button>
          <button
            on:click={() => (activeTab = "notebook")}
            class="px-4 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-2 {activeTab ===
            'notebook'
              ? isLight
                ? 'bg-indigo-100 text-indigo-900 shadow-sm'
                : 'bg-white/10 text-white shadow-sm'
              : subTextClass}"
          >
            <NotePencil size={16} /> Cuaderno
          </button>
        </nav>
      </div>

      <!-- Widgets -->
      <div class="flex items-center gap-4 md:gap-6">
        <!-- Cloud Drive Widget -->
        <a
          href={DRIVE_URL}
          target="_blank"
          class="group flex items-center gap-2 px-3 py-1.5 md:px-4 md:py-2 rounded-xl text-sm font-mono transition-all border {borderClass} {cardClass} {hoverClass} text-indigo-500"
          title="Abrir Nube (Google Drive)"
        >
          <CloudArrowUp size={18} weight="duotone" />
          <span class="hidden md:inline font-bold">Nube</span>
        </a>

        <!-- Theme Toggle Widget (NEW) -->
        <button
          on:click={toggleTheme}
          class="group flex items-center gap-2 px-3 py-1.5 md:px-4 md:py-2 rounded-xl text-sm font-mono transition-all border {borderClass} {cardClass} {hoverClass}"
          title="Cambiar Tema (Auto / Día / Noche)"
        >
          <svelte:component
            this={ThemeIcon}
            size={18}
            class={manualOverride
              ? isLight
                ? "text-amber-500"
                : "text-indigo-400"
              : subTextClass}
          />
          <span
            class="hidden md:inline {subTextClass} text-xs uppercase font-bold"
          >
            {manualOverride === "light"
              ? "Día"
              : manualOverride === "dark"
                ? "Noche"
                : "Auto"}
          </span>
        </button>

        <!-- Ambient Music Widget -->
        <div class="flex items-center gap-2">
          <button
            on:click={toggleMusic}
            class="group flex items-center gap-2 px-3 py-1.5 md:px-4 md:py-2 rounded-xl text-sm font-mono transition-all border {borderClass} {cardClass} {hoverClass} {isPlaying
              ? 'ring-2 ring-emerald-500/50'
              : ''}"
            title={isPlaying ? "Pausar Ambiente" : "Reproducir Ambiente"}
          >
            <MusicNotes
              size={18}
              weight={isPlaying ? "fill" : "regular"}
              class={isPlaying
                ? "text-emerald-500 animate-pulse"
                : subTextClass}
            />
          </button>
          <!-- Bind volumen y paused. Volume REMOVED to avoid errors, controlled via JS -->
          <audio
            bind:this={audioElement}
            bind:paused={isPaused}
            loop
            src={ambientMusic}
          ></audio>
        </div>

        <!-- Timer Widget -->
        <button
          on:click={toggleTimer}
          class="group flex items-center gap-2 md:gap-3 px-3 py-1.5 md:px-4 md:py-2 rounded-xl text-sm font-mono transition-all border {borderClass} {cardClass} {hoverClass} {timerActive
            ? 'ring-2 ring-indigo-500/50'
            : ''}"
        >
          <Timer
            size={18}
            weight={timerActive ? "fill" : "regular"}
            class={timerActive ? "text-indigo-500 animate-pulse" : subTextClass}
          />
          <span
            class="text-lg md:text-xl font-bold {timerActive
              ? isLight
                ? 'text-indigo-900'
                : 'text-indigo-100'
              : isLight
                ? 'text-slate-600'
                : 'text-slate-300'}"
          >
            {formatTimer(timerSeconds)}
          </span>
        </button>

        <!-- Clock Widget -->
        <div class="text-right hidden md:block">
          <div
            class="text-2xl font-bold leading-none {isLight
              ? 'text-indigo-950'
              : 'text-white'}"
          >
            {currentTime.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
          <div
            class="text-xs font-medium uppercase tracking-wider mt-1 {subTextClass}"
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
      <!-- COLUMN 1: LIBRARY -->
      <div
        class="flex-col gap-6 overflow-hidden h-full {activeTab === 'library'
          ? 'flex'
          : 'hidden md:flex'}"
      >
        {#if loading}
          <div class="flex-1 flex items-center justify-center">
            <div class="text-xl animate-pulse font-light {subTextClass}">
              Cargando la cuenca de datos...
            </div>
          </div>
        {:else}
          <!-- Stats Compactos (Restaurado para V5) -->
          <div class="flex-shrink-0">
            <Stats {data} {isLight} />
          </div>
          <!-- Tabla con Scroll Independiente -->
          <div
            class="flex-1 overflow-hidden rounded-xl border {borderClass} {isLight
              ? 'bg-white shadow-sm'
              : 'bg-black/10 backdrop-blur-sm'}"
          >
            <Table {data} {isLight} />
          </div>
        {/if}
      </div>

      <!-- COLUMN 2: RIGHT PANEL (Notebook & AI) -->
      <div
        class="flex-col gap-4 overflow-hidden h-full {activeTab === 'notebook'
          ? 'flex'
          : 'hidden md:flex'}"
      >
        <!-- Pestañas Superiores -->
        <div
          class="flex p-1 rounded-xl border {borderClass} {cardClass} shrink-0 self-start"
        >
          <button
            on:click={() => (rightTab = "notebook")}
            class="px-4 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-2 {rightTab ===
            'notebook'
              ? isLight
                ? 'bg-indigo-100 text-indigo-900 shadow-sm'
                : 'bg-white/10 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-500 hover:bg-black/5'}"
          >
            <NotePencil
              size={16}
              weight={rightTab === "notebook" ? "fill" : "regular"}
            /> Cuaderno
          </button>
          <button
            on:click={() => (rightTab = "assistant")}
            class="px-4 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-2 {rightTab ===
            'assistant'
              ? isLight
                ? 'bg-indigo-100 text-indigo-900 shadow-sm'
                : 'bg-white/10 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-500 hover:bg-black/5'}"
          >
            <ChatCircleText
              size={18}
              weight={rightTab === "assistant" ? "fill" : "regular"}
            /> Asistente
          </button>
          <button
            on:click={() => (rightTab = "bible")}
            class="px-4 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-2 {rightTab ===
            'bible'
              ? isLight
                ? 'bg-indigo-100 text-indigo-900 shadow-sm'
                : 'bg-white/10 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-500 hover:bg-black/5'}"
          >
            <BookOpen
              size={18}
              weight={rightTab === "bible" ? "fill" : "regular"}
            /> Biblia
          </button>
        </div>

        <div
          class="flex-1 h-full relative overflow-hidden rounded-xl border {borderClass} {isLight
            ? 'bg-white shadow-sm'
            : 'bg-white/5'}"
        >
          {#if rightTab === "notebook"}
            <div class="h-full w-full absolute inset-0">
              <Notebook {isLight} />
            </div>
          {:else if rightTab === "assistant"}
            <div class="h-full w-full absolute inset-0">
              <AiAssistant {isLight} {userName} />
            </div>
          {:else if rightTab === "bible"}
            <div class="h-full w-full absolute inset-0">
              <BibleWidget {isLight} />
            </div>
          {/if}
        </div>
      </div>
    </main>

    <!-- FOOTER -->
    <footer
      class="mt-8 text-center text-[10px] font-medium tracking-wide flex flex-col items-center justify-center gap-1 opacity-60 hover:opacity-100 transition-opacity pb-6 {subTextClass}"
    >
      <span>&copy; {new Date().getFullYear()} Héctor Aguila</span>
      <button
        on:click={() => (showDiagnostics = true)}
        class="flex items-center gap-1 mt-1 hover:text-indigo-400 transition-colors cursor-pointer"
        title="Abrir Diagnóstico del Sistema"
      >
        >Un Soñador con Poca Ram
        <Laptop size={15} />
      </button>
    </footer>
  </div>
</div>

<!-- 
<BackendDiagnostics
  isOpen={showDiagnostics}
  onClose={() => (showDiagnostics = false)}
/> 
-->
{#if showWelcomeModal}
  <WelcomeModal {isLight} on:save={handleWelcomeSave} />
{/if}
<Toaster />

<style>
  /* Scrollbar estilizado y dinámico */
  :global(:root) {
    --scrollbar-thumb: rgba(255, 255, 255, 0.1);
    --scrollbar-thumb-hover: rgba(255, 255, 255, 0.2);
  }

  /* Sobrescribir variables si es tema claro (detectado por clase en html o body, pero aquí lo haremos manual en style inline si es necesario, 
     o mejor, usando una clase global 'light-theme' si existiera. 
     Como no tenemos 'light-theme' global, usaremos selectores más específicos o simplemente colores oscuros con opacidad baja que funcionen en ambos o invertidos).
  */

  ::-webkit-scrollbar {
    width: 6px; /* Más sutil */
  }
  ::-webkit-scrollbar-track {
    background: transparent;
  }

  /* Thumb dinámico basado en las clases de color del padre */
  /* En Light Mode el texto es oscuro, así que usamos un gris medio */
  :global(.text-slate-800) ::-webkit-scrollbar-thumb {
    background-color: rgba(0, 0, 0, 0.2);
  }
  :global(.text-slate-800) ::-webkit-scrollbar-thumb:hover {
    background-color: rgba(0, 0, 0, 0.3);
  }

  /* En Dark Mode (default) */
  ::-webkit-scrollbar-thumb {
    background-color: rgba(255, 255, 255, 0.15);
    border-radius: 10px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background-color: rgba(255, 255, 255, 0.25);
  }

  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
</style>
