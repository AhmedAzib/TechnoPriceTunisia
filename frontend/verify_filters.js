
import fs from 'fs';

// Mock Data Loading
const tunisianet = JSON.parse(fs.readFileSync('src/data/tunisianet_clean.json', 'utf8'));
const spacenet = JSON.parse(fs.readFileSync('src/data/spacenet_products.json', 'utf8'));
const mytek = JSON.parse(fs.readFileSync('src/data/mytek_test.json', 'utf8'));
const wiki = JSON.parse(fs.readFileSync('src/data/wiki_clean.json', 'utf8'));

// Combine Data
const allData = [...tunisianet, ...spacenet, ...mytek, ...wiki];

const sortSizes = (list) => {
    return list.sort((a, b) => {
        const getVal = (s) => {
            if (!s) return 0;
            const str = s.toString().toUpperCase();
            let multiplier = 1;
            if (str.includes('TB')) multiplier = 1024;
            const num = parseFloat(str.replace(/[^0-9.]/g, '')) || 0;
            return num * multiplier;
        };
        return getVal(a) - getVal(b);
    });
};

const normalizeProductData = (data) => {
  return data.map(product => {
    const p = { ...product, specs: { ...product.specs } };

    // 1. Brand
    if (p.brand) p.brand = p.brand.trim().toUpperCase();
    
    // Fix Unknown Brands (e.g. BMAX)
    if (!p.brand || p.brand === 'UNKNOWN') {
        const t = p.title.toUpperCase();
        if (t.includes('BMAX')) p.brand = 'BMAX';
        else if (t.includes('HP') || t.includes('ELITEBOOK')) p.brand = 'HP';
        else if (t.includes('DELL')) p.brand = 'DELL';
        else if (t.includes('LENOVO')) p.brand = 'LENOVO';
        else if (t.includes('ASUS')) p.brand = 'ASUS';
        else if (t.includes('ACER')) p.brand = 'ACER';
        else if (t.includes('MSI')) p.brand = 'MSI';
        else if (t.includes('APPLE') || t.includes('MACBOOK')) p.brand = 'APPLE';
        else if (t.includes('INFINIX')) p.brand = 'INFINIX';
        else if (t.includes('GIGABYTE')) p.brand = 'GIGABYTE';
        else if (t.includes('CHUWI')) p.brand = 'CHUWI';
    }

    // 2. Store (Source)
    if (p.source) p.source = p.source.trim().toLowerCase();

    // 3. RAM (Unified Filter)
    let r = (p.specs && p.specs.ram) ? p.specs.ram.toString().trim().toUpperCase() : "";
    
    // VALIDITY CHECK: If RAM is > 96GB (Storage) or NaN (Garbage), WIPE IT to force Title Scan.
    const rVal = parseInt(r.replace(/[^0-9]/g, ''));
    if (isNaN(rVal) || rVal > 96) {
        r = "";
    }
    
    // Deep Scan Title if RAM is missing or "Unknown" or invalid
    if (!r || r === 'UNKNOWN' || r === '') {
        // Hardcoded Maps for specific models known to have no RAM in title
        const modelRAMMap = {
            "MR942FN/A": "16", // MacBook Pro 15 2018
            "13-4150NF": "8",   // HP Spectre x360
            "13-AF000NK": "8",  // HP Spectre 13
            "IMAC ( APPLE64)": "8", 
            "MACBOOK PRO RETINA – 13 POUCES": "8", 
            "IMAC RETINA 5K – 27 POUCES": "8"     
        };
        
        for (const [key, val] of Object.entries(modelRAMMap)) {
            if (p.title.toUpperCase().includes(key)) {
                r = val + "GB";
                break;
            }
        }
        
        if (!r) {
            // Regex to find all "number + G/GB/GO" patterns
            const matches = [...p.title.toUpperCase().matchAll(/(\d+)\s*(GB|GO|G)(?![A-Z])/g)];
            let bestCandidate = null;
            for (const m of matches) {
                const val = parseInt(m[1]);
                if (val >= 2 && val <= 96) {
                    bestCandidate = val;
                    break; 
                }
            }
            if (bestCandidate) r = bestCandidate + "GB";
        }
    }

    if (r) {
        r = r.replace(/GO/g, 'GB').replace(/\s+/g, ''); // "8 GO" -> "8GB"
        r = r.replace(/(\d+)G$/, '$1GB'); // Handle "16G" at end -> "16GB"
        
        const match = r.match(/(\d+)GB/);
        if (match) p.specs.ram = match[1] + "GB"; 
        else if (r.match(/^\d+$/)) p.specs.ram = r + "GB";
    } else {
        p.specs.ram = "Unknown";
    }
    
    // Accessories detection - Set RAM to N/A ONLY for distinct non-computer components
    const tCheck = p.title.toUpperCase();
    // Removed: SAC, CHARGEUR, WIN PRO, WIN HOME, ECRAN (too risky)
    // Added: PROTECTION, SUITE, ANTIVIRUS, OFFICE, LICENCE (Software), VERSUS (Monitor)
    if (tCheck.includes("BOITIER") || tCheck.includes("ALIMENTATION") || tCheck.includes("BARETTE") || tCheck.includes("NINTENDO") || tCheck.includes("REFROIDISSEUR") || tCheck.includes("VENTILATEUR") || tCheck.includes("PROTECTION") || tCheck.includes("SUITE") || tCheck.includes("ANTIVIRUS") || tCheck.includes("OFFICE") || tCheck.includes("LICENCE") || tCheck.includes("DSP OEI") || tCheck.includes("ECOUTEUR") || tCheck.includes("VERSUS")) {
        p.specs.ram = "N/A";
    }
    
    // 4. CPU (Unified Processor Filter)
    const t = (p.title + " " + (p.specs.cpu || "")).toUpperCase();
    if (t.includes("CORE ULTRA 9") || t.includes("ULTRA 9") || t.includes("CORE 9") || t.includes("U9-")) p.specs.cpu = "Core Ultra 9";
    else if (t.includes("CORE ULTRA 7") || t.includes("ULTRA 7") || t.includes("U7-")) p.specs.cpu = "Core Ultra 7";
    else if (t.includes("CORE ULTRA 5") || t.includes("ULTRA 5") || t.includes("U5-")) p.specs.cpu = "Core Ultra 5";
    else if (t.includes("CORE 7") || t.match(/CORE 7 \d+/) || t.includes(" 150U") || t.includes("CORE U7") || t.includes("INTEL 7")) p.specs.cpu = "Core i7"; // Merged
    else if (t.includes("CORE 5") || t.match(/CORE 5 \d+/) || t.includes(" 120U") || t.includes("CORE U5") || t.includes("INTEL 5")) p.specs.cpu = "Core i5"; // Merged
    else if (t.includes("CORE 3") || t.match(/CORE 3 \d+/) || t.includes(" 100U") || t.includes("CORE U3") || t.includes("INTEL 3")) p.specs.cpu = "Core i3"; // Merged
    else if (t.includes("RYZEN AI 9") || t.includes("AI 9") || t.includes("RYZEN AI MAX") || t.includes("RYZEN AL MAX")) p.specs.cpu = "Ryzen AI 9";
    else if (t.includes("RYZEN AI 5")) p.specs.cpu = "Ryzen AI 5";
    else if (t.includes("RYZEN AI")) p.specs.cpu = "Ryzen AI";
    else if (t.includes("I9") || t.includes("RYZEN 9") || t.includes("R9-") || t.includes("RYZEN9") || t.includes("R9 ")) p.specs.cpu = (t.includes("RYZEN") || t.includes("R9") || t.includes("RAYZEN")) ? "Ryzen 9" : "Core i9";
    else if (t.includes("I7") || t.includes("RYZEN 7") || t.includes("R7-") || t.includes("RYZEN7") || t.includes("R7 ") || t.includes("R7_")) p.specs.cpu = (t.includes("RYZEN") || t.includes("R7") || t.includes("RAYZEN")) ? "Ryzen 7" : "Core i7";
    else if (t.includes("R5-7520U")) p.specs.cpu = "Ryzen 5"; 
    else if (t.includes("I5") || t.includes("RYZEN 5") || t.includes("R5-") || t.includes("RYZEN5") || t.includes("R5 ") || t.includes("R5_")) p.specs.cpu = (t.includes("RYZEN") || t.includes("R5") || t.includes("RAYZEN")) ? "Ryzen 5" : "Core i5";
    else if (t.includes("I3") || t.includes("RYZEN 3") || t.includes("R3-") || t.includes("RYZEN3") || t.includes("R-3") || t.includes("R3 ") || t.includes("RAYZEN 3")) p.specs.cpu = (t.includes("RYZEN") || t.includes("R3") || t.includes("R-3") || t.includes("RAYZEN")) ? "Ryzen 3" : "Core i3";
    else if (t.includes("CELERON") || t.includes("N4500") || t.includes("N4020") || t.includes("N5100") || t.includes("QUAD CORE") || t.includes("ATOM") || t.includes("CELERON") || t.includes("DUAL CORE") || t.includes("DUAL-CORE") || t.includes("N4120") || t.includes("EMMC")) p.specs.cpu = "Celeron";
    else if (t.includes("N100") || t.includes("N200") || t.includes("N150") || t.includes("N95") || t.includes("N50")) p.specs.cpu = "Intel N-Series";
    else if (t.includes("SNAPDRAGON")) p.specs.cpu = "Snapdragon"; // ARM
    else if (t.includes("M5")) p.specs.cpu = "Apple M5";
    else if (t.includes("M4")) p.specs.cpu = "Apple M4";
    else if (t.includes("M3")) p.specs.cpu = "Apple M3";
    else if (t.includes("M2")) p.specs.cpu = "Apple M2";
    else if (t.includes("M1")) p.specs.cpu = "Apple M1";
    else if (t.includes("ATHLON") || t.includes("3050U") || t.includes("3050E") || t.includes("3020E")) p.specs.cpu = "Athlon";
    else {
        // Fallback checks for known models without CPU in title
        if (t.includes("13-4150NF")) p.specs.cpu = "Core i7";
        else if (t.includes("RYZEN") || t.includes("RAYZEN")) p.specs.cpu = "Ryzen (Unknown)";
        else if (t.includes("INTEL")) p.specs.cpu = "Intel (Unknown)";
        else if (t.includes("AMD")) p.specs.cpu = "Athlon"; 
        else if (t.includes("XEON")) p.specs.cpu = "Xeon";
        
        // Accessories detection
        if (t.includes("BOITIER") || t.includes("ALIMENTATION") || t.includes("PROTECTION") || t.includes("BARETTE") || t.includes("WIN PRO") || t.includes("ECRAN") || t.includes("VERSUS 24") || t.includes("STATION DE CALCUL") || t.includes("NINTENDO")) p.specs.cpu = "N/A";
    }



    // 4. Screen Size Normalization
    let sc = (p.specs && p.specs.screen && p.specs.screen !== "Unknown") ? p.specs.screen.toString().trim() : "";
    // Note: t is already defined
    
    if (!sc) {
        // Hardcoded Map for common models known to face issues
        const map = {
            "MACBOOK AIR": "13.3",
            "MACBOOK PRO": "14.0", 
            "LATITUDE 3520": "15.6",
            "LATITUDE 3530": "15.6",
            "DELL 5500": "15.6",
            "DELL G15": "15.6",
            "GIGABYTE AORUS 15": "15.6",
            "GIGABYTE AORUS 16": "16.0",
            "GIGABYTE G6": "16.0",
            "GIGABYTE G5": "15.6",
            "MSI GAMING KATANA": "15.6",
            "MSI KATANA": "15.6",
            "MSI THIN 15": "15.6",
            "MSI CYBORG 15": "15.6",
            "MSI VECTOR GP68": "16.0",
            "MSI RAIDER GE68": "16.0",
            "ASUS TUF GAMING A15": "15.6",
            "ASUS TUF GAMING F15": "15.6",
            "ASUS TUF GAMING F17": "17.3",
            "ASUS TUF GAMING A14": "14.0",
            "ASUS TUF GAMING F16": "16.0",
            "ASUS ROG ZEPHYRUS G16": "16.0",
            "ASUS ROG ZEPHYRUS G14": "14.0",
            "ASUS V16": "16.0",
            "ASUS K16": "16.0",
            "ASUS FLOW Z13": "13.4",
            "VIVOBOOK 15": "15.6",
            "VIVOBOOK 16": "16.0",
            "VIVOBOOK 17": "17.3",
            "VICTUS 15": "15.6",
            "VICTUS 16": "16.1",
            "LOQ 15": "15.6",
            "LOQ 17": "17.3",
            "IDEAPAD 3": "15.6",
            "IDEAPAD 1": "15.6",
            "LEGION 5": "15.6",
            "LEGION SLIM 7": "16.0", 
            "LEGION PRO 7": "16.0",
            "LEGION PRO 5": "16.0",
            "MPG TRIDENT": "N/A", 
            "BOITIER": "N/A",     
            "PC GAMER": "N/A",    
            "ECRAN": "N/A"        
        };
        
        for (const [key, val] of Object.entries(map)) {
            if (t.includes(key)) {
                sc = val;
                break;
            }
        }
        
        if (!sc) {
             const ecranMatch = t.match(/ECRAN\s*(\d{2}\.?\d?)/);
             if (ecranMatch) {
                 sc = ecranMatch[1];
             } else {
                 const matches = t.match(/(\d{2}\.?\d?)\s*(["”]|POUCE|INCH)/);
                 if (matches) {
                     sc = matches[1];
                 } else if (t.includes("15.6")) sc = "15.6";
                 else if (t.includes("17.3")) sc = "17.3";
                 else if (t.includes("14.0") || t.includes(" 14 ")) sc = "14.0"; 
                 else if (t.includes("13.3")) sc = "13.3";
                 else if (t.includes("16.0") || t.includes(" 16 ")) sc = "16.0";
                 else if (t.includes("11.6")) sc = "11.6";
             }
        }
    }
    
    p.specs.screen = sc || "Unknown";

    // 5. Storage (Unified Storage Filter)
    let s = (p.specs.storage || "").toString().trim().toUpperCase();
    s = s.replace(/GO/g, 'GB').replace(/MO/g, 'MB').replace(/\s+/g, ''); 
    
    // VALIDITY CHECK: If Storage is <= 96GB, it's likely RAM (Pollution). WIPE IT.
    // Also wipe if NO DIGITS found (NaN), e.g. "SSD" or "NVMe" text only.
    const sVal = parseInt(s.replace(/\D/g, ''));
    if (isNaN(sVal) || sVal <= 96) {
        s = ""; 
    }
    
    // Deep Scan Title if invalid or missing
    if (!s || s === 'UNKNOWN' || s === '') {
        const t = p.title.toUpperCase();
        
        // 1. Check for TB/TO
        const tbMatch = t.match(/(\d+)\s*(TB|TO)/);
        if (tbMatch) {
             s = tbMatch[1] + "TB";
        } else {
             // 2. Check for GB/GO OR direct "SSD" match (e.g. "512 SSD")
            const matches = [...t.matchAll(/(\d+)\s*(GB|GO|G|SSD|NVME)/g)];
            let maxVal = 0;
            let vals = [];
            
            for (const m of matches) {
                const val = parseInt(m[1]);
                if (val < 5000) vals.push(val); 
                if (val >= 128 && val < 5000) { 
                    if (val > maxVal) maxVal = val;
                }
            }
            
            // Special handling for 32GB / 64GB (eMMC / Low end)
            if (maxVal === 0) {
                 const lowEnd = vals.find(v => v === 32 || v === 64);
                 if (lowEnd) {
                     const hasSmallRam = vals.some(v => v < lowEnd && v > 0);
                     const isCheap = t.includes("ATOM") || t.includes("CELERON") || t.includes("EMMC") || t.includes("STREAM") || t.includes("SCHNEIDER") || t.includes("CLOUD");
                     
                     if (hasSmallRam || isCheap) {
                         maxVal = lowEnd;
                     }
                 }
            }
            
            if (maxVal > 0) s = maxVal + "GB";
        }
    }
    
    // Bucket Normalization
    if (s) {
        if (s.includes("TB") || s.includes("TO")) {
             const val = parseInt(s.replace(/\D/g, ''));
             if (val >= 2) p.specs.storage = "2TB";
             else p.specs.storage = "1TB";
        } else {
            const val = parseInt(s.replace(/\D/g, '')) || 0;
            if (val >= 900) p.specs.storage = "1TB";
            else if (val >= 480) p.specs.storage = "512GB";
            else if (val >= 240) p.specs.storage = "256GB"; 
            else if (val >= 120) p.specs.storage = "128GB";
            else if (val >= 60) p.specs.storage = "64GB";
            else if (val >= 30) p.specs.storage = "32GB";
            else p.specs.storage = "Unknown";
        }
    } else {
         p.specs.storage = "Unknown";
    }

    // Accessories detection for Storage
    const tStorageCheck = p.title.toUpperCase();
    if (tStorageCheck.includes("BOITIER") || tStorageCheck.includes("ALIMENTATION") || tStorageCheck.includes("BARETTE") || tStorageCheck.includes("NINTENDO") || tStorageCheck.includes("REFROIDISSEUR") || tStorageCheck.includes("VENTILATEUR") || tStorageCheck.includes("PROTECTION") || tStorageCheck.includes("SUITE") || tStorageCheck.includes("ANTIVIRUS") || tStorageCheck.includes("OFFICE") || tStorageCheck.includes("LICENCE") || tStorageCheck.includes("DSP OEI") || tStorageCheck.includes("ECOUTEUR") || tStorageCheck.includes("VERSUS") || tStorageCheck.includes("SAC")) {
        p.specs.storage = "N/A";
    }

    // INTEGRITY CHECK
    const ramVal = parseInt(p.specs.ram) || 0;
    const storageVal = parseInt(p.specs.storage) || 0;

    if (ramVal > 64 && storageVal > 0 && storageVal <= 64) {
         const temp = p.specs.ram;
         p.specs.ram = p.specs.storage;
         p.specs.storage = temp;
    }
    if (ramVal >= 128) {
         p.specs.storage = p.specs.ram;
         p.specs.ram = "Unknown";
    }

    // 6. Price
    if (p.price) {
        if (typeof p.price === 'string') {
            let cleanPrice = p.price.toUpperCase().replace(/[^0-9,.]/g, '').replace(',', '.').trim();
            p.price = parseFloat(cleanPrice) || 0;
        } else {
            p.price = parseFloat(p.price) || 0;
        }
    }

    // 7. Category Logic
    let category = 'Office'; 
    const gpuRaw = (p.specs.gpu || '').toUpperCase() + " " + p.title.toUpperCase();
    
    if (gpuRaw.includes('RTX') || gpuRaw.includes('GTX') || gpuRaw.includes('RX 6') || gpuRaw.includes('RX 7') || gpuRaw.includes('ARC A')) {
        category = 'Gaming';
         if (!p.specs.gpu || p.specs.gpu === 'Unknown') {
             p.specs.gpu = 'Dedicated GPU'; 
         }
    } 
    else if (p.price > 0 && p.price < 2500) {
        category = 'Étudiant';
        if (!p.specs.gpu || p.specs.gpu === 'Unknown') p.specs.gpu = 'Integrated Graphics';
    } else {
         if (!p.specs.gpu || p.specs.gpu === 'Unknown') p.specs.gpu = 'Integrated Graphics';
    }
    p.specs.category = category;

    // 8. OS Normalization
    const title = p.title.toUpperCase();
    if (title.includes("WINDOWS 11")) {
        p.specs.os = title.includes("PRO") ? "Windows 11 Pro" : "Windows 11 Home";
    } else if (title.includes("WINDOWS 10")) {
         p.specs.os = "Windows 10";
    } else if (title.includes("UBUNTU") || title.includes("LINUX")) {
        p.specs.os = "Linux / Ubuntu";
    } else if (title.includes("FREEDOS") || title.includes("NO OS") || title.includes("SANS SYST")) {
        p.specs.os = "FreeDOS";
    } else {
        p.specs.os = "FreeDOS / No OS"; 
    }

    return p;
  });
};

const result = normalizeProductData(allData);

const analyze = (key) => {
    const counts = {};
    const unknownSamples = [];
    result.forEach(p => {
        // CORRECTION: Brand is Top Level
        const val = key === 'brand' ? (p.brand || 'Unknown') : (p.specs[key] || 'Unknown');
        
        counts[val] = (counts[val] || 0) + 1;
        if (val === 'Unknown') {
             if (unknownSamples.length < 50) unknownSamples.push(p.title);
        }
    });
    console.log(`\n--- ${key.toUpperCase()} COUNTS (Sorted) ---`);
    const sortedKeys = sortSizes(Object.keys(counts));
    sortedKeys.forEach(k => {
        console.log(`${k}: ${counts[k]}`);
    });
    if (unknownSamples.length > 0) {
        console.log(`\n[${key.toUpperCase()} Unknown Samples]:`);
        unknownSamples.forEach(s => console.log(`  - ${s}`));
    }
}

// analyze('brand'); 
// analyze('ram');
// analyze('cpu');
// analyze('gpu');
// analyze('os');
analyze('screen');
// analyze('storage');
