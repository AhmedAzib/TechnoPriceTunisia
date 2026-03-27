
const fs = require('fs');

// Load Data
const spacenet = require('./frontend/src/data/spacenet_gpu.json');
const tunisianet = require('./frontend/src/data/tunisianet_gpu.json');
const products = [...spacenet, ...tunisianet]; 

// BASE MAP (Current Production)
const GPU_REF_MAP = {
      "RTX 5090": { bus: "512 bit" },
      "RTX 5080": { bus: "256 bit" },
      "RTX 5070 TI": { bus: "256 bit" },
      "RTX 5070": { bus: "192 bit" },
      "RTX 5060 TI": { bus: "128 bit" },
      "RTX 5060": { bus: "128 bit" },
      "RTX 5050": { bus: "96 bit" }, // The Problem? User says 128?
      "RTX 4090": { bus: "384 bit" },
      "RTX 4080 SUPER": { bus: "256 bit" },
      "RTX 4080": { bus: "256 bit" },
      "RTX 4070 TI SUPER": { bus: "256 bit" },
      "RTX 4070 TI": { bus: "192 bit" },
      "RTX 4070 SUPER": { bus: "192 bit" },
      "RTX 4070": { bus: "192 bit" },
      "RTX 4060 TI": { bus: "128 bit" },
      "RTX 4060": { bus: "128 bit" },
      "RTX 4050": { bus: "96 bit" },
      "RTX 3090 TI": { bus: "384 bit" },
      "RTX 3090": { bus: "384 bit" },
      "RTX 3080 TI": { bus: "384 bit" },
      "RTX 3080": { bus: "320 bit" },
      "RTX 3070 TI": { bus: "256 bit" },
      "RTX 3070": { bus: "256 bit" },
      "RTX 3060 TI": { bus: "256 bit" },
      "RTX 3060": { bus: "192 bit" },
      "RTX 3050": { bus: "128 bit" }, // Problem: 6GB is 96 bit
      "RTX 2080 TI": { bus: "352 bit" },
      "RTX 2080": { bus: "256 bit" },
      "RTX 2070": { bus: "256 bit" },
      "RTX 2060": { bus: "192 bit" },
      "GTX 1660": { bus: "192 bit" },
      "GTX 1650": { bus: "128 bit" },
      "GTX 1630": { bus: "64 bit" },
      "GT 1030": { bus: "64 bit" },
      "GT1030": { bus: "64 bit" },
      "GT 730": { bus: "64 bit" },
      "GT730": { bus: "64 bit" },
      "GT 710": { bus: "64 bit" },
      "GT710": { bus: "64 bit" },
      "GT 610": { bus: "64 bit" },
      "GT610": { bus: "64 bit" },
      "GT 520": { bus: "64 bit" },
      "GT 220": { bus: "64 bit" }, // User requested 64-bit for AFOX GT220
      "GT220": { bus: "64 bit" },
      "GT 210": { bus: "64 bit" },
      "GT210": { bus: "64 bit" },
};

const processProduct = (p) => {
    const titleUp = p.title.toUpperCase().replace(/\s+/g, ' ').trim();
    const model = (p.specs?.gpu || "").toUpperCase();
    const isAmd = titleUp.includes("RADEON") || titleUp.includes("AMD") || titleUp.includes("RX ");
    
    // VRAM Logic
    const vramMatch2 = (p.specs?.memory || (p.specs?.vram || "")).match(/(\d+)/);
    const vramVal = vramMatch2 ? parseInt(vramMatch2[0]) : 0;
    
    // Base Rule
    let rule = null;
    const sortedKeys = Object.keys(GPU_REF_MAP).sort((a,b) => b.length - a.length);
    let matchedKey = "";
    
    for (const key of sortedKeys) {
        if (titleUp.includes(key) || model.includes(key)) {
            rule = { ...GPU_REF_MAP[key] }; // Clone
            matchedKey = key;
            break;
        }
    }
    
    // --- 1. OLD LOGIC SIMULATION (Current Production) ---
    // (Without specific variant fixes for Bus, except for generic regex fallback)
    let busOld = "Unknown";
    if (rule && rule.bus && !isAmd) busOld = rule.bus;
    
    
    // --- 2. NEW LOGIC (Proposed Fix) ---
    // Apply specific variant overrides
    if (rule) {
         // RTX 3050 6GB -> 96 bit
         if (matchedKey === "RTX 3050" && vramVal === 6) {
             rule.bus = "96 bit";
         }
         
         // RTX 5050 8GB -> 128 bit
         if (matchedKey === "RTX 5050" && (vramVal === 8 || titleUp.includes("8GB") || titleUp.includes("8GO"))) {
             rule.bus = "128 bit";
         }
         
         // GT 730 4GB -> 128 bit (Broadened)
         const is4GB = vramVal === 4 || titleUp.includes(" 4GO") || titleUp.includes(" 4GB") || titleUp.includes(" 4 GO");
         if ((matchedKey === "GT 730" || matchedKey === "GT730") && is4GB) {
              if (!titleUp.includes("64 BIT") && !titleUp.includes("64-BIT")) {
                   rule.bus = "128 bit";
              }
         }
    }
    
    let busNew = "Unknown";
    if (rule && rule.bus && !isAmd) {
        busNew = rule.bus;
    }
    
    // Regex Fallback (Shared)
    const desc = (p.description || "") + " " + (p.specs?.description || "");
    if (busNew === "Unknown") {
          const busMatch = desc.match(/(\d{2,3})\s*-?\s*bits?/i);
          if (busMatch) busNew = `${busMatch[1]} bits`;
    }
    
    return { title: p.title, old: busOld, new: busNew, key: matchedKey, vram: vramVal };
};

console.log("--- CHANGED ITEMS (Proposed Fix) ---");
let changedCount = 0;
const buckets = {};

products.forEach(p => {
    const res = processProduct(p);
    
    // Bucket New
    if (res.new !== 'Unknown') {
        if (!buckets[res.new]) buckets[res.new] = [];
        buckets[res.new].push(res.title);
    }
    
    if (res.old !== res.new) {
        console.log(`[FIXED] ${res.title.substring(0, 60)}...`);
        console.log(`Was: ${res.old} | Now: ${res.new} (Key: ${res.key}, VRAM: ${res.vram})`);
        console.log("-");
        changedCount++;
    }
});

console.log(`Total changed: ${changedCount}`);
console.log("--- BUCKET SAMPLES (Top 5) ---");
Object.keys(buckets).sort().forEach(k => {
    console.log(`BUCKET: ${k} (${buckets[k].length} items)`);
    buckets[k].slice(0, 5).forEach(t => console.log(" - " + t.substring(0, 50)));
});
