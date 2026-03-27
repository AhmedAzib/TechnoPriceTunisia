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
    if (has('mytek')) return 'MyTek'; // For assembled PCs starting with "Pc de Bureau MyTek"
    if (has('kimera')) return 'Kimera';
    
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
    
    // --- RAM Normalization ---
    // ==============================================================================
    // === CRITICAL: RAM NORMALIZATION LOGIC - DO NOT MODIFY WITHOUT TESTING ===
    // This logic standardizes RAM to "XGB" format and handles both integer (4) 
    // and string ("4GB") inputs. It also cleans "GO" -> "GB".
    // ANY CHANGE HERE MUST BE VERIFIED WITH `verify_ram_stability.js`.
    // ==============================================================================
    // Extract from title if missing
    if (!specs.ram || specs.ram === 'Unknown') {
        const ramMatch = t.match(/(\d{1,3})\s?(GO|GB|G)\b/i);
        if (ramMatch) specs.ram = `${ramMatch[1]}GB`;
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

    // --- STORAGE Normalization ---
    // 0. Sanity Check: If existing spec looks like RAM (<= 32GB), wipe it so we scan the title.
    if (specs.storage) {
        const raw = specs.storage.toString().toUpperCase().replace(/\D/g, '');
        const val = parseInt(raw);
        // If it's small (<= 32) and not clearly TB, it's probably RAM (4, 8, 16, 32)
        // Note: 32GB eMMC exists but is rare/cheap. Most 32GB is RAM in this context.
        if (val > 0 && val <= 32 && !specs.storage.toString().toUpperCase().includes('T')) {
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
             
             for (const m of potentialMatches) {
                 const val = parseInt(m[1]); // The number
                 
                 // Heuristic:
                 // 64, 120, 128, 250, 256, 480, 500, 512, 1000, 2000 are valid storage.
                 // We ignore anything <= 32 during Scan too.
                 
                 if (val > 32 && val < 5000) {
                     bestStorage = val + "GB";
                     // Prefer standard sizes if found
                     if ([128, 256, 512, 1000, 1024].includes(val)) {
                         break; // Found a winner
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
    // The user explicitly requested "0 Unknowns" and provided a % distribution plan.
    // If we simply cannot find the storage, we infer it based on the machine's tier.
    if (!specs.storage || specs.storage === 'Unknown') {
        const c = (specs.cpu || "").toUpperCase();
        const g = (specs.gpu || "").toUpperCase();
        const cat = (specs.category || "").toUpperCase();
        
        const isGaming = cat === 'GAMING' || g.includes('RTX') || g.includes('GTX') || t.toUpperCase().includes('GAMER');
        const isHighEnd = c.includes('I7') || c.includes('I9') || c.includes('RYZEN 7') || c.includes('RYZEN 9') || c.includes('ULTRA 7') || c.includes('ULTRA 9');
        const isMidRange = c.includes('I5') || c.includes('RYZEN 5') || c.includes('ULTRA 5');
        
        if (isGaming) {
            specs.storage = "512GB"; // Standard for modern gaming laptops
        } else if (isHighEnd) {
            specs.storage = "512GB"; // High end usually starts at 512GB or 1TB
        } else if (isMidRange) {
            specs.storage = "512GB"; // Modern i5s are mostly 512GB
        } else {
            specs.storage = "256GB"; // Budget/Entry level fallback (i3, Celeron)
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
export const generateVariantKey = (product) => {
    let t = (product.title || product.name || "Unknown Product").toString().toUpperCase();
    
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
    
    // 4. Remove Promotional Text (Robust)
    t = t.replace(/\s(AVEC|\+|PLUS)\s.*?(OFFERTE?|GRATUITE?|INCLUSE?)/g, ' ');
    t = t.replace(/\s(SACOCHE|SAC|SOURIS|CASQUE).*?(OFFERTE?|GRATUITE?|INCLUSE?)/g, ' ');

    // 5. Cleanup
    t = t.replace(/\s+\//g, '/'); 
    t = t.replace(/\/\s+/g, '/');
    t = t.replace(/\s+/g, ' ').trim();
    
    // Strip trailing slash if any
    if (t.endsWith('/')) t = t.slice(0, -1).trim();

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
