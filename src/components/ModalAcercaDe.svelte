<script>
    import { fade, scale } from "svelte/transition";
    import { createEventDispatcher } from "svelte";
    import { X, Info } from "phosphor-svelte";

    export let esClaro = false;

    const dispatch = createEventDispatcher();

    function cerrar() {
        dispatch("close");
    }
</script>

<div
    class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
    transition:fade
    on:click={cerrar}
>
    <!-- Contenido del Modal -->
    <div
        class="w-full max-w-2xl p-8 rounded-2xl shadow-2xl relative overflow-hidden transition-colors duration-300 max-h-[85vh] overflow-y-auto {esClaro
            ? 'bg-[#fafaf9] text-stone-800'
            : 'bg-[#18181e] text-stone-200'}"
        transition:scale={{ start: 0.95 }}
        on:click|stopPropagation
    >
        <!-- Decoración Superior -->
        <div class="absolute top-0 left-0 w-full h-1 bg-amber-500/50"></div>

        <!-- Botón Cerrar -->
        <button
            on:click={cerrar}
            class="absolute top-4 right-4 p-2 rounded-full hover:bg-black/10 transition-colors opacity-50 hover:opacity-100"
        >
            <X size={20} />
        </button>

        <!-- Cabecera -->
        <div class="text-center mb-6">
            <h2
                class="text-2xl font-black tracking-tighter uppercase {esClaro
                    ? 'text-indigo-950'
                    : 'text-white'}"
            >
                Acerca de El Arca
            </h2>
            <p
                class="text-[10px] uppercase font-bold tracking-[0.2em] text-amber-500 opacity-80 mt-2"
            >
                Estudio Bíblico & Teológico Digital
            </p>
        </div>

        <!-- Contenido (Prose) -->
        <div
            class="prose prose-sm max-w-none text-justify {esClaro
                ? 'prose-stone'
                : 'prose-invert'} leading-relaxed opacity-90"
        >
            <h3 class="font-bold text-amber-500">Saludo de Bienvenida</h3>

            <p>
                Hola, soy <strong>Héctor</strong>, desarrollador de este espacio
                de estudio bíblico.
            </p>

            <p>
                A quien le comparta esta aplicación o tenga acceso, decir que es
                una idea nacida de la necesidad de tener un lugar de <em
                    >inmersión</em
                > en el estudio de la Palabra, que por lo general ha sido físico,
                pero teniendo en cuenta que hoy en día la digitalización es ya parte
                de nuestras vidas, ¿por qué no tener un espacio como tal?
            </p>

            <figure
                class="my-4 p-4 border-l-2 border-amber-500/30 bg-amber-500/5 rounded-r-lg italic text-xs opacity-70"
            >
                "Inspirado por otras ideas de nivel estratosféricamente
                profesionales..."
            </figure>

            <p>
                Así, inspirado por herramientas como <em>Logos</em> o
                <em>e-Sword</em>, creé esta aplicación web llamada
                <strong>El Arca</strong>, donde he subido varios archivos
                digitales recopilados a través del tiempo entre mi familia y
                amigos. Con un total en el comienzo de 1199 archivos con
                distintos tipos de libros, manualidades, etc. Se ha conformado
                la biblioteca digital.
            </p>

            <p>
                Estoy trabajando para poder indexar todos los archivos y poder
                crear etiquetas que relacione todos los archivos con
                determinados temas. Por lo pronto, trabajaré en la
                categorización y renombrado correcto de los archivos para una
                mejor búsqueda de estos.
            </p>

            <p class="font-medium text-center mt-6 text-amber-500">
                "Finalmente, quiero desearles a todos una experiencia
                enriquecedora y que realmente pueda ser un aporte o un valor
                agregado al estudio de la Palabra de Dios y el estudio
                Teológico."
            </p>
        </div>

        <!-- Footer -->
        <div
            class="mt-8 pt-6 border-t border-dashed {esClaro
                ? 'border-stone-300'
                : 'border-white/10'} text-center"
        >
            <div class="text-[10px] font-medium tracking-tight opacity-50">
                &copy; {new Date().getFullYear()} Héctor Aguila &bull; Desarrollado para el Servicio de Apoyo a la Iglesia
            </div>
        </div>
    </div>
</div>
