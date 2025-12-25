<script>
    import iconBook from "../assets/icons/book.svg";
    import iconPdf from "../assets/icons/file-pdf.svg";
    import iconPpt from "../assets/icons/presentation.svg";
    import iconFile from "../assets/icons/files.svg";

    export let data = [];
    export let isLight = false;

    let searchTerm = "";

    // Sorting State
    let sortField = "filename"; // 'filename' | 'category' | 'page_count'
    let sortDirection = "asc"; // 'asc' | 'desc'

    function toggleSort(field) {
        if (sortField === field) {
            sortDirection = sortDirection === "asc" ? "desc" : "asc";
        } else {
            sortField = field;
            sortDirection = "asc";
        }
    }

    export function applyExternalFilter(type, value) {
        // Mapeo simple: si es categoría, usamos setCategoryFilter
        // Si es tag, lo ponemos en el buscador o lógica especial
        if (type === "category") {
            searchTerm = value;
        } else if (type === "tag") {
            searchTerm = value;
        } else if (type === "format") {
            // Hack: poner formato en búsqueda
            searchTerm = value;
        } else if (type === "author") {
            searchTerm = value;
        }
    }

    function setCategoryFilter(category) {
        searchTerm = category;
    }

    $: filteredData = data
        .filter((item) => {
            if (!searchTerm) return true;
            const term = searchTerm.toLowerCase();
            return (
                item.filename.toLowerCase().includes(term) ||
                (item.tags && item.tags.toLowerCase().includes(term)) ||
                item.category.toLowerCase().includes(term)
            );
        })
        .sort((a, b) => {
            let valA = a[sortField];
            let valB = b[sortField];

            // Handle numeric sorting for pages
            if (sortField === "page_count") {
                valA = Number(valA) || 0;
                valB = Number(valB) || 0;
            } else {
                valA = valA.toString().toLowerCase();
                valB = valB.toString().toLowerCase();
            }

            if (valA < valB) return sortDirection === "asc" ? -1 : 1;
            if (valA > valB) return sortDirection === "asc" ? 1 : -1;
            return 0;
        });

    function getIcon(format) {
        if (format === "fisico") return iconBook;
        if (format === "pptx" || format === "ppt") return iconPpt;
        if (format === "pdf" || format === "epub") return iconPdf;
        return iconFile;
    }

    function copyPath(path) {
        navigator.clipboard.writeText(path);
    }

    // Detectar si estamos en Vercel/Web (no local)
    const isWeb =
        typeof window !== "undefined" &&
        window.location.hostname.includes("vercel.app");

    function handleFileClick(e) {
        if (isWeb) {
            e.preventDefault();
            // Importar toast dinámicamente o asumiendo que está disponible si se pasa al componente,
            // pero para ser seguros usaremos alert o un toast global si es fácil.
            // Como no tenemos toast importado aquí, usaremos alert simple o nada.
            // Mejor: Despachar evento o usar la prop 'isWeb' para condicional.
            alert(
                "⚠️ Estás en la versión Web.\n\nLos archivos grandes no se alojan aquí por velocidad.\nUsa el botón 'Nube' (Cloud) en el menú superior para acceder a los archivos en Google Drive.",
            );
        }
    }

    // Dynamic Classes
    $: containerClass = isLight
        ? "bg-[#fafaf9] border-stone-300"
        : "bg-white/5 border-white/10";

    $: searchBarClass = isLight
        ? "bg-stone-200 border-stone-300"
        : "bg-black/20 border-white/10";
    $: searchInputClass = isLight
        ? "text-stone-800 placeholder-stone-500"
        : "text-white placeholder-slate-500";
    $: theadClass = isLight
        ? "bg-stone-100 border-b border-stone-200"
        : "bg-[#1a1a20]";
    $: thTextClass = isLight
        ? "text-stone-600 hover:text-stone-800"
        : "text-slate-400 hover:text-white";
    $: rowHoverClass = isLight ? "hover:bg-stone-100" : "hover:bg-white/[0.02]";
    $: textMainClass = isLight ? "text-stone-900" : "text-slate-200";
    $: textSubClass = isLight ? "text-stone-500" : "text-slate-500";
    $: borderDivideClass = isLight ? "divide-stone-200" : "divide-white/5";
</script>

<div
    class="{containerClass} border rounded-xl overflow-hidden backdrop-blur-md flex flex-col h-[600px] transition-colors duration-500"
>
    <!-- Search Bar -->
    <div
        class="p-4 border-b {searchBarClass} flex items-center gap-4 transition-colors"
    >
        <div class="w-5 h-5 opacity-50 flex items-center justify-center">
            🔍
        </div>
        <input
            type="text"
            bind:value={searchTerm}
            placeholder="Buscar por nombre, autor, teología..."
            class="flex-1 bg-transparent border-none focus:outline-none focus:ring-0 text-sm {searchInputClass}"
        />
        <div
            class="bg-white/10 px-3 py-1 rounded-full text-xs opacity-70 font-medium"
        >
            {filteredData.length} resultados
        </div>
    </div>

    <!-- Table Wrapper -->
    <div class="overflow-auto flex-1">
        <table class="w-full text-left border-collapse">
            <thead
                class="sticky top-0 z-10 shadow-sm {theadClass} transition-colors"
            >
                <tr>
                    <th
                        class="p-4 text-xs font-semibold uppercase tracking-wider cursor-pointer select-none group {thTextClass}"
                        on:click={() => toggleSort("filename")}
                    >
                        Archivo {sortField === "filename"
                            ? sortDirection === "asc"
                                ? "↑"
                                : "↓"
                            : ""}
                    </th>
                    <th
                        class="p-4 text-xs font-semibold uppercase tracking-wider cursor-pointer select-none group {thTextClass}"
                        on:click={() => toggleSort("category")}
                    >
                        Categoría {sortField === "category"
                            ? sortDirection === "asc"
                                ? "↑"
                                : "↓"
                            : ""}
                    </th>
                    <th
                        class="p-4 text-xs font-semibold uppercase tracking-wider cursor-pointer select-none group {thTextClass}"
                        on:click={() => toggleSort("page_count")}
                    >
                        Páginas {sortField === "page_count"
                            ? sortDirection === "asc"
                                ? "↑"
                                : "↓"
                            : ""}
                    </th>
                    <th
                        class="p-4 text-xs font-semibold uppercase tracking-wider {thTextClass}"
                        >Etiquetas</th
                    >
                </tr>
            </thead>
            <tbody class="divide-y {borderDivideClass}">
                {#each filteredData.slice(0, 100) as row (row.md5_hash + row.path)}
                    <tr class="{rowHoverClass} transition-colors group">
                        <td class="p-4 flex items-center gap-3">
                            <a
                                href="/library/{row.path
                                    .split('\\')
                                    .map(encodeURIComponent)
                                    .join('/')}"
                                target="_blank"
                                on:click={handleFileClick}
                                class="flex items-center gap-3 group/link w-full"
                            >
                                <img
                                    src={getIcon(row.format)}
                                    alt={row.format}
                                    class="w-8 h-8 transition-all {isLight
                                        ? 'opacity-80 sepia-[.3] hover:sepia-0'
                                        : 'opacity-80 hover:opacity-100 brightness-110'}"
                                />
                                <div class="overflow-hidden">
                                    <div
                                        class="text-sm font-medium truncate group-hover/link:text-indigo-500 transition-colors {textMainClass}"
                                        title={row.filename}
                                    >
                                        {row.filename}
                                    </div>
                                    <!-- Only show path if different from filename -->
                                    {#if row.path !== row.filename}
                                        <div
                                            class="text-xs truncate font-mono mt-0.5 {textSubClass}"
                                            title={row.path}
                                        >
                                            {row.path}
                                        </div>
                                    {/if}
                                </div>
                            </a>
                        </td>
                        <td class="p-4">
                            <button
                                on:click={() => setCategoryFilter(row.category)}
                                class="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium border cursor-pointer transition-colors {isLight
                                    ? 'bg-stone-200 text-stone-700 border-stone-300 hover:bg-stone-300'
                                    : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'}"
                            >
                                {row.category}
                            </button>
                        </td>
                        <td class="p-4 text-sm tabular-nums {textSubClass}">
                            {row.page_count}
                        </td>
                        <td class="p-4">
                            <div class="flex flex-wrap gap-2">
                                {#if row.tags}
                                    {#each row.tags.split(", ") as tag}
                                        {#if tag}
                                            <span
                                                class="inline-flex items-center px-2 py-0.5 rounded text-xs transition-colors cursor-default {isLight
                                                    ? 'text-stone-600 bg-stone-100 border border-stone-200'
                                                    : 'text-slate-300 bg-white/10 hover:bg-white/20'}"
                                            >
                                                {tag}
                                            </span>
                                        {/if}
                                    {/each}
                                {:else}
                                    <span class="{textSubClass} text-xs">-</span
                                    >
                                {/if}
                            </div>
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>

        {#if filteredData.length > 100}
            <div
                class="p-4 text-center text-xs {textSubClass} border-t {isLight
                    ? 'border-stone-200'
                    : 'border-white/5'}"
            >
                Mostrando los primeros 100 resultados para optimizar
                rendimiento...
            </div>
        {/if}
    </div>
</div>
