<script>
  import { onMount, onDestroy } from "svelte";
  import { fade } from "svelte/transition"; // Importar transición
  import { Toaster } from "svelte-french-toast";
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

  // Estado Local
  let mostrarBienvenida = false;
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
        // LOGOUT O NO LOGUEADO - LIMPIEZA DE SESIÓN
        detenerMusica(); // 1. Parar música
        archivoAbierto.set(null); // 2. Cerrar lector
        izquierdaColapsada = false; // 3. Reset layout
        derechaColapsada = false;

        const legacyUser = localStorage.getItem("arca_usuario");
        if (legacyUser) {
          usuario.set(legacyUser);
          await cargarTodo(); // Cargar legacy si existe
        } else {
          usuario.set(null);
          // 4. Vaciar datos sensibles visualmente
          biblioteca.set([]);
          notas.set([]);

          mostrarBienvenida = true;
          // Cargar notas públicas/sistema para que el login no se vea vacío
          await cargarTodo();
        }
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
                <button
                  on:click={async () => {
                    localStorage.removeItem("arca_usuario"); // Limpiar legacy
                    usuario.set(null);
                    await manejarLogout();
                  }}
                  class="ml-2 text-[8px] text-red-400 hover:text-red-300 uppercase font-bold tracking-wider"
                  >(Salir)</button
                >
              </div>
            {:else}
              <!-- Botón de Login (o Mostrar Modal si está "atascado" como invitado sin nombre) -->
              {#if $usuario && !$usuario.includes("Invitado")}
                <!-- Caso Borde: Usuario Legacy detectado pero sin Firebase -->
                <div class="flex items-center gap-2 mt-1">
                  <span
                    class="text-[8px] md:text-[9px] uppercase tracking-[0.3em] opacity-60 font-bold"
                  >
                    {$usuario} (Local)
                  </span>
                  <button
                    on:click={() => {
                      localStorage.removeItem("arca_usuario");
                      usuario.set(null);
                      mostrarBienvenida = true;
                    }}
                    class="ml-2 text-[8px] text-indigo-400 hover:text-indigo-300 uppercase font-bold tracking-wider"
                    >(Conectar)</button
                  >
                </div>
              {:else}
                <button
                  on:click={() => {
                    mostrarBienvenida = true;
                  }}
                  class="group flex items-center gap-2 text-[8px] md:text-[9px] uppercase tracking-[0.3em] opacity-60 hover:opacity-100 hover:text-indigo-400 font-bold mt-1 text-left transition-all"
                >
                  <!-- Google G Logo (Grayscale to Color on Hover) -->
                  <svg
                    class="w-3 h-3 grayscale group-hover:grayscale-0 transition-all"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      fill="#4285F4"
                    />
                    <path
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      fill="#34A853"
                    />
                    <path
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      fill="#FBBC05"
                    />
                    <path
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      fill="#EA4335"
                    />
                  </svg>
                  Inicia Sesión
                </button>
              {/if}
            {/if}
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

{#if cargandoAuth}
  <div
    class="flex h-screen w-full flex-col items-center justify-center bg-gray-900 text-white"
  >
    <div
      class="h-12 w-12 animate-spin rounded-full border-4 border-amber-500 border-t-transparent"
    ></div>
    <p class="mt-4 animate-pulse text-gray-400">Cargando El Arca...</p>
  </div>
{:else if mostrarBienvenida}
  <div in:fade={{ duration: 300 }}>
    <ModalBienvenida {esClaro} on:save={manejarGuardadoUsuario} />
  </div>
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
