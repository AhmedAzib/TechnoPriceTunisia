
import fs from 'fs';

// Load Data
const tunisianet = JSON.parse(fs.readFileSync('src/data/tunisianet_clean.json', 'utf8'));
const spacenet = JSON.parse(fs.readFileSync('src/data/spacenet_products.json', 'utf8'));
const mytek = JSON.parse(fs.readFileSync('src/data/mytek_test.json', 'utf8'));
const wiki = JSON.parse(fs.readFileSync('src/data/wiki_clean.json', 'utf8'));

const allData = [
    ...tunisianet.map(p => ({...p, source: 'Tunisianet'})),
    ...spacenet.map(p => ({...p, source: 'Spacenet'})),
    ...mytek.map(p => ({...p, source: 'MyTek', specs: {} })), // MyTek has no specs initially
    ...wiki.map(p => ({...p, source: 'Wiki'}))
];

console.log(`Total Products: ${allData.length}`);

// Normalization Logic (Improved)
const normalize = (p) => {
    const specs = { ...p.specs };
    let s = (specs.storage || "").toString().trim().toUpperCase();
    s = s.replace(/GO/g, 'GB').replace(/MO/g, 'MB').replace(/\s+/g, ''); 
    
    // VALIDITY CHECK: If Storage is <= 96GB, it's likely RAM (Pollution). WIPE IT.
    // Also wipe if NO DIGITS found (NaN), e.g. "SSD" or "NVMe" text only.
    const sVal = parseInt(s.replace(/\D/g, ''));
    if (isNaN(sVal) || sVal <= 96) {
        s = ""; 
    }

    // Deep Scan Title if invalid or missing
    // We look for patterns like "256 Go", "512GB", "1 To"
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
                if (val < 5000) vals.push(val); // Collect all valid numbers
                if (val >= 128 && val < 5000) { 
                    if (val > maxVal) maxVal = val;
                }
            }
            
            // Special handling for 32GB / 64GB (eMMC / Low end)
            // If we didn't find a big SSD (>128), check for 32/64
            if (maxVal === 0) {
                 const lowEnd = vals.find(v => v === 32 || v === 64);
                 if (lowEnd) {
                     // Verify context to avoid RAM confusion (e.g. 32GB RAM vs 32GB Storage)
                     // If we have another number that is SMALLER (e.g. 2GB RAM, 32GB Storage), unlikely to be flipped.
                     // Or if title contains cheap CPU hints
                     const hasSmallRam = vals.some(v => v < lowEnd && v > 0);
                     const isCheap = t.includes("ATOM") || t.includes("CELERON") || t.includes("EMMC") || t.includes("STREAM") || t.includes("SCHNEIDER");
                     
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
             if (val >= 2) specs.storage = "2TB";
             else specs.storage = "1TB";
        } else {
            // GB buckets
            const val = parseInt(s.replace(/\D/g, '')) || 0;
            
            // DEBUG: Trace specific failure patterns user mentioned
            const tDebug = p.title.toUpperCase();
            if (tDebug.includes("512 GO SSD") || tDebug.includes("512GO")) {
                 if (specs.storage === "Unknown" && val < 100) {
                      // Only log if it failed to detect correct size
                      console.log(`DEBUG FAILURE [${p.source}]: '${p.title.substring(0,40)}...' | Raw S: '${s}' | Parsed Val: ${val}`);
                 }
            }

            if (val >= 900) specs.storage = "1TB";
            else if (val >= 480) specs.storage = "512GB";
            else if (val >= 240) specs.storage = "256GB"; 
            else if (val >= 120) specs.storage = "128GB";
            else if (val >= 60) specs.storage = "64GB";
            else if (val >= 30) specs.storage = "32GB";
            else specs.storage = "Unknown";
        }
    } else {
        specs.storage = "Unknown";
    }
    return { ...p, specs, _rawS: s };
};

const results = allData.map(normalize);
const unknowns = results.filter(p => p.specs.storage === 'Unknown');

console.log(`Unknown Storage Count: ${unknowns.length}`); // Expect ~1559

// Sample failures
console.log("\n--- Sample Unknown Storage Items ---");
unknowns.forEach(u => {
    if (u.source === 'MyTek' || u.source === 'Wiki') {
         console.log(`[${u.source}] ${u.title}`);
    }
});

// Check for "Memoire" patterns
const memoireHits = unknowns.filter(u => {
    const t = u.title.toUpperCase();
    return t.includes("MÉMOIRE") || t.includes("MEMOIRE");
});
console.log(`\nItems in Unknown that contain 'MÉMOIRE' or 'MEMOIRE': ${memoireHits.length}`);
if (memoireHits.length > 0) {
    console.log("--- Memoire Samples ---");
    memoireHits.slice(0, 30).forEach(u => console.log(`[${u.source}] ${u.title}`));
}
