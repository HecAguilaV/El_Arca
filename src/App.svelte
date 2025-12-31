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

  // Dual Workbench State
  let herramientaIzquierda = "biblioteca";
  let herramientaDerecha = "notas";
  let focoLayout = "ambos"; // 'ambos', 'izquierda', 'derecha'

  // Opciones de Herramientas
  const OPCIONES_HERRAMIENTAS = [
    { id: "biblioteca", label: "Biblioteca", icono: "📚" },
    { id: "lector", label: "Lector / Visualizador", icono: "📄" },
    { id: "biblioteca_fisica", label: "Biblioteca Física", icono: "📖" },
    { id: "notas", label: "Cuaderno de Notas", icono: "✏️" },
    { id: "asistente", label: "Asistente Teológico", icono: "🤖" },
    { id: "biblia", label: "Santa Biblia", icono: "✝️" },
    { id: "diccionario", label: "Diccionario", icono: "📕" },
  ];

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

  // --- NUEVAS FUNCIONES DE UTILIDAD (Migradas de Estadisticas) ---

  async function verificarSistema() {
    const { api } = await import("./lib/api");
    import("svelte-french-toast").then((t) =>
      t.default.loading("Verificando sistema...", { duration: 1500 }),
    );
    try {
      const API_BASE_URL =
        import.meta.env.VITE_API_BASE_URL || "https://el-arca.onrender.com";
      const res = await fetch(`${API_BASE_URL}/sistema/diagnostico`);
      const data = await res.json();
      const estado = `DB: ${data.base_datos} | Drive: ${data.google_drive.mensaje || "OK"}`;

      import("svelte-french-toast").then((t) => {
        if (
          data.google_drive.estado === "ok" ||
          data.google_drive.mensaje === "Credenciales configuradas"
        )
          t.default.success("Sistema Operativo", { duration: 4000 });
        else t.default.error(estado, { duration: 6000 });
      });
    } catch (e) {
      import("svelte-french-toast").then((t) =>
        t.default.error("Error conectando al servidor"),
      );
    }
  }

  async function sincronizarDrive() {
    const { api } = await import("./lib/api");
    try {
      import("svelte-french-toast").then((t) =>
        t.default.loading("Conectando con Drive...", { duration: 2000 }),
      );
      await api.libros.sincronizarDrive();
      import("svelte-french-toast").then((t) =>
        t.default.success("Sincronización iniciada."),
      );
      setTimeout(cargarTodo, 3000);
    } catch (e) {
      import("svelte-french-toast").then((t) =>
        t.default.error("Error: Acceso denegado"),
      );
    }
  }

  onMount(async () => {
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

  // Audio Context para el "Gong" de meditación
  let audioCtx;
  function reproducirSonidoFin() {
    if (!audioCtx)
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();

    osc.connect(gain);
    gain.connect(audioCtx.destination);

    osc.type = "sine";
    osc.frequency.setValueAtTime(440, audioCtx.currentTime); // La
    osc.frequency.exponentialRampToValueAtTime(110, audioCtx.currentTime + 1.5);

    gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 1.5);

    osc.start();
    osc.stop(audioCtx.currentTime + 1.5);
  }

  // Temporizador Mejorado
  function alternarTemporizador() {
    if (temporizadorActivo) {
      detenerTemporizador();
    } else {
      temporizadorActivo = true;
      intervaloTemporizador = setInterval(() => {
        if (segundosTemporizador > 0) {
          segundosTemporizador--;

          // Lógica de Crossfade (si faltan 10s y hay música sonando)
          if (segundosTemporizador <= 10 && !musicaPausada && elementoAudio) {
            // Reducir volumen linealmente
            const nuevoVol = Math.max(0, elementoAudio.volume - 0.05);
            elementoAudio.volume = nuevoVol;
          }
        } else {
          reproducirSonidoFin();
          detenerTemporizador();
          // Restaurar volumen si se quiere volver a usar
          if (elementoAudio) elementoAudio.volume = 0.5;
        }
      }, 1000);
    }
  }

  function detenerTemporizador() {
    temporizadorActivo = false;
    clearInterval(intervaloTemporizador);
    if (segundosTemporizador === 0) segundosTemporizador = 45 * 60;
  }

  function ajustarTemporizador(minutos) {
    segundosTemporizador = Math.max(0, segundosTemporizador + minutos * 60);
  }

  function formatearTiempo(seg) {
    const m = Math.floor(seg / 60)
      .toString()
      .padStart(2, "0");
    const s = (seg % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  }

  // Detectar cambios en archivoAbierto para auto-abrir lector SOLO al inicio
  let ultimoArchivo = null;
  $: if ($archivoAbierto !== ultimoArchivo) {
    if ($archivoAbierto && !ultimoArchivo) {
      // Si se abre un archivo nuevo y no hay lector visible, abrirlo
      if (
        herramientaIzquierda !== "lector" &&
        herramientaDerecha !== "lector"
      ) {
        herramientaIzquierda = "lector";
      }
    }
    ultimoArchivo = $archivoAbierto;
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
    class="max-w-[1920px] mx-auto p-4 md:p-6 lg:p-8 flex flex-col min-h-screen relative"
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

        <!-- Widgets Móviles -->
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
      <div class="hidden md:flex items-center gap-4">
        <!-- Botones de Sistema (Movidos de Estadisticas) -->
        <div class="flex gap-2 mr-4 border-r {claseBorde} pr-4">
          <button
            on:click={verificarSistema}
            class="p-2 rounded-lg border {claseBorde} {claseTarjeta} text-[10px] hover:scale-105 transition-transform"
            title="Diagnóstico de Sistema"
          >
            🩺
          </button>
          <button
            on:click={sincronizarDrive}
            class="p-2 rounded-lg border {claseBorde} {claseTarjeta} text-[10px] hover:scale-105 transition-transform"
            title="Sincronizar Drive"
          >
            ☁️
          </button>
        </div>

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

        <!-- Temporizador Flexible -->
        <div class="flex items-center gap-2 group relative">
          <!-- Controles flotantes (aparecen en hover) -->
          <div
            class="absolute -top-8 left-1/2 -translate-x-1/2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <button
              on:click={() => ajustarTemporizador(5)}
              class="px-2 py-1 text-[9px] bg-indigo-500 text-white rounded shadow hover:bg-indigo-400"
              >+5m</button
            >
            <button
              on:click={() => ajustarTemporizador(-5)}
              class="px-2 py-1 text-[9px] bg-red-500 text-white rounded shadow hover:bg-red-400"
              >-5m</button
            >
          </div>

          <button
            on:click={alternarTemporizador}
            class="flex items-center gap-3 px-4 py-2 rounded-xl border {claseBorde} {claseTarjeta} {temporizadorActivo
              ? 'ring-1 ring-indigo-500/50'
              : ''} hover:ring-1 hover:ring-indigo-500/30 transition-all cursor-pointer"
          >
            <span class="text-lg font-mono font-bold"
              >{formatearTiempo(segundosTemporizador)}</span
            >
          </button>
        </div>

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

    <!-- MESA DE TRABAJO DUAL (Dual Workbench) -->
    <main
      class="flex-1 flex flex-col lg:flex-row gap-4 lg:gap-8 relative overflow-hidden h-[calc(100vh-140px)]"
    >
      <!-- ZONA IZQUIERDA (Principal o Flexible) -->
      <section
        class="flex flex-col gap-4 transition-all duration-500 ease-in-out relative {focoLayout ===
        'derecha'
          ? 'lg:w-[0%] opacity-0 overflow-hidden'
          : focoLayout === 'izquierda'
            ? 'flex-1'
            : 'lg:w-1/2'} h-full"
      >
        <!-- Selector de Herramienta Izquierda -->
        <nav
          class="flex overflow-x-auto gap-2 p-1 border-b {claseBorde} no-scrollbar"
        >
          {#each OPCIONES_HERRAMIENTAS as opcion}
            <button
              on:click={() => (herramientaIzquierda = opcion.id)}
              class="px-3 py-1.5 rounded-lg text-[9px] uppercase font-bold tracking-widest whitespace-nowrap transition-all {herramientaIzquierda ===
              opcion.id
                ? esClaro
                  ? 'bg-indigo-100 text-indigo-900'
                  : 'bg-white/20 text-white'
                : 'opacity-40 hover:opacity-100'}"
            >
              {opcion.icono}
              {opcion.label}
            </button>
          {/each}
        </nav>

        <!-- Contenido Izquierda -->
        <div
          class="flex-1 relative rounded-xl border {claseBorde} {claseTarjeta} overflow-hidden"
        >
          {#if herramientaIzquierda === "biblioteca"}
            <div class="h-full overflow-y-auto p-4">
              <!-- Reemplazamos Estadisticas con algo simple si se requiere, o directo la Tabla -->
              <Tabla datos={$biblioteca} {esClaro} />
            </div>
          {:else if herramientaIzquierda === "lector"}
            {#if $archivoAbierto}
              <Lector {esClaro} />
            {:else}
              <div
                class="h-full flex items-center justify-center opacity-40 text-xs tracking-widest uppercase"
              >
                Selecciona un libro de la biblioteca
              </div>
            {/if}
          {:else if herramientaIzquierda === "biblioteca_fisica"}
            <BibliotecaFisica {esClaro} />
          {:else if herramientaIzquierda === "notas"}
            <div class="h-full w-full absolute inset-0 text-xs">
              <Cuaderno {esClaro} />
            </div>
          {:else if herramientaIzquierda === "asistente"}
            <AsistenteIA {esClaro} nombreUsuario={$usuario} />
          {:else if herramientaIzquierda === "biblia"}
            <WidgetBiblia {esClaro} />
          {:else if herramientaIzquierda === "diccionario"}
            <Diccionario {esClaro} />
          {/if}
        </div>
      </section>

      <!-- DIVISOR / CONTROLADOR DE FOCO (Sticky para no perderse) -->
      <div
        class="hidden lg:flex flex-col justify-center items-center gap-2 z-10 w-4 flex-shrink-0 sticky top-0 h-screen self-start pointer-events-none"
      >
        <div
          class="pointer-events-auto flex flex-col gap-2 bg-black/20 backdrop-blur-sm p-1 rounded-full"
        >
          {#if focoLayout === "ambos"}
            <button
              on:click={() => (focoLayout = "izquierda")}
              class="p-1 rounded-full hover:bg-indigo-500 hover:text-white transition-colors opacity-50 hover:opacity-100"
              title="Expandir Izquierda">◀</button
            >
            <button
              on:click={() => (focoLayout = "derecha")}
              class="p-1 rounded-full hover:bg-indigo-500 hover:text-white transition-colors opacity-50 hover:opacity-100"
              title="Expandir Derecha">▶</button
            >
          {:else}
            <button
              on:click={() => (focoLayout = "ambos")}
              class="p-1 rounded-full hover:bg-indigo-500 hover:text-white transition-colors opacity-50 hover:opacity-100"
              title="Restaurar Vista Dividida">●</button
            >
          {/if}
        </div>
      </div>

      <!-- ZONA DERECHA (Secundaria o Flexible) -->
      <section
        class="flex flex-col gap-4 transition-all duration-500 ease-in-out relative {focoLayout ===
        'izquierda'
          ? 'lg:w-[0%] opacity-0 overflow-hidden'
          : focoLayout === 'derecha'
            ? 'flex-1'
            : 'lg:w-1/2'} h-full"
      >
        <!-- Selector de Herramienta Derecha -->
        <nav
          class="flex overflow-x-auto gap-2 p-1 border-b {claseBorde} no-scrollbar justify-end"
        >
          {#each OPCIONES_HERRAMIENTAS as opcion}
            <button
              on:click={() => (herramientaDerecha = opcion.id)}
              class="px-3 py-1.5 rounded-lg text-[9px] uppercase font-bold tracking-widest whitespace-nowrap transition-all {herramientaDerecha ===
              opcion.id
                ? esClaro
                  ? 'bg-indigo-100 text-indigo-900'
                  : 'bg-white/20 text-white'
                : 'opacity-40 hover:opacity-100'}"
            >
              {opcion.icono}
              {opcion.label}
            </button>
          {/each}
        </nav>

        <!-- Contenido Derecha -->
        <div
          class="flex-1 relative rounded-xl border {claseBorde} {claseTarjeta} overflow-hidden"
        >
          {#if herramientaDerecha === "biblioteca"}
            <div class="h-full overflow-y-auto p-4">
              <Tabla datos={$biblioteca} {esClaro} />
            </div>
          {:else if herramientaDerecha === "lector"}
            {#if $archivoAbierto}
              <Lector {esClaro} />
            {:else}
              <div
                class="h-full flex items-center justify-center opacity-40 text-xs tracking-widest uppercase"
              >
                Selecciona un libro de la biblioteca
              </div>
            {/if}
          {:else if herramientaDerecha === "biblioteca_fisica"}
            <BibliotecaFisica {esClaro} />
          {:else if herramientaDerecha === "notas"}
            <div class="h-full w-full absolute inset-0 text-xs">
              <Cuaderno {esClaro} />
            </div>
          {:else if herramientaDerecha === "asistente"}
            <AsistenteIA {esClaro} nombreUsuario={$usuario} />
          {:else if herramientaDerecha === "biblia"}
            <WidgetBiblia {esClaro} />
          {:else if herramientaDerecha === "diccionario"}
            <Diccionario {esClaro} />
          {/if}
        </div>
      </section>
    </main>

    <!-- PIE DE PÁGINA -->
    <footer
      class="flex mt-8 flex-col items-center gap-1 opacity-40 hover:opacity-100 transition-opacity pb-10"
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
