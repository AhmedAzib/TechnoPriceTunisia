
const fs = require('fs');

// Load Data
const tunisianet = require('./frontend/src/data/tunisianet_gpu.json');
const spacenet = require('./frontend/src/data/spacenet_gpu.json');
const products = [...spacenet, ...tunisianet]; // Check both

// FULL MAP from ProductsPage.jsx
const GPU_REF_MAP = {
      "RTX 5090": { bus: "512 bit" },
      "RTX 5080": { bus: "256 bit" },
      "RTX 5070 TI": { bus: "256 bit" },
      "RTX 5070": { bus: "192 bit" },
      "RTX 5060 TI": { bus: "128 bit" },
      "RTX 5060": { bus: "128 bit" },
      "RTX 5050": { bus: "96 bit" },
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
      "RTX 3050": { bus: "128 bit" },
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
      "GT 220": { bus: "128 bit" },
      "GT220": { bus: "128 bit" },
      "GT 210": { bus: "64 bit" },
      "GT210": { bus: "64 bit" },
};


const processProduct = (p) => {
    // Logic from ProductsPage.jsx (Simulated)
    const titleUp = p.title.toUpperCase().replace(/\s+/g, ' ').trim();
    const model = (p.specs?.gpu || "").toUpperCase();

    let rule = null;
    const sortedKeys = Object.keys(GPU_REF_MAP).sort((a,b) => b.length - a.length);
    for (const key of sortedKeys) {
        if (titleUp.includes(key) || model.includes(key)) {
            rule = GPU_REF_MAP[key];
            break;
        }
    }

    let bus = p.specs?.bus_memoire || 'Unknown';
    const desc = (p.description || "") + " " + (p.specs?.description || ""); // Simplification

    // 1. Map Fallback (Priority)
    if (rule && rule.bus) {
        // Preference: If current 'bus' is garbage or 'Unknown', use Map
        if (bus === 'Unknown' || !bus.includes('bit')) {
             bus = rule.bus;
        }
    }

    // 2. Regex Fallback
    if (bus === 'Unknown') {
          const busMatch = desc.match(/(\d+)\s*bits?/i);
          if (busMatch) {
               bus = `${busMatch[1]} bits`; // Pluralize as requested
          }
    }

    // 3. Normalization cleanup
    if (bus !== 'Unknown') {
        // Enforce " bits"
        let num = bus.replace(/\D/g, '');
        if (num) {
            bus = `${num} bits`;
        }
    }

    return { title: p.title, bus };
};

console.log("--- VERIFICATION RESULTS ---");
let validCount = 0;
// Test first 50 Spacenet + random Tunisianet + ALL AMD
const amdItems = products.filter(p => p.title.toUpperCase().includes("RADEON") || p.title.toUpperCase().includes("RX "));
const testSet = [...spacenet.slice(0, 50), ...tunisianet.slice(0, 10), ...amdItems.slice(0, 20)];

testSet.forEach(p => {
    const res = processProduct(p);
    if (res.bus !== 'Unknown') {
        console.log(`[${res.bus}] ${res.title.substring(0, 60)}...`);
        validCount++;
    } else {
        // console.log(`[UNKNOWN] ${p.title.substring(0, 50)}...`);
    }
});
console.log(`Total valid: ${validCount}`);
