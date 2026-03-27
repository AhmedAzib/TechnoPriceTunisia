
const fs = require('fs');

// Mock Data Loading
const tunisianet = require('./frontend/src/data/tunisianet_gpu.json');
const spacenet = require('./frontend/src/data/spacenet_gpu.json');

const products = [...spacenet]; // TARGETING SPACENET ONLY

// The NEW Logic (Copied from ProductsPage.jsx for testing)
const GPU_REF_MAP = {
      "RTX 5090": { cuda: 21760 },
      "RTX 5080": { cuda: 10752 },
      "RTX 5070 TI": { cuda: 8960 },
      "RTX 5070": { cuda: 6144 },
      "RTX 5060 TI": { cuda: 4608 },
      "RTX 5060": { cuda: 3840 },
      "RTX 5050": { cuda: 2560 },
      "RTX 4090": { cuda: 16384 },
      "RTX 4080 SUPER": { cuda: 10240 },
      "RTX 4080": { cuda: 9728 },
      "RTX 4070 TI SUPER": { cuda: 8448 },
      "RTX 4070 TI": { cuda: 7680 },
      "RTX 4070 SUPER": { cuda: 7168 },
      "RTX 4070": { cuda: 5888 },
      "RTX 4060 TI": { cuda: 4352 },
      "RTX 4060": { cuda: 3072 },
      "RTX 3060": { cuda: 3584 },
      "RTX 3050": { cuda: 2560 },
      "RTX 2060": { cuda: 1920 },
      "GTX 1660": { cuda: 1408 },
      "GTX 1650": { cuda: 896 },
      "GT 1030": { cuda: 384 },
      "GT1030": { cuda: 384 },
      "GT 730": { cuda: 384 },
      "GT730": { cuda: 384 },
      "GT 710": { cuda: 192 },
      "GT710": { cuda: 192 },
      "GT 610": { cuda: 48 },
      "GT610": { cuda: 48 },
      "GT 220": { cuda: 48 },
      "GT220": { cuda: 48 },
      "GT 210": { cuda: 16 },
      "GT210": { cuda: 16 }
};

const cleanCuda = (val) => {
     if (!val || val === 'Unknown') return 'Unknown';
     const num = parseInt(val.toString().replace(/\D/g, ''));
     if (isNaN(num)) return 'Unknown';
     if (num < 16 || num > 25000) return 'Unknown';
     return num.toString();
};

const processProduct = (p) => {
    let cudaCores = 'Unknown';
    
    // 1. Specs check
    const cudaKey = Object.keys(p.specs || {}).find(k => k.toLowerCase().includes('noyaux cuda') || k.toLowerCase().includes('cuda cores'));
    if (cudaKey) {
        cudaCores = cleanCuda(p.specs[cudaKey]);
    }

    // 2. Map Lookup
    const titleUp = p.title.toUpperCase().replace(/\s+/g, ' ').trim();
    const model = (p.specs?.gpu || "").toUpperCase();
    const isAmd = titleUp.includes("RADEON") || titleUp.includes("AMD") || titleUp.includes("RX ");
    let rule = null;
    
    // Sort keys by length desc
    const sortedKeys = Object.keys(GPU_REF_MAP).sort((a,b) => b.length - a.length);
    if (p.title.includes("4070 Ti")) {
        console.log("Sorted Keys:", JSON.stringify(sortedKeys));
    }

    for (const key of sortedKeys) {
        if (p.title.includes("4070 Ti")) {
             // Debug char codes
             if (key === "RTX 4070 TI") {
                 console.log(`Checking '${key}' against '${titleUp}'`);
                 console.log(`Key chars: ${key.split('').map(c => c.charCodeAt(0)).join(',')}`);
                 const idx = titleUp.indexOf("4070");
                 const segment = titleUp.substring(idx, idx + 10);
                 console.log(`Title segment '${segment}' chars: ${segment.split('').map(c => c.charCodeAt(0)).join(',')}`);
             }
        }
        if (titleUp.includes(key) || model.includes(key)) {
            if (p.title.includes("4070 Ti")) {
                 console.log(`MATCHED: '${key}'`);
            }
            rule = GPU_REF_MAP[key];
            // ...
             const vramMatch2 = (p.specs?.memory || (p.specs?.vram || "")).match(/(\d+)/);
             const vramVal = vramMatch2 ? parseInt(vramMatch2[0]) : 0;
             
             if (key === "RTX 3060" && vramVal >= 12) rule = { ...rule, cuda: 3584 }; 
            break; 
        }
    }

    if (rule && !isAmd) {
        if (rule.cuda) cudaCores = rule.cuda.toString();
    }
    
    // 3. Manual Override
    const manualCudaMap = {
         "Carte Graphique PNY GeForce RTX 5060 8Go Dual Fan": "3840",
         "Carte Graphique Pro PNY NVIDIA T1000 4Go GDDR6": "896",
         "Carte Graphique Gamer PNY GeForce GT 1030 2Go (VCG10302D4SFPPB)": "384"
    };
    if (manualCudaMap[p.title]) {
        cudaCores = manualCudaMap[p.title];
    }
    
    if (isAmd) cudaCores = "Unknown";
    
    // FINAL FORMATTING SIMULATION
    if (cudaCores !== 'Unknown') {
        cudaCores += " Units";
    }
    
    return { title: p.title, oldCuda: p.specs?.cuda_cores, newCuda: cudaCores, isAmd };
};

console.log("--- VERIFICATION RESULTS ---");
let fixedCount = 0;
products.forEach(p => {
    const res = processProduct(p);
    if (res.newCuda !== 'Unknown') {
         console.log(`[${res.newCuda}] ${res.title}`);
        fixedCount++;
    }
    // Check specific problematic ones
    if (res.title.includes("GT 610") || res.title.includes("GT 220") || res.title.includes("RX 7600")) {
        console.log(`CHECK: ${res.title} -> ${res.newCuda}`);
    }
});
console.log(`Total items with valid CUDA: ${fixedCount}`);
