
import fs from 'fs';

// Load Data
const tunisianet = JSON.parse(fs.readFileSync('src/data/tunisianet_clean.json', 'utf8'));
const spacenet = JSON.parse(fs.readFileSync('src/data/spacenet_products.json', 'utf8'));
const mytek = JSON.parse(fs.readFileSync('src/data/mytek_test.json', 'utf8'));
const wiki = JSON.parse(fs.readFileSync('src/data/wiki_clean.json', 'utf8'));

const allData = [...tunisianet, ...spacenet, ...mytek, ...wiki];

const normalizeProductData = (data) => {
  return data.map(product => {
    const p = { ...product, specs: { ...product.specs } };

    // COPY PASTE LOGIC FROM PRODUCTS PAGE
    
    // 3. RAM (Unified Filter)
    let r = (p.specs && p.specs.ram) ? p.specs.ram.toString().trim().toUpperCase() : "";
    
    // VALIDITY CHECK
    const rVal = parseInt(r.replace(/[^0-9]/g, ''));
    if (isNaN(rVal) || rVal > 96) {
        r = "";
    }
    
    // Deep Scan Title if RAM is missing or "Unknown" or invalid
    if (!r || r === 'UNKNOWN' || r === '') {
        // Hardcoded Maps for specific models known to have no RAM in title
        const modelRAMMap = {
            "MR942FN/A": "16", 
            "13-4150NF": "8",   
            "13-AF000NK": "8",  
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
            // CURRENT REGEX
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
        r = r.replace(/GO/g, 'GB').replace(/\s+/g, ''); 
        r = r.replace(/(\d+)G$/, '$1GB'); 
        
        const match = r.match(/(\d+)GB/);
        if (match) p.specs.ram = match[1] + "GB"; 
        else if (r.match(/^\d+$/)) p.specs.ram = r + "GB";
    } else {
        p.specs.ram = "Unknown";
    }
    
    // Accessories detection
    const tCheck = p.title.toUpperCase();
    if (tCheck.includes("BOITIER") || tCheck.includes("ALIMENTATION") || tCheck.includes("PROTECTION") || tCheck.includes("BARETTE") || tCheck.includes("WIN PRO") || tCheck.includes("WIN HOME") || tCheck.includes("ECRAN") || tCheck.includes("VERSUS 24") || tCheck.includes("STATION DE CALCUL") || tCheck.includes("NINTENDO") || tCheck.includes("CHARGEUR") || tCheck.includes("SAC") || tCheck.includes("LOGICIEL")) {
        p.specs.ram = "N/A";
    }

    return p;
  });
};

const result = normalizeProductData(allData);

console.log(`Total Products: ${result.length}`);

let unknownCount = 0;
let naCount = 0;
let suspectNA = []; // N/A items that look like laptops

result.forEach(p => {
    if (p.specs.ram === 'Unknown') {
        unknownCount++;
        console.log(`[UNKNOWN] ${p.title} (Original RAM: ${p.specs && p.specs.ram})`);
    } else if (p.specs.ram === 'N/A') {
        naCount++;
        // Check if it looks like a computer but got classified as N/A?
        // Actually, N/A is applied based on keywords like "Boitier".
        // Let's see if any have "Go" in the title.
        if (p.title.toUpperCase().includes(" GO ") || p.title.toUpperCase().includes(" GB ")) {
             suspectNA.push(p.title);
        }
    }
});

console.log(`\nUnknown RAM Count: ${unknownCount}`);
console.log(`N/A RAM Count: ${naCount}`);

if (suspectNA.length > 0) {
    console.log("\nSuspect N/A Items (contain GB/GO):");
    suspectNA.slice(0, 20).forEach(t => console.log(` - ${t}`));
}
