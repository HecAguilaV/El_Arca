<script>
  import { onMount, onDestroy } from "svelte";
  import { Toaster } from "svelte-french-toast";
  import {
    tema,
    usuario,
    pestañaActiva,
    biblioteca,
    cargando,
    cargarTodo,
  } from "./lib/stores";

  // Componentes
  import Stats from "./components/Stats.svelte";
  import Table from "./components/Table.svelte";
  import Notebook from "./components/Notebook.svelte";
  import AiAssistant from "./components/AiAssistant.svelte";
  import BibleWidget from "./components/BibleWidget.svelte";
  import ArcaLogo from "./components/ArcaLogo.svelte";
  import WelcomeModal from "./components/WelcomeModal.svelte";

  // Estado Local
  let mostrarBienvenida = false;
  let subPestañaDerecha = "notas"; // 'notas', 'asistente', 'biblia'
  let tiempoActual = new Date();
  let intervaloTiempo;

  // Temporizador
  let temporizadorActivo = false;
  let segundosTemporizador = 45 * 60;
  let intervaloTemporizador;

  // Música Ambiental
  let musicaPausada = true;
  let elementoAudio;
  let volumen = 0;
  let intervaloFade;

  function alternarMusica() {
    if (musicaPausada) {
      musicaPausada = false;
      if (elementoAudio) {
        elementoAudio.volume = 0;
        volumen = 0;
      }
      clearInterval(intervaloFade);
      intervaloFade = setInterval(() => {
        if (elementoAudio && elementoAudio.volume < 0.5) {
          volumen = Math.min(0.5, elementoAudio.volume + 0.02);
          elementoAudio.volume = volumen;
        } else {
          clearInterval(intervaloFade);
        }
      }, 100);
    } else {
      musicaPausada = true;
      clearInterval(intervaloFade);
    }
  }

  function actualizarTema(hora) {
    if ($tema !== "auto") return;
    // Lógica auto-tema si se desea mantener
  }

  function alternarTema() {
    tema.update((t) => {
      const nuevo =
        t === "claro" ? "oscuro" : t === "oscuro" ? "auto" : "claro";
      localStorage.setItem("arca_tema", nuevo);
      return nuevo;
    });
  }

  function manejarGuardadoUsuario(evento) {
    usuario.set(evento.detail);
    localStorage.setItem("arca_usuario", evento.detail);
    mostrarBienvenida = false;
  }

  onMount(async () => {
    // Cargar datos iniciales desde la API
    await cargarTodo();

    if (!$usuario || $usuario === "Estudiante") {
      mostrarBienvenida = true;
    }

    intervaloTiempo = setInterval(() => {
      tiempoActual = new Date();
    }, 1000);
  });

  onDestroy(() => {
    clearInterval(intervaloTiempo);
    clearInterval(intervaloTemporizador);
    clearInterval(intervaloFade);
  });

  // Temporizador
  function alternarTemporizador() {
    if (temporizadorActivo) {
      detenerTemporizador();
    } else {
      temporizadorActivo = true;
      intervaloTemporizador = setInterval(() => {
        if (segundosTemporizador > 0) segundosTemporizador--;
        else detenerTemporizador();
      }, 1000);
    }
  }

  function detenerTemporizador() {
    temporizadorActivo = false;
    clearInterval(intervaloTemporizador);
    if (segundosTemporizador === 0) segundosTemporizador = 45 * 60;
  }

  function formatearTiempo(seg) {
    const m = Math.floor(seg / 60)
      .toString()
      .padStart(2, "0");
    const s = (seg % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  }

  // Clases Reactivas basadas en el tema
  $: esClaro = $tema === "claro";
  $: claseFondo = esClaro ? "bg-[#e7e5e4]" : "bg-[#0f0f13]";
  $: claseTexto = esClaro ? "text-stone-800" : "text-slate-200";
  $: claseSubTexto = esClaro ? "text-stone-500" : "text-slate-400";
  $: claseBorde = esClaro ? "border-stone-300" : "border-white/10";
  $: claseTarjeta = esClaro
    ? "bg-[#fafaf9] border-stone-300 shadow-sm"
    : "bg-white/5 border-white/10";
</script>

<div
  class="min-h-screen transition-colors duration-700 {claseFondo} {claseTexto} font-sans selection:bg-indigo-500/30"
>
  <div
    class="max-w-[1920px] mx-auto p-4 md:p-6 lg:p-8 flex flex-col h-screen overflow-hidden"
  >
    <!-- CABECERA -->
    <header
      class="flex flex-col md:flex-row justify-between items-center mb-6 gap-4 flex-shrink-0"
    >
      <div
        class="flex items-center gap-6 w-full md:w-auto justify-between md:justify-start"
      >
        <div class="flex items-center gap-3">
          <ArcaLogo
            size="w-10 h-10"
            color={esClaro ? "text-indigo-900" : "text-white"}
          />
          <div>
            <h1
              class="text-2xl md:text-3xl font-bold tracking-tight leading-none {esClaro
                ? 'text-indigo-950'
                : 'text-white'}"
            >
              El Arca
            </h1>
            <span
              class="text-[10px] md:text-xs uppercase tracking-widest {claseSubTexto}"
            >
              Biblioteca Digital {$usuario ? `— ${$usuario}` : ""}
            </span>
          </div>
        </div>

        <!-- Navegación Móvil -->
        <nav
          class="flex md:hidden p-1 rounded-xl border {claseBorde} {esClaro
            ? 'bg-white/50'
            : 'bg-black/20'}"
        >
          <button
            on:click={() => pestañaActiva.set("biblioteca")}
            class="px-4 py-1.5 rounded-lg text-xs font-medium transition-all {$pestañaActiva ===
            'biblioteca'
              ? esClaro
                ? 'bg-indigo-100 text-indigo-900'
                : 'bg-white/10 text-white'
              : claseSubTexto}"
          >
            Biblioteca
          </button>
          <button
            on:click={() => pestañaActiva.set("notas")}
            class="px-4 py-1.5 rounded-lg text-xs font-medium transition-all {$pestañaActiva ===
            'notas'
              ? esClaro
                ? 'bg-indigo-100 text-indigo-900'
                : 'bg-white/10 text-white'
              : claseSubTexto}"
          >
            Notas
          </button>
        </nav>
      </div>

      <!-- Widgets Superiores -->
      <div class="flex items-center gap-4 md:gap-6">
        <!-- Tema -->
        <button
          on:click={alternarTema}
          class="px-4 py-2 rounded-lg text-[9px] uppercase font-bold tracking-[0.2em] border {claseBorde} {claseTarjeta} hover:border-indigo-500 transition-all"
        >
          <span class="opacity-40 mr-2">Visualización:</span>
          {$tema}
        </button>

        <!-- Música -->
        <button
          on:click={alternarMusica}
          class="px-4 py-2 rounded-lg text-[9px] uppercase font-bold tracking-[0.2em] border {claseBorde} {claseTarjeta} {!musicaPausada
            ? 'text-emerald-500 border-emerald-500/50'
            : 'hover:border-indigo-500'} transition-all"
        >
          <span class="opacity-40 mr-2">Ambiente:</span>
          {musicaPausada ? "Silencio" : "Activo"}
        </button>
        <audio
          bind:this={elementoAudio}
          bind:paused={musicaPausada}
          loop
          src="/ambient.mp3"
        ></audio>

        <!-- Temporizador -->
        <button
          on:click={alternarTemporizador}
          class="flex items-center gap-3 px-4 py-2 rounded-xl border {claseBorde} {claseTarjeta} {temporizadorActivo
            ? 'ring-1 ring-indigo-500/50'
            : ''}"
        >
          <span class="text-lg font-mono font-bold"
            >{formatearTiempo(segundosTemporizador)}</span
          >
        </button>

        <!-- Reloj -->
        <div class="text-right hidden md:block border-l {claseBorde} pl-6">
          <div class="text-xl font-bold leading-none">
            {tiempoActual.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
          <div
            class="text-[10px] uppercase tracking-widest mt-1 {claseSubTexto}"
          >
            {tiempoActual.toLocaleDateString("es-ES", {
              weekday: "long",
              day: "numeric",
              month: "short",
            })}
          </div>
        </div>
      </div>
    </header>

    <!-- ÁREA PRINCIPAL -->
    <main class="flex-1 overflow-hidden grid md:grid-cols-2 gap-6 relative">
      <!-- Columna Biblioteca -->
      <div
        class="flex-col gap-6 overflow-hidden h-full {$pestañaActiva ===
        'biblioteca'
          ? 'flex'
          : 'hidden md:flex'}"
      >
        {#if $cargando}
          <div class="flex-1 flex items-center justify-center">
            <span class="text-sm uppercase tracking-[0.2em] animate-pulse"
              >Sincronizando Archivos...</span
            >
          </div>
        {:else}
          <div class="flex-shrink-0">
            <Stats data={$biblioteca} isLight={esClaro} />
          </div>
          <div
            class="flex-1 overflow-hidden rounded-xl border {claseBorde} {esClaro
              ? 'bg-white shadow-sm'
              : 'bg-black/10 backdrop-blur-sm'}"
          >
            <Table data={$biblioteca} isLight={esClaro} />
          </div>
        {/if}
      </div>

      <!-- Columna Derecha: Notas, Asistente, Biblia -->
      <div
        class="flex-col gap-4 overflow-hidden h-full {$pestañaActiva === 'notas'
          ? 'flex'
          : 'hidden md:flex'}"
      >
        <!-- Selector de Sub-pestaña -->
        <nav
          class="flex p-1 rounded-xl border {claseBorde} {claseTarjeta} self-start"
        >
          <button
            on:click={() => (subPestañaDerecha = "notas")}
            class="px-5 py-2 rounded-lg text-[10px] uppercase font-bold tracking-widest transition-all {subPestañaDerecha ===
            'notas'
              ? esClaro
                ? 'bg-indigo-100 text-indigo-900'
                : 'bg-white/10 text-white'
              : 'opacity-40 hover:opacity-100'}"
          >
            Notas
          </button>
          <button
            on:click={() => (subPestañaDerecha = "asistente")}
            class="px-5 py-2 rounded-lg text-[10px] uppercase font-bold tracking-widest transition-all {subPestañaDerecha ===
            'asistente'
              ? esClaro
                ? 'bg-indigo-100 text-indigo-900'
                : 'bg-white/10 text-white'
              : 'opacity-40 hover:opacity-100'}"
          >
            Asistente
          </button>
          <button
            on:click={() => (subPestañaDerecha = "biblia")}
            class="px-5 py-2 rounded-lg text-[10px] uppercase font-bold tracking-widest transition-all {subPestañaDerecha ===
            'biblia'
              ? esClaro
                ? 'bg-indigo-100 text-indigo-900'
                : 'bg-white/10 text-white'
              : 'opacity-40 hover:opacity-100'}"
          >
            Biblia
          </button>
        </nav>

        <div
          class="flex-1 h-full relative overflow-hidden rounded-xl border {claseBorde} {esClaro
            ? 'bg-white shadow-sm'
            : 'bg-white/5'}"
        >
          {#if subPestañaDerecha === "notas"}
            <div class="h-full w-full absolute inset-0 text-xs">
              <Notebook isLight={esClaro} />
            </div>
          {:else if subPestañaDerecha === "asistente"}
            <div class="h-full w-full absolute inset-0">
              <AiAssistant isLight={esClaro} userName={$usuario} />
            </div>
          {:else if subPestañaDerecha === "biblia"}
            <div class="h-full w-full absolute inset-0">
              <BibleWidget isLight={esClaro} />
            </div>
          {/if}
        </div>
      </div>
    </main>

    <!-- PIE DE PÁGINA -->
    <footer
      class="mt-8 flex flex-col items-center gap-1 opacity-40 hover:opacity-100 transition-opacity pb-10"
    >
      <div class="text-[10px] font-medium tracking-tight">
        &copy; {new Date().getFullYear()} Héctor Aguila
      </div>
      <div
        class="text-[10px] font-bold tracking-widest mt-1 uppercase cursor-default"
      >
        &gt; Un Soñador con Poca Ram 👨🏻‍💻
      </div>
    </footer>
  </div>
</div>

{#if mostrarBienvenida}
  <WelcomeModal isLight={esClaro} on:save={manejarGuardadoUsuario} />
{/if}
<Toaster />

<style>
  :global(body) {
    margin: 0;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  ::-webkit-scrollbar {
    width: 4px;
  }
  ::-webkit-scrollbar-track {
    background: transparent;
  }
  ::-webkit-scrollbar-thumb {
    background-color: rgba(128, 128, 128, 0.2);
    border-radius: 10px;
  }
</style>
