<script>
    import iconBook from "../assets/icons/book.svg";
    import iconPdf from "../assets/icons/file-pdf.svg";
    import iconPpt from "../assets/icons/presentation.svg";
    import iconFile from "../assets/icons/files.svg";

    export let data = [];

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
</script>

<div
    class="bg-white/5 border border-white/10 rounded-xl overflow-hidden backdrop-blur-md flex flex-col h-[600px]"
>
    <!-- Search Bar -->
    <div
        class="p-4 border-b border-white/10 flex items-center gap-4 bg-black/20"
    >
        <div class="w-5 h-5 opacity-50 flex items-center justify-center">
            🔍
        </div>
        <input
            type="text"
            bind:value={searchTerm}
            placeholder="Buscar por nombre, autor, teología..."
            class="flex-1 bg-transparent border-none text-white placeholder-slate-500 focus:outline-none focus:ring-0 text-sm"
        />
        <div
            class="bg-white/10 px-3 py-1 rounded-full text-xs text-slate-400 font-medium"
        >
            {filteredData.length} resultados
        </div>
    </div>

    <!-- Table Wrapper -->
    <div class="overflow-auto flex-1">
        <table class="w-full text-left border-collapse">
            <thead class="sticky top-0 bg-[#1a1a20] z-10 shadow-sm">
                <tr>
                    <th
                        class="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider cursor-pointer hover:text-white select-none group"
                        on:click={() => toggleSort("filename")}
                    >
                        Archivo {sortField === "filename"
                            ? sortDirection === "asc"
                                ? "↑"
                                : "↓"
                            : ""}
                    </th>
                    <th
                        class="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider cursor-pointer hover:text-white select-none group"
                        on:click={() => toggleSort("category")}
                    >
                        Categoría {sortField === "category"
                            ? sortDirection === "asc"
                                ? "↑"
                                : "↓"
                            : ""}
                    </th>
                    <th
                        class="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider cursor-pointer hover:text-white select-none group"
                        on:click={() => toggleSort("page_count")}
                    >
                        Páginas {sortField === "page_count"
                            ? sortDirection === "asc"
                                ? "↑"
                                : "↓"
                            : ""}
                    </th>
                    <th
                        class="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider"
                        >Etiquetas</th
                    >
                </tr>
            </thead>
            <tbody class="divide-y divide-white/5">
                {#each filteredData.slice(0, 100) as row (row.md5_hash + row.path)}
                    <tr class="hover:bg-white/[0.02] transition-colors group">
                        <td class="p-4 flex items-center gap-3">
                            <a
                                href="/library/{row.path
                                    .split('\\')
                                    .map(encodeURIComponent)
                                    .join('/')}"
                                target="_blank"
                                class="flex items-center gap-3 group/link w-full"
                            >
                                <img
                                    src={getIcon(row.format)}
                                    alt={row.format}
                                    class="w-8 h-8 opacity-80 group-hover/link:opacity-100 transition-opacity"
                                />
                                <div class="overflow-hidden">
                                    <div
                                        class="text-sm font-medium text-slate-200 truncate group-hover/link:text-indigo-400 transition-colors"
                                        title={row.filename}
                                    >
                                        {row.filename}
                                    </div>
                                    <div
                                        class="text-xs text-slate-500 truncate font-mono mt-0.5"
                                        title={row.path}
                                    >
                                        {row.path}
                                    </div>
                                </div>
                            </a>
                        </td>
                        <td class="p-4">
                            <button
                                on:click={() => setCategoryFilter(row.category)}
                                class="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700 cursor-pointer transition-colors"
                            >
                                {row.category}
                            </button>
                        </td>
                        <td class="p-4 text-sm text-slate-400 tabular-nums">
                            {row.page_count}
                        </td>
                        <td class="p-4">
                            <div class="flex flex-wrap gap-2">
                                {#if row.tags}
                                    {#each row.tags.split(", ") as tag}
                                        {#if tag}
                                            <span
                                                class="inline-flex items-center px-2 py-0.5 rounded text-xs text-slate-300 bg-white/10 hover:bg-white/20 transition-colors cursor-default"
                                            >
                                                {tag}
                                            </span>
                                        {/if}
                                    {/each}
                                {:else}
                                    <span class="text-slate-600 text-xs">-</span
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
                class="p-4 text-center text-xs text-slate-500 border-t border-white/5"
            >
                Mostrando los primeros 100 resultados para optimizar
                rendimiento...
            </div>
        {/if}
    </div>
</div>
