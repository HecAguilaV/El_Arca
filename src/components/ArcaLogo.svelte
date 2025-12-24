<script>
    export let size = "w-10 h-10";
    export let color = "text-indigo-500";
</script>

<svg
    class="{size} {color}"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
>
    <!-- Base del Arca / Libro Abierto -->
    <path
        d="M12 21C12 21 4 20 4 12V4C4 4 8 3 12 5C16 3 20 4 20 4V12C20 20 12 21 12 21Z"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
    />
    <!-- Linea Central (Lomo / Mástil) -->
    <path
        d="M12 5V21"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
    />
    <!-- Detalles de páginas / Tablas del arca -->
    <path
        d="M6 9C6 9 9 8 12 9"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-opacity="0.5"
        stroke-linecap="round"
    />
    <path
        d="M6 13C6 13 9 12 12 13"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-opacity="0.5"
        stroke-linecap="round"
    />
    <path
        d="M18 9C18 9 15 8 12 9"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-opacity="0.5"
        stroke-linecap="round"
    />
    <path
        d="M18 13C18 13 15 12 12 13"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-opacity="0.5"
        stroke-linecap="round"
    />
</svg>
