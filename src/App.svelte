<script>
  import { onMount, onDestroy } from "svelte";
  import { Toaster } from "svelte-french-toast";
  import {
    tema,
    usuario,
    pestañaActiva,
    biblioteca,
    librosFisicos,
    archivoAbierto,
    cargando,
    cargarTodo,
  } from "./lib/stores";

  // Componentes
  import Estadisticas from "./components/Estadisticas.svelte";
  import Tabla from "./components/Tabla.svelte";
  import Cuaderno from "./components/Cuaderno.svelte";
  import AsistenteIA from "./components/AsistenteIA.svelte";
  import WidgetBiblia from "./components/WidgetBiblia.svelte";
  import LogoArca from "./components/ArcaLogo.svelte";
  import ModalBienvenida from "./components/ModalBienvenida.svelte";
  import Diccionario from "./components/Diccionario.svelte";
  import Lector from "./components/Lector.svelte";
  import BibliotecaFisica from "./components/BibliotecaFisica.svelte";

  // Estado Local
  let mostrarBienvenida = false;
  let subPestañaIzquierda = "digital"; // 'digital', 'fisica'
  let subPestañaDerecha = "notas"; // 'notas', 'asistente', 'biblia', 'diccionario'
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
  $: horaActual = tiempoActual.getHours();
  $: esDeDia = horaActual >= 7 && horaActual < 19;
  $: esClaro = $tema === "claro" || ($tema === "auto" && esDeDia);

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
    class="max-w-[1920px] mx-auto p-4 md:p-6 lg:p-8 flex flex-col min-h-screen md:h-screen md:overflow-hidden relative"
  >
    <!-- CABECERA -->
    <header
      class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 md:mb-10 gap-6 flex-shrink-0"
    >
      <div class="flex items-center gap-6 w-full justify-between md:w-auto">
        <!-- Logo -->
        <div class="flex items-center gap-4">
          <LogoArca
            size="w-10 h-10 md:w-12 md:h-12"
            color={esClaro ? "text-indigo-900" : "text-white"}
          />
          <div class="flex flex-col border-l {claseBorde} pl-4 md:pl-6 py-1">
            <h1
              class="text-xl md:text-2xl font-black tracking-tighter leading-none {esClaro
                ? 'text-indigo-950'
                : 'text-white'}"
            >
              El Arca
            </h1>
            <span
              class="text-[8px] md:text-[9px] uppercase tracking-[0.3em] opacity-40 font-bold mt-1"
            >
              Estudiante: {$usuario || "Invitado"}
            </span>
          </div>
        </div>

        <!-- Widgets Móviles (Solo Tema y Música por espacio) -->
        <!-- Widgets Móviles (Solo Tema y Música por espacio) -->
        <div class="flex md:hidden gap-2 items-center">
          <button
            on:click={alternarTema}
            class="p-2 rounded-lg border {claseBorde} {claseTarjeta} text-xs"
          >
            {$tema === "claro" ? "☀️" : "🌙"}
          </button>

          <button
            on:click={alternarMusica}
            class="p-2 rounded-lg border {claseBorde} {claseTarjeta} text-xs {!musicaPausada
              ? 'text-emerald-500 border-emerald-500/50'
              : ''}"
          >
            🎵
          </button>
          <button
            on:click={alternarTemporizador}
            class="p-2 rounded-lg border {claseBorde} {claseTarjeta} text-xs font-mono {temporizadorActivo
              ? 'text-indigo-500 border-indigo-500'
              : ''}"
          >
            {temporizadorActivo ? formatearTiempo(segundosTemporizador) : "⏱️"}
          </button>
        </div>
      </div>

      <!-- Widgets Desktop -->
      <div class="hidden md:flex items-center gap-6">
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

    <!-- ÁREA PRINCIPAL (Desktop: Grid Fixed / Mobile: Flex Scroll) -->
    <main
      class="flex-1 grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-6 relative md:overflow-hidden"
    >
      <!-- SECCIÓN 1: BIBLIOTECA (Siempre visible arriba en móvil) -->
      <div
        class="flex flex-col gap-4 md:gap-6 md:h-full md:overflow-hidden min-h-[500px]"
      >
        {#if $cargando}
          <div class="flex-1 flex items-center justify-center p-10">
            <span class="text-sm uppercase tracking-[0.2em] animate-pulse"
              >Sincronizando Archivos...</span
            >
          </div>
        {:else}
          <div class="flex-shrink-0 flex flex-col gap-4">
            <div class="flex justify-between items-center">
              <nav
                class="flex p-1 rounded-xl border {claseBorde} {claseTarjeta} self-start"
              >
                <button
                  on:click={() => (subPestañaIzquierda = "digital")}
                  class="px-4 md:px-5 py-2 rounded-lg text-[9px] md:text-[10px] uppercase font-bold tracking-widest transition-all {subPestañaIzquierda ===
                  'digital'
                    ? esClaro
                      ? 'bg-indigo-100 text-indigo-900'
                      : 'bg-white/10 text-white'
                    : 'opacity-40 hover:opacity-100'}"
                >
                  Digital
                </button>
                <button
                  on:click={() => (subPestañaIzquierda = "fisica")}
                  class="px-4 md:px-5 py-2 rounded-lg text-[9px] md:text-[10px] uppercase font-bold tracking-widest transition-all {subPestañaIzquierda ===
                  'fisica'
                    ? esClaro
                      ? 'bg-indigo-100 text-indigo-900'
                      : 'bg-white/10 text-white'
                    : 'opacity-40 hover:opacity-100'}"
                >
                  Física
                </button>
              </nav>
            </div>

            <Estadisticas
              datos={subPestañaIzquierda === "digital"
                ? $biblioteca
                : $librosFisicos}
              {esClaro}
            />
          </div>

          <!-- Contenedor Tabla/Visor con altura fija en móvil para scroll interno -->
          <div
            class="flex-1 md:overflow-hidden h-[600px] md:h-auto rounded-xl border {claseBorde} {esClaro
              ? 'bg-white shadow-sm'
              : 'bg-black/10 backdrop-blur-sm'} relative"
          >
            {#if subPestañaIzquierda === "digital"}
              <Tabla datos={$biblioteca} {esClaro} />
            {:else}
              <BibliotecaFisica {esClaro} />
            {/if}
          </div>
        {/if}
      </div>

      <!-- SECCIÓN 2: HERRAMIENTAS (Debajo en móvil) -->
      <div
        class="flex flex-col gap-4 md:h-full md:overflow-hidden min-h-[600px] pb-10 md:pb-0"
      >
        <!-- Selector de Sub-pestaña -->
        <nav
          class="flex flex-wrap p-1 rounded-xl border {claseBorde} {claseTarjeta} self-start"
        >
          <button
            on:click={() => (subPestañaDerecha = "notas")}
            class="px-4 py-2 rounded-lg text-[9px] md:text-[10px] uppercase font-bold tracking-widest transition-all {subPestañaDerecha ===
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
            class="px-4 py-2 rounded-lg text-[9px] md:text-[10px] uppercase font-bold tracking-widest transition-all {subPestañaDerecha ===
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
            class="px-4 py-2 rounded-lg text-[9px] md:text-[10px] uppercase font-bold tracking-widest transition-all {subPestañaDerecha ===
            'biblia'
              ? esClaro
                ? 'bg-indigo-100 text-indigo-900'
                : 'bg-white/10 text-white'
              : 'opacity-40 hover:opacity-100'}"
          >
            Biblia
          </button>
          <button
            on:click={() => (subPestañaDerecha = "diccionario")}
            class="px-4 py-2 rounded-lg text-[9px] md:text-[10px] uppercase font-bold tracking-widest transition-all {subPestañaDerecha ===
            'diccionario'
              ? esClaro
                ? 'bg-indigo-100 text-indigo-900'
                : 'bg-white/10 text-white'
              : 'opacity-40 hover:opacity-100'}"
          >
            Diccionario
          </button>
        </nav>

        <div
          class="flex-1 h-[600px] md:h-full relative overflow-hidden rounded-xl border {claseBorde} {esClaro
            ? 'bg-white shadow-sm'
            : 'bg-white/5'}"
        >
          {#if subPestañaDerecha === "notas"}
            <div class="h-full w-full absolute inset-0 text-xs">
              <Cuaderno {esClaro} />
            </div>
          {:else if subPestañaDerecha === "asistente"}
            <div class="h-full w-full absolute inset-0">
              <AsistenteIA {esClaro} nombreUsuario={$usuario} />
            </div>
          {:else if subPestañaDerecha === "biblia"}
            <div class="h-full w-full absolute inset-0">
              <WidgetBiblia {esClaro} />
            </div>
          {:else if subPestañaDerecha === "diccionario"}
            <div class="h-full w-full absolute inset-0">
              <Diccionario {esClaro} />
            </div>
          {/if}
        </div>
      </div>
    </main>

    <!-- PIE DE PÁGINA (Desktop Only) -->
    <footer
      class="hidden md:flex mt-8 flex-col items-center gap-1 opacity-40 hover:opacity-100 transition-opacity pb-10"
    >
      <div class="text-[10px] font-medium tracking-tight">
        &copy; {new Date().getFullYear()} Héctor Aguila
      </div>
      <div
        class="text-[10px] font-bold tracking-widest mt-1 uppercase cursor-default"
      >
        >Un Soñador con Poca Ram 👨🏻‍💻
      </div>
    </footer>
  </div>
</div>

{#if mostrarBienvenida}
  <ModalBienvenida {esClaro} on:save={manejarGuardadoUsuario} />
{/if}
{#if $archivoAbierto}
  <Lector {esClaro} />
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
