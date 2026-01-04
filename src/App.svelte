<script>
  import { onMount, onDestroy } from "svelte";
  import { fade } from "svelte/transition"; // Importar transición
  import { Toaster } from "svelte-french-toast";
  import { Info } from "phosphor-svelte"; // Icono Info
  // Importar Firebase
  import { auth, loginWithGoogle, logout } from "./lib/firebase";
  import { onAuthStateChanged } from "firebase/auth";

  import {
    tema,
    usuario,
    pestañaActiva,
    biblioteca,
    librosFisicos,
    archivoAbierto, // Corregido: nombre real del store
    notas, // Agregado
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
  import ModalAcercaDe from "./components/ModalAcercaDe.svelte";

  // Estado Local
  let mostrarBienvenida = false;
  let mostrarAcercaDe = false; // Nuevo estado Modal About
  let cargandoAuth = true; // Estado para spinner inicial
  let usuarioFirebase = null; // Objeto completo de Firebase

  // Dual Workbench State
  let herramientaIzquierda = "biblioteca";
  let herramientaDerecha = "notas";

  // Estado de Colapso Independiente
  let izquierdaColapsada = false;
  let derechaColapsada = false;

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
      detenerMusica(); // Reutilizamos lógica
    }
  }

  function detenerMusica() {
    musicaPausada = true;
    clearInterval(intervaloFade);
    if (elementoAudio) {
      // Fade out rápido
      let fadeOut = setInterval(() => {
        if (elementoAudio.volume > 0.05) {
          elementoAudio.volume -= 0.05;
        } else {
          elementoAudio.volume = 0;
          clearInterval(fadeOut);
        }
      }, 50);
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

  // --- AUTENTICACIÓN ---
  async function manejarLogin() {
    try {
      await loginWithGoogle();
      import("svelte-french-toast").then((t) =>
        t.default.success("Sesión iniciada"),
      );
    } catch (e) {
      import("svelte-french-toast").then((t) =>
        t.default.error("Error al iniciar sesión"),
      );
    }
  }

  async function manejarLogout() {
    try {
      localStorage.removeItem("arca_usuario"); // Limpiar legacy explicitamente
      await logout();
      import("svelte-french-toast").then((t) =>
        t.default.success("Sesión cerrada"),
      );
    } catch (e) {
      console.error(e);
    }
  }

  function manejarGuardadoUsuario(evento) {
    // Legacy: Mantenemos compatibilidad con el modal antiguo por si falla firebase
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
    // Escuchar cambios de Auth
    const unsubscribeAuth = onAuthStateChanged(auth, async (user) => {
      // Async para cargar
      usuarioFirebase = user;
      if (user) {
        usuario.set(user.displayName);
        mostrarBienvenida = false; // Ya no necesitamos el modal si entra con Google

        // RE-CARGAR DATOS AL LOGUEARSE (Para traer sus notas privadas)
        await cargarTodo();
      } else {
        // LOGOUT O NO LOGUEADO - LIMPIEZA DE SESIÓN ESTRICTA

        // 1. Limpieza Audio
        detenerMusica();

        // 2. Limpieza Temporizador (CRÍTICO: Detener el intervalo)
        clearInterval(intervaloTemporizador);
        temporizadorActivo = false;
        segundosTemporizador = 45 * 60; // Reset a 45min

        // 3. Limpieza UI
        archivoAbierto.set(null);
        izquierdaColapsada = false;
        derechaColapsada = false;

        // 4. Reset User y Datos
        usuario.set(null);
        usuarioFirebase = null;
        biblioteca.set([]);
        notas.set([]);

        mostrarBienvenida = true;

        // NO llamar cargarTodo() aqui. El usuario debe loguearse primero.
      }
      cargandoAuth = false; // Finalizar carga inicial
    });

    // Eliminamos la llamada explícita a cargarTodo() aquí abajo para evitar doble carga race-condition
    // await cargarTodo();

    intervaloTiempo = setInterval(() => {
      tiempoActual = new Date();
    }, 1000);

    return () => unsubscribeAuth();
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
            // Asegurar que el volumen baje suavemente hasta 0
            // Si el volumen inicial es 0.5, bajar 0.05 por segundo llega a 0 en 10s.
            const nuevoVol = Math.max(0, elementoAudio.volume - 0.05);
            elementoAudio.volume = nuevoVol;
          }
        } else {
          // Fin del temporizador
          reproducirSonidoFin();

          // Detener música explícitamente
          if (!musicaPausada) {
            musicaPausada = true; // Activa bind:paused
            if (elementoAudio) elementoAudio.volume = 0.5; // Resetear volumen para la próxima
          }

          detenerTemporizador();
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
        izquierdaColapsada = false; // Auto-expandir al abrir un archivo
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

{#if cargandoAuth}
  <div
    class="absolute inset-0 z-50 flex flex-col items-center justify-center bg-[#111827]"
  >
    <div
      class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mb-4"
    ></div>
    <span
      class="text-xs uppercase tracking-widest text-indigo-400 font-bold opacity-80 animate-pulse"
    >
      Iniciando Protocolos...
    </span>
  </div>
{:else if !usuarioFirebase}
  <div
    class="absolute inset-0 z-40 flex items-center justify-center bg-[#111827] px-4 font-sans"
  >
    <div
      class="max-w-md w-full text-center space-y-8 animate-[fadeIn_1s_ease-out]"
    >
      <!-- Logo Grande -->
      <div class="flex justify-center mb-6">
        <div class="relative group">
          <div
            class="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-amber-500 rounded-full blur opacity-25 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"
          ></div>
          <div
            class="relative bg-[#111827] rounded-full p-6 ring-1 ring-white/10"
          >
            <LogoArca size="w-20 h-20" color="text-indigo-400" />
          </div>
        </div>
      </div>

      <!-- Título y Versículo -->
      <div>
        <h1
          class="text-4xl md:text-5xl font-black text-white tracking-tighter mb-2"
        >
          El Arca
        </h1>
        <p
          class="text-xs uppercase tracking-[0.3em] font-bold text-indigo-400 opacity-80 mb-6"
        >
          Espacio de Estudio Bíblico
        </p>

        <figure class="border-l-2 border-amber-500/30 pl-4 py-2 mx-8 text-left">
          <blockquote
            class="text-stone-300 italic text-sm font-serif leading-relaxed"
          >
            "La sabiduría clama en las calles, alza su voz en las plazas..."
          </blockquote>
          <figcaption
            class="text-[0.6rem] uppercase tracking-widest text-amber-500 mt-2 font-bold opacity-70"
          >
            — Proverbios 1:20
          </figcaption>
        </figure>
      </div>

      <!-- Explicación de Seguridad -->
      <div
        class="bg-indigo-900/20 rounded-xl p-6 border border-indigo-500/10 backdrop-blur-sm"
      >
        <h3 class="text-white text-sm font-bold mb-2">
          Bienvenido a tu Espacio Digital
        </h3>
        <p class="text-stone-400 text-xs leading-relaxed mb-6">
          Para mantener tus notas, subrayados y progreso sincronizados y
          seguros, necesitamos que te identifiques. Todo tu avance se guardará
          automáticamente en tu cuenta personal.
        </p>
        <button
          on:click={loginWithGoogle}
          class="w-full group relative flex items-center justify-center gap-3 bg-white hover:bg-stone-100 text-gray-900 px-8 py-3 rounded-lg font-bold transition-all transform hover:scale-[1.02] active:scale-95 shadow-lg shadow-indigo-500/10"
        >
          <svg class="w-5 h-5" viewBox="0 0 24 24">
            <path
              fill="currentColor"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="currentColor"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="currentColor"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.26z"
            />
            <path
              fill="currentColor"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          <span>Acceder con Google</span>
        </button>
      </div>

      <!-- Firma -->
      <div class="pt-4 opacity-40 hover:opacity-100 transition-opacity">
        <p
          class="text-[0.65rem] uppercase tracking-[0.2em] text-stone-500 font-bold"
        >
          Autor: Héctor Aguila
        </p>
        <p class="text-[0.6rem] text-stone-600 font-mono mt-1">
          &gt; Un Soñador con Poca RAM 👨🏻‍💻
        </p>
      </div>
    </div>
  </div>
{:else}
  <!-- APP PRINCIPAL: Solo visible si hay usuario autenticado -->
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

              {#if usuarioFirebase}
                <div class="flex items-center gap-2 mt-1">
                  {#if usuarioFirebase.photoURL}
                    <img
                      src={usuarioFirebase.photoURL}
                      alt="User"
                      class="w-4 h-4 rounded-full border border-white/20"
                    />
                  {/if}
                  <span
                    class="text-[8px] md:text-[9px] uppercase tracking-[0.3em] opacity-60 font-bold"
                  >
                    {usuarioFirebase.displayName}
                  </span>
                </div>
              {/if}
            </div>
          </div>

          <!-- Controles Móviles (Colapso) -->
          <div class="flex md:hidden gap-2">
            <!-- Widgets Móviles -->
            <button
              on:click={() => (mostrarAcercaDe = true)}
              class="p-2 rounded-lg border {claseBorde} {claseTarjeta} text-xs opacity-60 hover:opacity-100"
            >
              <Info size={16} />
            </button>

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
              {temporizadorActivo
                ? formatearTiempo(segundosTemporizador)
                : "⏱️"}
            </button>
          </div>
        </div>

        <!-- BARRA DERECHA (Buscador + Menú) -->
        <div
          class="hidden md:flex flex-col md:flex-row items-stretch md:items-center gap-4 w-full md:w-auto"
        >
          <!-- Widgets Escritorio -->
          <div class="flex items-center gap-3">
            <!-- Tema -->
            <button
              on:click={() => (mostrarAcercaDe = true)}
              class="p-2 -mr-1 rounded-lg border {claseBorde} {claseTarjeta} opacity-40 hover:opacity-100 transition-opacity"
              title="Acerca de El Arca"
            >
              <Info size={16} />
            </button>

            <!-- Tema -->
            <button
              on:click={alternarTema}
              class="p-2 mr-2 rounded-lg border {claseBorde} {claseTarjeta} opacity-60 hover:opacity-100 transition-opacity"
              title="Cambiar Tema"
            >
              {$tema === "claro" ? "☀️" : "🌙"}
            </button>

            <!-- Musica -->
            <button
              on:click={alternarMusica}
              class="mr-4 opacity-50 hover:opacity-100 transition-opacity text-xl"
              title={musicaPausada ? "Activar Música" : "Pausar Música"}
            >
              {#if musicaPausada}🔇{:else}🔊{/if}
            </button>

            <!-- Temporizador Flexible (Movido aquí) -->
            <div
              class="flex items-center gap-2 group relative border-l {claseBorde} pl-6"
            >
              <!-- Controles flotantes -->
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

            <!-- Boton Salir -->
            <button
              on:click={manejarLogout}
              class="ml-6 p-2 rounded-lg text-red-500 hover:bg-red-500/10 transition-colors opacity-60 hover:opacity-100 uppercase text-[10px] font-bold tracking-widest border border-transparent hover:border-red-500/30"
              title="Cerrar Sesión"
            >
              Salir
            </button>

            <audio
              bind:this={elementoAudio}
              bind:paused={musicaPausada}
              loop
              src="/ambient.mp3"
            ></audio>

            <!-- Reloj (Movido aquí, esquina derecha) -->
            <div
              class="hidden md:flex flex-col items-end text-right border-l {claseBorde} pl-6"
            >
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

            <!-- Reloj Extra Eliminado (Estaba duplicado) -->
          </div>
        </div>
      </header>

      <!-- MESA DE TRABAJO DUAL (Dual Workbench) -->
      <main
        class="flex-1 flex flex-col lg:flex-row gap-4 lg:gap-8 relative overflow-hidden h-[calc(100vh-140px)]"
      >
        <!-- ZONA IZQUIERDA -->
        <section
          class="transition-all duration-500 ease-in-out relative flex flex-col
        {izquierdaColapsada
            ? 'flex-none h-12 lg:w-16 lg:h-full'
            : 'flex-1 min-h-0 lg:w-1/2'}"
        >
          <!-- Selector Izquierda -->
          <nav
            class="flex flex-wrap gap-2 p-1 border-b {claseBorde} items-center"
          >
            {#each OPCIONES_HERRAMIENTAS as opcion}
              <button
                on:click={() => {
                  herramientaIzquierda = opcion.id;
                  izquierdaColapsada = false; // Auto-abrir al seleccionar
                }}
                class="px-3 py-1.5 rounded-lg text-[9px] uppercase font-bold tracking-widest whitespace-nowrap transition-all {herramientaIzquierda ===
                opcion.id
                  ? esClaro
                    ? 'bg-indigo-100 text-indigo-900'
                    : 'bg-white/20 text-white'
                  : 'opacity-40 hover:opacity-100'} {izquierdaColapsada
                  ? 'hidden lg:hidden'
                  : ''}"
              >
                {opcion.icono}
                {opcion.label}
              </button>
              <!-- Icono Solo visible colapsado -->
              {#if izquierdaColapsada && herramientaIzquierda === opcion.id}
                <button class="px-2 py-1 bg-indigo-500/20 rounded">
                  {opcion.icono}
                </button>
              {/if}
            {/each}

            <!-- Boton Colapso (Visible Siempre) -->
            <button
              on:click={() => (izquierdaColapsada = !izquierdaColapsada)}
              class="ml-auto px-2 opacity-50 hover:opacity-100 text-xs"
              title={izquierdaColapsada ? "Expandir" : "Colapsar"}
            >
              {izquierdaColapsada
                ? window.innerWidth > 1024
                  ? "▶"
                  : "🔽"
                : window.innerWidth > 1024
                  ? "◀"
                  : "🔼"}
            </button>
          </nav>

          <!-- Contenido Izquierda -->
          <div
            class="flex-1 relative rounded-xl border {claseBorde} {claseTarjeta} overflow-hidden min-h-0 flex flex-col mt-2 {izquierdaColapsada
              ? 'hidden'
              : ''}"
          >
            {#if herramientaIzquierda === "biblioteca"}
              <div class="flex-1 overflow-y-auto p-4 custom-scrollbar">
                <Tabla datos={$biblioteca} {esClaro} />
              </div>
            {:else if herramientaIzquierda === "lector"}
              {#if $archivoAbierto}
                <div class="flex-1 overflow-hidden h-full">
                  <Lector {esClaro} />
                </div>
              {:else}
                <div
                  class="h-full flex items-center justify-center opacity-40 text-xs tracking-widest uppercase"
                >
                  Selecciona un libro de la biblioteca
                </div>
              {/if}
            {:else if herramientaIzquierda === "biblioteca_fisica"}
              <div class="flex-1 overflow-y-auto">
                <BibliotecaFisica {esClaro} />
              </div>
            {:else if herramientaIzquierda === "notas"}
              <Cuaderno {esClaro} />
            {:else if herramientaIzquierda === "asistente"}
              <AsistenteIA {esClaro} nombreUsuario={$usuario} />
            {:else if herramientaIzquierda === "biblia"}
              <WidgetBiblia {esClaro} />
            {:else if herramientaIzquierda === "diccionario"}
              <Diccionario {esClaro} />
            {/if}
          </div>
        </section>

        <!-- DIVISOR DESKTOP (Decorativo) -->
        <div class="hidden lg:block w-px bg-white/10 h-full mx-2"></div>

        <!-- ZONA DERECHA -->
        <section
          class="transition-all duration-500 ease-in-out relative flex flex-col
        {derechaColapsada
            ? 'flex-none h-12 lg:w-16 lg:h-full'
            : 'flex-1 min-h-0 lg:w-1/2'}"
        >
          <!-- Selector Derecha -->
          <nav
            class="flex flex-wrap gap-2 p-1 border-b {claseBorde} items-center justify-end"
          >
            <!-- Boton Colapso (Izquierda aligned) -->
            <button
              on:click={() => (derechaColapsada = !derechaColapsada)}
              class="mr-auto px-2 opacity-50 hover:opacity-100 text-xs"
              title={derechaColapsada ? "Expandir" : "Colapsar"}
            >
              {derechaColapsada
                ? window.innerWidth > 1024
                  ? "◀"
                  : "🔽"
                : window.innerWidth > 1024
                  ? "▶"
                  : "🔼"}
            </button>

            {#each OPCIONES_HERRAMIENTAS as opcion}
              <button
                on:click={() => {
                  herramientaDerecha = opcion.id;
                  derechaColapsada = false;
                }}
                class="px-3 py-1.5 rounded-lg text-[9px] uppercase font-bold tracking-widest whitespace-nowrap transition-all {herramientaDerecha ===
                opcion.id
                  ? esClaro
                    ? 'bg-indigo-100 text-indigo-900'
                    : 'bg-white/20 text-white'
                  : 'opacity-40 hover:opacity-100'} {derechaColapsada
                  ? 'hidden lg:hidden'
                  : ''}"
              >
                {opcion.icono}
                {opcion.label}
              </button>
              {#if derechaColapsada && herramientaDerecha === opcion.id}
                <button class="px-2 py-1 bg-indigo-500/20 rounded">
                  {opcion.icono}
                </button>
              {/if}
            {/each}
          </nav>

          <!-- Contenido Derecha -->
          <div
            class="flex-1 relative rounded-xl border {claseBorde} {claseTarjeta} overflow-hidden min-h-0 flex flex-col mt-2 {derechaColapsada
              ? 'hidden'
              : ''}"
          >
            {#if herramientaDerecha === "biblioteca"}
              <div class="flex-1 overflow-y-auto p-4 custom-scrollbar">
                <Tabla datos={$biblioteca} {esClaro} />
              </div>
            {:else if herramientaDerecha === "lector"}
              {#if $archivoAbierto}
                <div class="flex-1 overflow-hidden h-full">
                  <Lector {esClaro} />
                </div>
              {:else}
                <div
                  class="h-full flex items-center justify-center opacity-40 text-xs tracking-widest uppercase"
                >
                  Selecciona un libro de la biblioteca
                </div>
              {/if}
            {:else if herramientaDerecha === "biblioteca_fisica"}
              <div class="flex-1 overflow-y-auto">
                <BibliotecaFisica {esClaro} />
              </div>
            {:else if herramientaDerecha === "notas"}
              <div class="flex-1 h-full flex flex-col">
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
          &copy; {new Date().getFullYear()}
          <a
            href="mailto:hdaguila@gmail.com"
            class="hover:text-indigo-500 transition-colors">Héctor Aguila</a
          >
        </div>
        <div
          class="text-[10px] font-bold tracking-widest mt-1 uppercase cursor-default"
        >
          >Un Soñador con Poca Ram 👨🏻‍💻
        </div>
      </footer>
    </div>
  </div>

  <Toaster />

  {#if mostrarAcercaDe}
    <ModalAcercaDe {esClaro} on:close={() => (mostrarAcercaDe = false)} />
  {/if}
{/if}

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
