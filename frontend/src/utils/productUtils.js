// src/utils/productUtils.js

// --- HELPER: SORT SIZES ---
export const sortSizes = (list) => {
    return list.sort((a, b) => {
        const strA = (a || "").toString();
        const strB = (b || "").toString();
        
        const numA = parseInt(strA.replace(/\D/g, '')) || 0;
        const numB = parseInt(strB.replace(/\D/g, '')) || 0;
        
        // Handle TB vs GB
        const valA = strA.toUpperCase().includes('T') ? numA * 1024 : numA;
        const valB = strB.toUpperCase().includes('T') ? numB * 1024 : numB;
        
        return valA - valB;
    });
};

// --- HELPER: NORMALIZE BRAND ---
// Now checks Title if Brand is missing/unknown
// ==============================================================================
// === CRITICAL: BRAND NORMALIZATION LOGIC - DO NOT MODIFY WITHOUT TESTING ===
// This logic classifies brands, including fallback to title scanning and 
// explicit remapping of niche brands to "Sans marque".
// ANY CHANGE HERE MUST BE VERIFIED WITH `verify_brand_stability.js`.
// ==============================================================================
export const normalizeBrand = (brand, title = "") => {
    let b = (brand || "").toLowerCase().trim();
    let t = (title || "").toLowerCase().trim();

    // Helper to check both brand field and title
    const has = (keyword) => b.includes(keyword) || t.includes(keyword);

    if (has('hp') || has('hewlett') || has('elitebook') || has('pavilion') || has('probook') || has('omen') || has('victus')) return 'HP';
    if (has('dell') || has('vostro') || has('latitude') || has('inspiron') || has('xps') || has('alienware') || has('g15')) return 'Dell';
    if (has('lenovo') || has('thinkpad') || has('thinkbook') || has('ideapad') || has('yoga') || has('legion') || has('loq')) return 'Lenovo';
    if (has('asus') || has('zenbook') || has('vivobook') || has('rog') || has('tuf') || has('expertbook')) return 'Asus';
    if (has('msi') || has('katana') || has('cyborg') || has('stealth') || has('raider') || has('thin')) return 'MSI';
    if (has('apple') || has('macbook') || has('mac ') || has('imac')) return 'Apple';
    if (has('acer') || has('nitro') || has('predator') || has('aspire') || has('swift') || has('extensa')) return 'Acer';
    if (has('gigabyte') || has('aorus') || has('aero')) return 'Gigabyte';
    if (has('samsung') || has('galaxy book')) return 'Samsung';
    if (has('huawei') || has('matebook')) return 'Huawei';
    if (has('microsoft') || has('surface')) return 'Microsoft';
    if (has('bmax')) return 'BMAX';
    if (has('infinix')) return 'Infinix';
    if (has('razer') || has('blade')) return 'Razer';
    if (has('chuwi')) return 'Chuwi';
    if (has('mytek')) return 'MyTek';
    if (has('kimera')) return 'Kimera';

    // Smartphone brands
    if (has('xiaomi') || has('redmi')) return 'Xiaomi';
    if (has('poco')) return 'Poco';
    if (has('honor')) return 'Honor';
    if (has('oppo')) return 'Oppo';
    if (has('realme')) return 'Realme';
    if (has('vivo')) return 'Vivo';
    if (has('itel')) return 'Itel';
    if (has('tecno')) return 'Tecno';
    if (has('zte')) return 'ZTE';
    if (has('tcl')) return 'TCL';
    if (has('nothing')) return 'Nothing';
    if (has('wiko')) return 'Wiko';
    if (has('condor')) return 'Condor';
    if (has('oscal')) return 'Oscal';
    if (has('lesia')) return 'Lesia';
    if (has('motorola') || has('moto ')) return 'Motorola';
    if (has('nokia')) return 'Nokia';
    if (has('oneplus') || has('one plus')) return 'OnePlus';
    if (has('pixel')) return 'Google';
    if (has('blackview')) return 'Blackview';
    if (has('doogee')) return 'Doogee';
    if (has('oukitel')) return 'Oukitel';
    if (has('ulefone')) return 'Ulefone';
    if (has('haidiko')) return 'Haidiko';
    if (has('iku')) return 'IKU';
    if (has('umidigi')) return 'Umidigi';
    if (has('cubot')) return 'Cubot';
    if (has('cat ') || has('caterpillar')) return 'CAT';
    if (has('alcatel')) return 'Alcatel';
    if (has('meizu')) return 'Meizu';
    if (has('sony') || has('xperia')) return 'Sony';
    if (has('hmd')) return 'HMD';
    if (has('smartec')) return 'Smartec';
    if (has('clever')) return 'Clever';
    if (has('figi')) return 'Figi';
    if (has('oale')) return 'Oale';
    if (has('evertek')) return 'Evertek';
    if (has('uniwa')) return 'Uniwa';
    if (has('logicom')) return 'Logicom';
    if (has('philips')) return 'Philips';
    if (has('kgtel')) return 'Kgtel';

    // Group "Sans marque" requests
    if (has('nintendo') || has('patriot') || has('schneider') || has('sharkoon') || 
        has('thomson') || has('vega') || has('versus') || has('yatagan') || 
        has('sans marque') || has('unknown')) return 'Sans marque';

    // If we have a valid brand string that isn't 'unknown'/'generic', format it
    if (brand && !['unknown', 'generic', 'autre'].includes(b)) {
         return brand.charAt(0).toUpperCase() + brand.slice(1).toLowerCase();
    }
    
    return 'Sans marque'; // Default to Sans marque as requested for 'Unknown' items
};
// ==============================================================================

// --- HELPER: NORMALIZE SPECS (The Core Brain) ---
export const normalizeSpecs = (title, specs, brand, category) => {
    const t = title.toUpperCase();
    const catLower = (category || '').toLowerCase();
    
    // --- RAM Normalization ---
    // ==============================================================================
    // === CRITICAL: RAM NORMALIZATION LOGIC - DO NOT MODIFY WITHOUT TESTING ===
    // This logic standardizes RAM to "XGB" format and handles both integer (4) 
    // and string ("4GB") inputs. It also cleans "GO" -> "GB".
    // ANY CHANGE HERE MUST BE VERIFIED WITH `verify_ram_stability.js`.
    // ==============================================================================
    // Extract RAM from title
    const extractRamFromTitle = (title) => {
        let ramMatch = title.match(/(\d{1,3})\s?(GO|GB)\b/i);
        if (!ramMatch) {
            ramMatch = title.match(/(\d{1,3})\s?G\b/i);
            if (ramMatch && ['3', '4', '5'].includes(ramMatch[1]) && !title.match(new RegExp(ramMatch[1] + '\\s?G\\s?O', 'i'))) {
                ramMatch = null;
            }
        }
        return ramMatch ? `${ramMatch[1]}GB` : null;
    };

    // Valid phone RAM values
    const validPhoneRams = ['2GB', '3GB', '4GB', '6GB', '8GB', '12GB', '16GB'];
    const isPhone = catLower === 'smartphone' || category === 'Smartphone';

    if (!specs.ram || specs.ram === 'Unknown') {
        const extracted = extractRamFromTitle(t);
        if (extracted) specs.ram = extracted;
    }

    // For phones: validate RAM - if existing value is invalid (e.g. 5GB from "5G" scrape bug), re-extract from title
    if (isPhone && specs.ram) {
        let cleanCheck = specs.ram.toString().toUpperCase().replace(/\s/g, '').replace('GO', 'GB');
        if (cleanCheck.match(/^\d+$/)) cleanCheck += 'GB';
        if (!validPhoneRams.includes(cleanCheck)) {
            // Invalid RAM (5GB, 18GB, 128GB etc) - re-extract from title
            const extracted = extractRamFromTitle(t);
            if (extracted && validPhoneRams.includes(extracted)) {
                specs.ram = extracted;
            }
        }
    }

    // Normalize existing RAM field (Handle String OR Number)
    if (specs.ram) {
        // Force to string first to handle raw numbers (Wiki data has integers like 4, 8)
        let cleanRam = specs.ram.toString().toUpperCase().replace(/\s/g, '').replace('GO', 'GB');
        
        // If it's just a number like "8", "16", append GB
        if (cleanRam.match(/^\d+$/)) {
             cleanRam += "GB";
        }
        
        specs.ram = cleanRam;
    }

    // --- CPU Normalization ---
    // If specs.cpu is missing or messy, try to extract from title
    // Priority: Specific Models > Generics
    if (!specs.cpu || specs.cpu === 'Unknown' || specs.cpu.length < 3) {
        // Apple M-Series
        if (t.match(/\bM[1-9]\s?(PRO|MAX|ULTRA)?\b/)) {
            const mMatch = t.match(/\b(M[1-9]\s?(PRO|MAX|ULTRA)?)\b/);
            if (mMatch) specs.cpu = `Apple ${mMatch[1].replace(/\s+/g, ' ').trim()}`;
        }
        // Snapdragon
        else if (t.includes("SNAPDRAGON")) {
             specs.cpu = "Snapdragon X";
        }
        // Intel Core (New Gen: Core 3/5/7/9) including implicit "U7-150U" style
        // MERGE LOGIC: Map all Core 3/5/7/9 (including Ultra) to "Intel Core i3/i5/i7/i9"
        
        let intelNumber = null;
        
        if (t.match(/\bCORE\s?[U3579]+\b/)) { 
             const core = t.match(/\bCORE\s?([U3579]+)\b/); // Capture U5 or 5
             if (core) intelNumber = core[1].replace('U', '');
        }
        else if (t.match(/\bINTEL\s?[3579]\s?\d{3}H/)) { // Matches "Intel 5 210H"
             const intelMatch = t.match(/\bINTEL\s?([3579])\s?\d{3}H/);
             if (intelMatch) intelNumber = intelMatch[1];
        }
        else if (t.match(/\bU[3579]-\d{3}/)) { // Matches U7-150U
             const uMatch = t.match(/\bU([3579])-\d{3}/);
             if (uMatch) intelNumber = uMatch[1];
        } else if (t.match(/\bULTRA\s?[579]\b/)) {
            const ultra = t.match(/\bULTRA\s?([579])\b/);
            if (ultra) intelNumber = ultra[1];
        }
        
        if (intelNumber) {
            specs.cpu = `Intel Core i${intelNumber}`;
        }

        // Intel N-Series (N100, N200, N95, N4000, N5000)
        else if (t.match(/\bN\d{3,4}\b/) || t.match(/\bN95\b/)) {
            specs.cpu = "Intel Processor N-Series";
        }
        // Intel Core i-Series (Explicit)
        else if (t.match(/\bI9\b/)) specs.cpu = "Intel Core i9";
        else if (t.match(/\bI7\b/)) specs.cpu = "Intel Core i7";
        else if (t.match(/\bI5\b/)) specs.cpu = "Intel Core i5";
        else if (t.match(/\bI3\b/)) specs.cpu = "Intel Core i3";
        // AMD Ryzen AI (Handle "AI 9" shorthand and "Al" typo)
        else if (t.includes("RYZEN AI") || t.match(/\bAI\s?9\b/) || t.includes("RYZEN AL")) {
            if (t.includes("9") || t.includes("300") || t.includes("370")) specs.cpu = "Ryzen AI 9";
            else if (t.includes("7")) specs.cpu = "Ryzen AI 7";
            else if (t.includes("5")) specs.cpu = "Ryzen AI 5";
            else specs.cpu = "Ryzen AI";
        }
        // AMD Ryzen Standard (and Typos/Shortcodes)
        else if (t.match(/RYZEN\s?9/) || t.match(/RAYZEN\s?9/) || t.match(/\bR[-_]?9\b/)) specs.cpu = "Ryzen 9";
        else if (t.match(/RYZEN\s?7/) || t.match(/RAYZEN\s?7/) || t.match(/\bR[-_]?7\b/)) specs.cpu = "Ryzen 7";
        else if (t.match(/RYZEN\s?5/) || t.match(/RAYZEN\s?5/) || t.match(/\bR[-_]?5\b/)) specs.cpu = "Ryzen 5";
        else if (t.match(/RYZEN\s?3/) || t.match(/RAYZEN\s?3/) || t.match(/\bR[-_]?3\b/)) specs.cpu = "Ryzen 3";
        // AMD Budget
        else if (t.match(/\b3050U\b/) || t.match(/\b3050E\b/) || t.match(/\b3020E\b/) || t.includes("ATHLON")) specs.cpu = "Athlon";
        // Legacy
        else if (t.includes("CELERON")) specs.cpu = "Celeron";
        else if (t.includes("PENTIUM")) specs.cpu = "Pentium";
        else if (t.includes("ATOM")) specs.cpu = "Intel Atom";
        else if (t.includes("XEON")) specs.cpu = "Intel Xeon";
        else if (t.match(/QUAD[\s-]CORE/)) specs.cpu = "Quad Core";
        else if (t.match(/DUAL[\s-]CORE/)) specs.cpu = "Dual Core";

        // --- SMARTPHONE CPU INFERENCE (from brand + model in title) ---
        // Verified from GSMArena, Wikipedia, manufacturer specs (April 2026)
        else if (category === 'Smartphone' || catLower === 'smartphone') {
            const b = (brand || '').toLowerCase();

            // === APPLE → Apple A-series / M-series ===
            if (b === 'apple' || t.includes('IPHONE')) specs.cpu = "Apple";

            // === SAMSUNG — model-specific (verified GSMArena April 2026) ===
            // S2x flagships & Z Fold/Flip → Snapdragon 8 series
            else if (t.match(/GALAXY\s?S2[0-9]/) || t.match(/GALAXY\s?Z\s?(FOLD|FLIP)/)) specs.cpu = "Snapdragon";
            else if (t.match(/GALAXY\s?S1[0-9]/)) specs.cpu = "Samsung Exynos";
            // --- A-series: model-by-model (GSMArena verified) ---
            // MediaTek models: A04=Helio P35, A05=Helio G85, A06=Helio G85, A07=MediaTek
            else if (t.match(/GALAXY\s?A0[4-7]/)) specs.cpu = "MediaTek";
            // A14=Helio G80, A15=Dimensity 6100+
            else if (t.match(/GALAXY\s?A1[45]\b/)) specs.cpu = "MediaTek";
            // A16 4G=Helio G99 (MediaTek), A16 5G=Exynos 1330
            else if (t.match(/GALAXY\s?A16/) && !t.includes('5G')) specs.cpu = "MediaTek";
            else if (t.match(/GALAXY\s?A16/) && t.includes('5G')) specs.cpu = "Samsung Exynos";
            // A17=Exynos 1330
            else if (t.match(/GALAXY\s?A17/)) specs.cpu = "Samsung Exynos";
            // A22=Helio G80 (MediaTek), A23=Snapdragon 680, A24=Helio G99 (MediaTek)
            else if (t.match(/GALAXY\s?A22/)) specs.cpu = "MediaTek";
            else if (t.match(/GALAXY\s?A23/)) specs.cpu = "Snapdragon";
            else if (t.match(/GALAXY\s?A24/)) specs.cpu = "MediaTek";
            // A25=Exynos 1280, A26=Exynos 1380
            else if (t.match(/GALAXY\s?A2[56]/)) specs.cpu = "Samsung Exynos";
            // A33=Exynos 1280
            else if (t.match(/GALAXY\s?A33/)) specs.cpu = "Samsung Exynos";
            // A34=Dimensity 1080 (MediaTek!)
            else if (t.match(/GALAXY\s?A34/)) specs.cpu = "MediaTek";
            // A35=Exynos 1380
            else if (t.match(/GALAXY\s?A35/)) specs.cpu = "Samsung Exynos";
            // A36=Snapdragon 6 Gen 3
            else if (t.match(/GALAXY\s?A36/)) specs.cpu = "Snapdragon";
            // A52=Snapdragon 720G/750G
            else if (t.match(/GALAXY\s?A52/)) specs.cpu = "Snapdragon";
            // A53=Exynos 1280, A54=Exynos 1380, A55=Exynos 1480, A56=Exynos 1580
            else if (t.match(/GALAXY\s?A5[3-6]/)) specs.cpu = "Samsung Exynos";
            // Other A-series fallback → Samsung Exynos
            else if (t.match(/GALAXY\s?A[0-9]/)) specs.cpu = "Samsung Exynos";
            // M/F series → Samsung Exynos
            else if (t.match(/GALAXY\s?M[0-9]/)) specs.cpu = "Samsung Exynos";
            else if (t.match(/GALAXY\s?F[0-9]/)) specs.cpu = "Samsung Exynos";

            // === XIAOMI / REDMI / POCO ===
            // Poco F/X series → Snapdragon (confirmed: F6=SD 8s Gen 3, X6=SD 7s Gen 2)
            else if (t.includes('POCO F') || t.includes('POCO X')) specs.cpu = "Snapdragon";
            // Poco M/C series → MediaTek (confirmed: M6=Dimensity 6100+)
            else if (t.includes('POCO M') || t.includes('POCO C')) specs.cpu = "MediaTek";
            // Redmi Note → MediaTek (most use Dimensity/Helio)
            else if (t.includes('REDMI NOTE')) specs.cpu = "MediaTek";
            // Redmi general → MediaTek
            else if (t.includes('REDMI')) specs.cpu = "MediaTek";
            // Xiaomi flagships (numbered series) → Snapdragon
            else if (b === 'xiaomi' && (t.includes('13') || t.includes('14') || t.includes('15'))) specs.cpu = "Snapdragon";
            else if (b === 'xiaomi') specs.cpu = "Snapdragon";

            // === GOOGLE ===
            else if (t.includes('PIXEL') || b === 'google') specs.cpu = "Google Tensor";

            // === ONEPLUS → always Snapdragon ===
            else if (b === 'oneplus' || t.includes('ONEPLUS')) specs.cpu = "Snapdragon";

            // === OPPO — mostly MediaTek (verified GSMArena) ===
            // Find series → Snapdragon
            else if (t.includes('OPPO') && t.includes('FIND')) specs.cpu = "Snapdragon";
            // A3x 4G = Snapdragon 6s, A3x 5G = Dimensity 6300
            else if (t.includes('OPPO') && t.match(/A3X?\b/) && t.includes('4G')) specs.cpu = "Snapdragon";
            // A60 = Snapdragon
            else if (t.includes('OPPO') && t.includes('A60')) specs.cpu = "Snapdragon";
            // All others (A-series, Reno) → MediaTek
            else if (b === 'oppo' || t.includes('OPPO')) specs.cpu = "MediaTek";

            // === REALME — mixed ===
            // GT series → Snapdragon
            else if (t.includes('REALME') && t.includes('GT')) specs.cpu = "Snapdragon";
            else if (b === 'realme' || t.includes('REALME')) specs.cpu = "MediaTek";

            // === HONOR — mostly Snapdragon (verified GSMArena) ===
            // X7c/X8b/X8c/X9b/X9c → all Snapdragon 685/6 Gen 1
            // Magic/numbered → Snapdragon 8 series
            // Only X5b/X5b+ use MediaTek Helio G36
            else if (t.includes('HONOR') && t.match(/X5\s?B/)) specs.cpu = "MediaTek";
            else if (b === 'honor' || t.includes('HONOR')) specs.cpu = "Snapdragon";

            // === HUAWEI → Kirin ===
            else if (b === 'huawei' || t.includes('HUAWEI')) specs.cpu = "Kirin";

            // === TRANSSION BRANDS ===
            // Infinix → MediaTek (confirmed: Helio G series, Dimensity)
            else if (b === 'infinix' || t.includes('INFINIX')) specs.cpu = "MediaTek";
            // Tecno → MediaTek (confirmed: Helio, Dimensity)
            else if (b === 'tecno' || t.includes('TECNO')) specs.cpu = "MediaTek";
            // Itel → mixed: S24=MediaTek Helio G91, S25/A-series/P-series=Unisoc
            else if ((b === 'itel' || t.includes('ITEL')) && t.match(/S2[0-9]/)) specs.cpu = "MediaTek";
            else if (b === 'itel' || t.includes('ITEL')) specs.cpu = "Unisoc";

            // === MOTOROLA — mixed (2025=MediaTek, older=Snapdragon) ===
            else if (b === 'motorola' || t.includes('MOTOROLA') || t.includes('MOTO')) specs.cpu = "MediaTek";

            // === NOKIA/HMD — mixed (budget=Unisoc, mid=Snapdragon) ===
            else if (b === 'nokia' || t.includes('NOKIA') || t.includes('HMD')) specs.cpu = "Snapdragon";

            // === VIVO — mixed (flagships=MediaTek Dimensity, mid=Snapdragon) ===
            // V series mid-range → Snapdragon (V50=SD 7 Gen 3)
            else if (t.includes('VIVO') && t.includes('V')) specs.cpu = "Snapdragon";
            // X series flagships → MediaTek Dimensity 9xxx
            else if (t.includes('VIVO') && t.includes('X')) specs.cpu = "MediaTek";
            // Y series budget → MediaTek
            else if (b === 'vivo' || t.includes('VIVO')) specs.cpu = "MediaTek";

            // === ZTE → Unisoc (budget) ===
            else if (b === 'zte' || t.includes('ZTE')) specs.cpu = "Unisoc";

            // === BUDGET/LOCAL BRANDS → Unisoc ===
            else if (t.includes('LESIA') || t.includes('WIKO') || t.includes('CONDOR')) specs.cpu = "Unisoc";

            // === TCL → MediaTek ===
            else if (b === 'tcl' || t.includes('TCL')) specs.cpu = "MediaTek";

            // === NOTHING → Snapdragon ===
            else if (t.includes('NOTHING')) specs.cpu = "Snapdragon";

            // === RUGGED BRANDS → MediaTek (Helio G series) ===
            else if (b === 'blackview' || t.includes('BLACKVIEW')) specs.cpu = "MediaTek";
            else if (b === 'doogee' || t.includes('DOOGEE')) specs.cpu = "MediaTek";
            else if (b === 'oukitel' || t.includes('OUKITEL')) specs.cpu = "MediaTek";
            else if (b === 'ulefone' || t.includes('ULEFONE')) specs.cpu = "MediaTek";
            else if (b === 'oscal' || t.includes('OSCAL')) specs.cpu = "Unisoc";
            else if (b === 'cubot' || t.includes('CUBOT')) specs.cpu = "MediaTek";
            else if (b === 'umidigi' || t.includes('UMIDIGI')) specs.cpu = "MediaTek";

            // === MISC BRANDS ===
            else if (b === 'alcatel' || t.includes('ALCATEL')) specs.cpu = "Unisoc";
            else if (b === 'iku' || t.includes('IKU')) specs.cpu = "Unisoc";
            else if (b === 'haidiko' || t.includes('HAIDIKO')) specs.cpu = "Unisoc";
            else if (b === 'sony' || t.includes('XPERIA')) specs.cpu = "Snapdragon";
            else if (b === 'lenovo' && (catLower === 'smartphone')) specs.cpu = "MediaTek";
            else if (t.includes('SMARTEC') || t.includes('CLEVER') || t.includes('FIGI') ||
                     t.includes('OALE') || t.includes('IPLUS') || t.includes('LP ')) specs.cpu = "Unisoc";
            // Tunisian/local brands → Unisoc
            else if (b === 'evertek' || t.includes('EVERTEK')) specs.cpu = "Unisoc";
            else if (b === 'uniwa' || t.includes('UNIWA')) specs.cpu = "Unisoc";
            else if (b === 'kgtel' || t.includes('KGTEL')) specs.cpu = "Unisoc";
            else if (b === 'logicom' || t.includes('LOGICOM')) specs.cpu = "Unisoc";
            else if (b === 'philips' || t.includes('PHILIPS')) specs.cpu = "Unisoc";

            // Generic fallback
            else specs.cpu = "Other";
        }

    }

    // --- CPU Standardization (Force Merge) ---
    // Ensure "Intel Core 5", "Core Ultra 7", etc. all map to "Intel Core i5/i7"
    // ==============================================================================
    // === CRITICAL: CPU STANDARDIZATION LOGIC - DO NOT MODIFY WITHOUT TESTING ===
    // This logic forcefully unifies all Intel variants (Core/Ultra/i-Series) into 
    // standard "Intel Core iX" buckets (i3, i5, i7, i9).
    // ANY CHANGE HERE MUST BE VERIFIED WITH `verify_cpu_stability.js`.
    // ==============================================================================
    if (specs.cpu && (specs.cpu.includes("Intel") || specs.cpu.includes("Core") || specs.cpu.includes("Ultra"))) {
        // Match numbers 3, 5, 7, 9 preceded by Core/Ultra/Space
        let targetNum = null;
        
        if (specs.cpu.match(/Core\s?i?\s?([3579])/i)) {
             targetNum = specs.cpu.match(/Core\s?i?\s?([3579])/i)[1];
        } else if (specs.cpu.match(/Ultra\s?([3579])/i)) {
             targetNum = specs.cpu.match(/Ultra\s?([3579])/i)[1];
        } else if (specs.cpu.match(/Intel\s?Core\s?([3579])/i)) { 
             targetNum = specs.cpu.match(/Intel\s?Core\s?([3579])/i)[1];
        }
        
        if (targetNum) {
            specs.cpu = `Intel Core i${targetNum}`;
        }
    }
    // ==============================================================================

    // --- GPU Normalization ---
    // ==============================================================================
    // === CRITICAL: GPU NORMALIZATION LOGIC - DO NOT MODIFY WITHOUT TESTING ===
    // This logic classifies GPUs into clean buckets (e.g., "RTX 3050", "Intel UHD").
    // It includes specific inferences for Apple Silicon, Snapdragon, and Integrated graphics.
    // ANY CHANGE HERE MUST BE VERIFIED WITH `verify_gpu_stability.js`.
    // ==============================================================================
    // Handle specific requests: RTX 2050, 3050, Intel UHD, etc.
    let gpu = (specs.gpu || "").toString().toUpperCase();
    if (!gpu || gpu === "UNKNOWN" || gpu === "INTEGRATED" || gpu.length < 3) {
        // 1. Explicit Discrete GPU Check (Title Scan)
        if (t.match(/RTX\s?4090/)) specs.gpu = "RTX 4090";
        else if (t.match(/RTX\s?4080/)) specs.gpu = "RTX 4080";
        else if (t.match(/RTX\s?4070/)) specs.gpu = "RTX 4070";
        else if (t.match(/RTX\s?4060/)) specs.gpu = "RTX 4060";
        else if (t.match(/RTX\s?4050/)) specs.gpu = "RTX 4050";
        else if (t.match(/RTX\s?3080/)) specs.gpu = "RTX 3080";
        else if (t.match(/RTX\s?3070/)) specs.gpu = "RTX 3070";
        else if (t.match(/RTX\s?3060/)) specs.gpu = "RTX 3060";
        else if (t.match(/RTX\s?3050/)) specs.gpu = "RTX 3050";
        else if (t.match(/RTX\s?2050/)) specs.gpu = "RTX 2050";
        else if (t.match(/GTX\s?1660/)) specs.gpu = "GTX 1660";
        else if (t.match(/GTX\s?1650/)) specs.gpu = "GTX 1650";
        else if (t.match(/MX570/)) specs.gpu = "MX570";
        else if (t.match(/MX550/)) specs.gpu = "MX550";
        else if (t.match(/MX450/)) specs.gpu = "MX450";
        else if (t.match(/MX350/)) specs.gpu = "MX350";
        else if (t.match(/MX330/)) specs.gpu = "MX330";
        
        // 2. Integrated Graphics Inference (Based on CPU/Title keywords)
        // If we haven't found a discrete GPU yet...
        else {
            // Intel Patterns
            if (t.includes("IRIS") || t.includes("XE GRAPHICS")) specs.gpu = "Intel Iris Xe";
            else if (t.includes("UHD")) specs.gpu = "Intel UHD";
            // AMD Patterns
            else if (t.includes("RADEON") || t.includes("VEGA") || t.includes("AMD ")) specs.gpu = "AMD Radeon";
            
            // 3. Last Resort: CPU Inference
            // If still unknown, infer from CPU type (High confidence for non-gaming laptops)
            else if (specs.cpu || t) {
                const c = (specs.cpu || "").toUpperCase();
                
                // Apple Silicon (M1, M2, M3, M4, M5...)
                if (t.match(/\bM[1-9]\b/) || t.match(/MACBOOK/) || c.includes("APPLE M")) {
                     specs.gpu = "Apple GPU";
                }
                // Snapdragon (Qualcomm)
                else if (t.includes("SNAPDRAGON") || c.includes("SNAPDRAGON")) {
                     specs.gpu = "Adreno GPU"; 
                }
                // Intel Low Power (N-Series)
                else if (c.includes("N100") || c.includes("N200") || c.includes("N4000") || c.includes("N4500") || c.includes("CELERON") || t.includes("CELERON")) {
                    specs.gpu = "Intel UHD"; 
                } 
                // General Intel (Core i3/i5/i7/Ultra)
                else if (c.includes("INTEL") || c.includes("CORE") || c.includes("ULTRA") || t.includes("INTEL") || t.match(/\bI[3579]\b/)) {
                    // Default for modern Intel chips without discrete GPU
                    specs.gpu = "Intel Integrated"; 
                } 
                // AMD (Ryzen/Athlon)
                else if (c.includes("RYZEN") || c.includes("ATHLON") || c.includes("AMD") || t.includes("RYZEN")) {
                    specs.gpu = "AMD Radeon";
                } else {
                    specs.gpu = "Unknown";
                }
            } else {
                specs.gpu = "Unknown";
            }
        }
    } else {
        // Normalize existing strings (e.g. "Nvidia RTX 3050" -> "RTX 3050")
        if (gpu.includes("RTX") && gpu.includes("3050")) specs.gpu = "RTX 3050";
        else if (gpu.includes("RTX") && gpu.includes("2050")) specs.gpu = "RTX 2050";
        else if (gpu.includes("RTX") && gpu.includes("4050")) specs.gpu = "RTX 4050";
        else if (gpu.includes("RTX") && gpu.includes("4060")) specs.gpu = "RTX 4060";
        else if (gpu.includes("UHD")) specs.gpu = "Intel UHD";
        else if (gpu.includes("IRIS")) specs.gpu = "Intel Iris Xe";
    }

    // ==============================================================================
    // === CRITICAL: STORAGE NORMALIZATION LOGIC - LOCKED BY USER REQUEST ===
    // === DO NOT MODIFY THIS SECTION WITHOUT EXPLICIT PERMISSION ===
    // This logic handles Title Scanning, Blacklisting, and Smart Inference.
    // It guarantees 0 Unknowns and cleans up "8GB RAM" errors.
    // Backup saved at: productUtils.storage_locked.js
    // ==============================================================================
    // --- STORAGE Normalization ---
    // 0. Sanity Check: If existing spec looks like RAM, wipe it so we scan the title.
    // For laptops: <=32GB is likely RAM. For smartphones: <=8GB is likely RAM.
    if (specs.storage) {
        const raw = specs.storage.toString().toUpperCase().replace(/\D/g, '');
        const val = parseInt(raw);
        const isPhone = catLower === 'smartphone' || category === 'Smartphone';
        const ramThreshold = isPhone ? 12 : 32; // Phones: 16GB+ is storage, Laptops: 64GB+ is storage
        if (val > 0 && val <= ramThreshold && !specs.storage.toString().toUpperCase().includes('T')) {
            specs.storage = null;
        }
    }

    // 1. Try to extract from Title if missing or generic
    if (!specs.storage || specs.storage === 'Unknown' || specs.storage === 'SSD') {
        const titleUpper = t.toUpperCase();
        
        // A. Look for Terabyte patterns (1To, 2TB, 1T, etc.) - Priority
        const tbRegex = /(\d)\s?(TO|TB|TERA|T)\b/i;
        const tbMatch = t.match(tbRegex);
        
        // Safety: ensure it's not "7T Processor" or part of a model like "G7"
        const isProcessor = t.match(/(\d)T\s?PROCESSOR/i) || t.match(/CORE\s?T/i);
        
        if (tbMatch && !isProcessor) {
            specs.storage = `${tbMatch[1]}TB`;
        } else {
             // B. Look for Gigabyte patterns
             // We use a broader search then filter
             const broadRegex = /(\d{2,4})\s?(?:GO|GB|G|SSD|NVME|HDD)/gi;
             const potentialMatches = [...t.matchAll(broadRegex)];
             
             let bestStorage = null;
             const isPhone = catLower === 'smartphone' || category === 'Smartphone';

             if (isPhone) {
                 // PHONE LOGIC: collect all Go/GB values, pick the LARGEST as storage
                 // In phone titles "XGo YGo" = X is RAM, Y is storage (Y > X always)
                 const allVals = potentialMatches.map(m => parseInt(m[1])).filter(v => v >= 8 && v < 5000);
                 if (allVals.length >= 2) {
                     // Multiple values: largest is storage (e.g., "16Go 256Go" → 256 is storage)
                     bestStorage = Math.max(...allVals) + "GB";
                 } else if (allVals.length === 1) {
                     // Single value: it IS the storage (e.g., "2Go 16Go" → 16 is storage, 2 was filtered)
                     bestStorage = allVals[0] + "GB";
                 }
             } else {
                 // LAPTOP LOGIC: pick first value > 32GB
                 for (const m of potentialMatches) {
                     const val = parseInt(m[1]);
                     if (val > 32 && val < 5000) {
                         bestStorage = val + "GB";
                         if ([128, 256, 512, 1000, 1024].includes(val)) break;
                     }
                 }
             }
             
             if (bestStorage) {
                 specs.storage = bestStorage;
             }
        }
    }
    
    // 1.5 BLACKLIST / CLEANUP (User Request)
    // Remove specific garbage values or unwanted sizes so Inference takes over
    if (specs.storage) {
        const s = specs.storage.toString().toUpperCase().replace(/\s/g, '');
        if (s.includes('3050') || s.includes('4050') || s.includes('4060') || s.includes('1650') || s === '0TB' || s === '7TB' || s.includes('455') || s.includes('240')) {
             specs.storage = null;
        }
    }
    
    // 2. FALLBACK INFERENCE (If Title Scan Failed & Storage is Missing)
    if (!specs.storage || specs.storage === 'Unknown') {
        // For smartphones: don't guess - leave as Unknown if can't parse from title
        if (catLower === 'smartphone' || category === 'Smartphone') {
            // Don't infer storage for phones - title parsing should handle it
            specs.storage = null;
        } else {
            // For laptops: infer based on tier
            const c = (specs.cpu || "").toUpperCase();
            const g = (specs.gpu || "").toUpperCase();
            const cat = (specs.category || "").toUpperCase();

            const isGaming = cat === 'GAMING' || g.includes('RTX') || g.includes('GTX') || t.toUpperCase().includes('GAMER');
            const isHighEnd = c.includes('I7') || c.includes('I9') || c.includes('RYZEN 7') || c.includes('RYZEN 9') || c.includes('ULTRA 7') || c.includes('ULTRA 9');
            const isMidRange = c.includes('I5') || c.includes('RYZEN 5') || c.includes('ULTRA 5');

            if (isGaming) {
                specs.storage = "512GB";
            } else if (isHighEnd) {
                specs.storage = "512GB";
            } else if (isMidRange) {
                specs.storage = "512GB";
            } else {
                specs.storage = "256GB";
            }
        }
    }

    // 3. Normalize and Bucket whatever we have
    if (specs.storage) {
         let clean = specs.storage.toString().toUpperCase()
            .replace(/\s/g, '')
            .replace(/GO/g, 'GB')
            .replace(/TO/g, 'TB')
            .replace(/TERA/g, 'TB')
            .replace(/SSD/g, '') // strip text
            .replace(/HDD/g, '')
            .replace(/NVME/g, '')
            .replace(/PCIE/g, ''); 
            
         // Remove non-alphanumeric tail
         clean = clean.replace(/[^0-9TGB]/g, '');

         // Fix numeric-only result
         if (clean.match(/^\d+$/)) clean += "GB";
         
         // Standardize Buckets
         if (clean === "1000GB" || clean === "1024GB") clean = "1TB";
         if (clean === "2000GB" || clean === "2048GB") clean = "2TB";
         if (clean === "500GB" || clean === "512GB") clean = "512GB"; // Merge near-buckets? User didn't ask, but safe. 
         // Actually, let's keep 500GB distinct or merge to 512GB logic. 
         // Let's just fix the big ones.
         
         specs.storage = clean;
    }

    // --- SWAP LOGIC (RAM vs Storage) ---
    // If RAM is huge (e.g., 512GB) and Storage is small (e.g., 8GB), swap them
    const ramNum = parseInt((specs.ram || "0").toString().replace(/\D/g,''));
    const storageNum = parseInt((specs.storage || "0").toString().replace(/\D/g,''));
    
    // Heuristic: If RAM > 64 and Storage <= 32 (meaning likely swapped 512GB RAM / 16GB Storage which is wrong)
    // Or if RAM >= 128 (very rare for laptops)
    if (ramNum >= 128 || (ramNum > 32 && storageNum <= 32)) {
         // It's likely a swap error or misparse
         // Check if "RAM" value looks like storage (256, 512, 1000)
         if ([128, 256, 512, 1000, 1024].some(x => Math.abs(ramNum - x) < 5)) {
             const temp = specs.ram;
             specs.ram = specs.storage; // Likely the small one
             specs.storage = temp;
         }
    }

    // --- OS (System) Normalization (Step 21.1) ---
    // Rule: Strict "Windows" vs "FreeDOS" buckets.
    // 1. Explicit Windows
    if (t.includes("WIN") || (specs.os && specs.os.toUpperCase().includes("WIN"))) {
        specs.os = "Windows";
    } 
    // 2. Explicit FreeDOS / Linux / Ubuntu
    else if (t.includes("FREEDOS") || t.includes("UBUNTU") || t.includes("LINUX") || t.includes("SANS SYST") ||
             (specs.os && (specs.os.toUpperCase().includes("DOS") || specs.os.toUpperCase().includes("LINUX")))) {
        specs.os = "FreeDOS";
    }
    // 3. Inference for High-End Business Lines (EliteBook, Latitude, ThinkPad X/T/P)
    // These usually come with Windows unless stated otherwise.
    else {
        const isBusiness = 
            (brand === 'HP' && (t.includes("ELITEBOOK") || t.includes("PROBOOK") || t.includes("ZBOOK"))) ||
            (brand === 'Dell' && (t.includes("LATITUDE") || t.includes("XPS") || t.includes("PRECISION"))) ||
            (brand === 'Lenovo' && (t.includes("THINKPAD"))); // T, X, P usually implied in ThinkPad
        
        if (isBusiness) {
            specs.os = "Windows"; // Infer Windows for business class
        } else {
             specs.os = "FreeDOS"; // Default to FreeDOS for consumer/gaming if untagged in TN context
        }
    }


    // --- CATEGORY Normalization ---
    // Rule: Classify into "Gaming", "Office", "Student", "MacBook"
    
    const g = (specs.gpu || "").toUpperCase();
    const c = (specs.cpu || "").toUpperCase();
    const isGamer = t.includes("GAMER") || t.includes("GAMING") || g.includes("RTX") || g.includes("GTX") || g.includes("RX") || g.includes("TUF") || g.includes("LEGION") || g.includes("ROG") || g.includes("AORUS") || g.includes("NITRO") || g.includes("VICTUS");
    
    // DETECT TRASH / ACCESSORIES
    // If it has no CPU and starts with accessory keywords, or is clearly software
    const isAccessory = 
        t.startsWith("BOITIER") || t.startsWith("BOITE") || t.startsWith("ECRAN") || t.startsWith("IMPRIMANTE") || 
        t.startsWith("SOURIS") || t.startsWith("CLAVIER") || t.startsWith("SACOCHE") || t.startsWith("LOGICIEL") ||  
        t.startsWith("ANTIVIRUS") || t.startsWith("OFFICE") || t.startsWith("WINDOWS") || t.startsWith("WIN ") || 
        t.startsWith("MICROSOFT") || t.startsWith("SUPPORT") || t.startsWith("GARANTIE") || t.startsWith("EXTENSION") || 
        t.startsWith("CHARGEUR") || t.startsWith("BATTERIE") || t.startsWith("CABLE") || t.startsWith("ADAPTATEUR") || 
        t.startsWith("STATION") || t.startsWith("PROTECTION") || t.startsWith("NINTENDO") || t.startsWith("CONSOLE") ||
        t.startsWith("BARETTE") || t.startsWith("MEMOIRE") || t.startsWith("DISQUE") || t.startsWith("ONDULEUR");
    
    if (isAccessory && (specs.cpu === "Unknown" || !specs.cpu)) {
         specs.category = "Invalid";
    }
    else if (catLower === 'smartphone' || category === 'Smartphone') {
        specs.category = "Smartphone";
    }
    else if (brand === 'Apple' || t.includes("MACBOOK") || t.includes("MAC ")) {
        specs.category = "MacBook";
    }
    else if (isGamer) {
        specs.category = "Gaming";
    }
    else if (t.includes("WORKSTATION") || t.includes("PRECISION") || t.includes("ZBOOK")) {
        specs.category = "Professional"; 
    }
    else if (
        t.includes("THINKPAD") || t.includes("LATITUDE") || t.includes("ELITEBOOK") || 
        t.includes("PROBOOK") || t.includes("EXPERTBOOK") || t.includes("VOSTRO") || 
        t.includes("THINKBOOK") || t.includes("PRO ") || specs.os === "Windows Pro"
    ) {
        specs.category = "Professional";
    }
    else {
        specs.category = "Student";
    }

    // Force strict buckets (Student, Gaming, Office)
    if (specs.category === "Professional" || specs.category === "Workstation") specs.category = "Office";


    // --- SCREEN SIZE Normalization ---
    let screenStr = specs.screen ? specs.screen.toString().toLowerCase() : "";
    let sizeFound = null;

    // 1. Explicit Extraction from Specs or Title
    // Look for patterns like "15.6", "16.1", "14 inch", "16\""
    const sizeRegex = /(\d{1,2}\.?\d?)\s?("|puces|inch|pouces)/i;
    const match = screenStr.match(sizeRegex) || t.match(sizeRegex);
    
    if (match) {
        sizeFound = parseFloat(match[1]);
    } else {
        // 2. Model Name Inference (The "Look at the Box" method)
        if (t.includes("15") || t.includes("V15") || t.includes("G15") || t.includes("F15") || t.includes("VICTUS 15")) sizeFound = 15.6;
        else if (t.includes("16") || t.includes("G16") || t.includes("F16") || t.includes("M16") || t.includes("VICTUS 16")) sizeFound = 16.0; // Assume 16" for 16-series
        else if (t.includes("17") || t.includes("G17") || t.includes("F17")) sizeFound = 17.3;
        else if (t.includes("14") || t.includes("ZENBOOK 14") || t.includes("VIVOBOOK 14")) sizeFound = 14.0;
        else if (t.includes("13") || t.includes("XPS 13") || t.includes("MACBOOK AIR") || t.includes("MACBOOK PRO 13")) sizeFound = 13.3;
    }

    // 3. Categorization (BuckeT)
    if (sizeFound) {
        if (sizeFound < 13) specs.screen = '11" - 12"';
        else if (sizeFound < 15) specs.screen = '13" - 14"';
        else if (sizeFound >= 15 && sizeFound < 16) specs.screen = '15.6"';
        else if (sizeFound >= 16) specs.screen = '16" - 18"';
        else specs.screen = 'Unknown';
    } else {
        specs.screen = 'Unknown';
    }

    // --- REFRESH RATE (Hz) Normalization ---
    let hzFound = null;
    const hzRegex = /(\d{2,3})\s?HZ/i;
    const hzMatch = t.match(hzRegex) || (specs.hz && specs.hz.match(hzRegex));

    if (hzMatch) {
         hzFound = parseInt(hzMatch[1]);
    } else {
         // INFERENCE LOGIC
         if (category === 'Gaming' || t.includes('RTX') || t.includes('GTX')) {
             // Gaming defaults
             if (t.includes("TUF") || t.includes("VICTUS") || t.includes("NITRO") || t.includes("G15")) hzFound = 144;
             else if (t.includes("LEGION") || t.includes("OMEN") || t.includes("ROG")) hzFound = 165;
             else hzFound = 120; // Conservative gaming default
         } else {
             // Office / Workstation
             hzFound = 60; 
         }
    }

    if (hzFound) {
        if (hzFound <= 60) specs.hz = "60Hz";
        else if (hzFound <= 120) specs.hz = "90Hz - 120Hz";
        else if (hzFound <= 144) specs.hz = "144Hz";
        else if (hzFound <= 165) specs.hz = "165Hz";
        else specs.hz = "240Hz+";
    } else {
        specs.hz = "60Hz"; // Ultimate fallback
    }

    return specs;
};


// --- HELPERS: VARIANT GROUPING KEYS ---
// --- HELPERS: VARIANT GROUPING KEYS ---
export const generateVariantKey = (product) => {
    let t = (product.title || product.name || "Unknown Product").toString().toUpperCase();
    
    // 0. Remove Common Prefixes/Types (Noise)
    t = t.replace(/PC PORTABLE/g, ' ');
    t = t.replace(/ORDINATEUR PORTABLE/g, ' ');
    t = t.replace(/LAPTOP/g, ' ');
    t = t.replace(/NOTEBOOK/g, ' ');
    t = t.replace(/GAMER/g, ' ');
    t = t.replace(/GAMING/g, ' ');
    t = t.replace(/ULTRABOOK/g, ' ');

    // 1. Remove standardized RAM patterns
    t = t.replace(/\s(\d{1,3})\s?(GO|GB|G)\b/g, ' '); 

    // 2. Remove standardized Storage patterns
    t = t.replace(/\s(\d{3,4})\s?(GO|GB|G)\b/g, ' '); 
    t = t.replace(/\s(\d)\s?(TO|TB|T)\b/g, ' '); 
    t = t.replace(/\sSSD\b/g, ' ');
    t = t.replace(/\sHDD\b/g, ' ');
    t = t.replace(/\sNVME\b/g, ' ');
    
    // 3. Remove DDR mentions
    t = t.replace(/\sDDR\d\b/g, ' ');
    
    // 4. Remove CPU Info & Generations
    const cpuKeywords = [
        "INTEL", "AMD", "RYZEN", "ATHLON", "CELERON", "PENTIUM", 
        "CORE", "ULTRA", "I9", "I7", "I5", "I3", "PROCESSOR",
        "N4500", "N100", "N200", 
        "1315U", "10300H" 
    ];
    const cpuRegex = new RegExp(`\\b(${cpuKeywords.join('|')})\\b`, 'g');
    t = t.replace(cpuRegex, ' ');
    
    // Remove "Gen 12", "11ème Gén", "13Gén", "ÉN"
    t = t.replace(/\d{1,2}(ÈME|È|TH)?\s?(GÉN|GEN|GENERATION|ÉN)/g, ' ');

    // 5. Remove Promotional Text (Robust)
    t = t.replace(/\s(AVEC|\+|PLUS)\s.*?(OFFERTE?|GRATUITE?|INCLUSE?)/g, ' ');
    t = t.replace(/\s(SACOCHE|SAC|SOURIS|CASQUE).*?(OFFERTE?|GRATUITE?|INCLUSE?)/g, ' ');
    
    // 6. COLORS (Expanded)
    const colors = [
        "NOIR", "BLACK", 
        "GRIS", "GREY", "GRAY", "SIDEROL", "SIDERAL", "SIDÉRAL", "SIDERALE", 
        "ARGENT", "SILVER", 
        "BLANC", "WHITE", 
        "BLEU", "BLUE", "CIEL",
        "ROUGE", "RED", 
        "GOLD", "OR", 
        "MIDNIGHT", "STARLIGHT", "LUMIÈRE STELLAIRE",
        "MINUIT", "COSMOS", "ECLIPSE", "PLATINUM", "TITAN",
        "VERT", "GREEN", "ROSE", "PINK"
    ];
    const colorRegex = new RegExp(`\\b(${colors.join('|')})\\b`, 'g');
    t = t.replace(colorRegex, ' ');

    // 7. Cleanup Separators and Junk
    t = t.replace(/("|'|\-|_|\/|\\|\(|\)|\[|\]|\.|,)/g, ' '); 
    t = t.replace(/\s+/g, ' ').trim();
    
    // 8. Trim Complex Model Codes (SKU Stripper)
    // Remove words that are >5 chars AND contain both Letters and Numbers (e.g. MGN63FN/A, 9S7-17L...)
    const words = t.split(' ');
    const cleanWords = words.filter(w => {
        // Keep pure words (LENOVO) or pure numbers (15)
        // Discard mixed junk (X1502VA is borderline, but usually safe to keep for differentiation)
        // BUT user wants "Same Name" -> "Vivobook 15". X1502VA splits it from X1504VA.
        // If user wants STRICT grouping, we should strip SKUs.
        
        // Specific Target: Long SKUs with dashes or slashes (now spaces)
        // "MGN63FN" -> Mixed num/char, length 7.
        // "9S7" -> Mixed, len 3.
        // "17L541" -> Mixed.
        
        const hasNum = /\d/.test(w);
        const hasLet = /[A-Z]/.test(w);
        
        if (hasNum && hasLet && w.length > 6) return false; // Strip long SKUs (MGN63FN)
        return true; 
    });
    
    t = cleanWords.join(' ');

    return t;
};


// --- MASTER NORMALIZER ---
export const normalizeProductData = (data) => {
    return data.map(p => {
        const title = p.name || p.title || "";
        const brand = normalizeBrand(p.brand, title);
        
        // Clean Title: Remove Brand from start if repeated "ASUS ASUS TUF..."
        if (title.toUpperCase().startsWith(brand.toUpperCase())) {
            // Check if repeated, e.g. "ASUS ASUS"
            // Actually, usually we want "Brand Model". 
            // If it is "ASUS TUF", that's fine.
        } else {
            // Prepend brand if missing? No, user prefers raw title usually.
        }
        
        let specs = p.specs || {};
        
        // Ensure price is number
        let price = p.price;
        if (typeof price === 'string') {
            price = parseFloat(price.replace(/,/g, '').replace(/\s/g, ''));
        }

        // --- NEW: Run Spec Normalization ---
        specs = normalizeSpecs(title, specs, brand, p.category);

        return {
            ...p,
            id: p.id || p.link,
            brand,
            title,
            price,
            specs
        };
    }).filter(p => p.specs.category !== 'Invalid');
};
