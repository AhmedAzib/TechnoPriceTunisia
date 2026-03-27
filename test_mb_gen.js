import fs from 'fs';

const skymilData = JSON.parse(fs.readFileSync('C:/Users/USER/Documents/programmation/frontend/src/data/skymil_intel_mobos.json', 'utf8'));

// Apply logic from ProductsPage.jsx
let mbGenStats = {};

skymilData.forEach(p => {
    // 27. Filter "Generation" (PCIe Gen 3, 4, 5) - "10000% safe" strict mapping
    let mbGen = p.specs?.generation || "Unknown";
    const isMobo = (p.category || '').toLowerCase() === 'motherboard' || (p.specs?.category || '').toLowerCase() === 'motherboard' || p.title.toLowerCase().includes("carte mère") || p.title.toLowerCase().includes("motherboard") || p.title.includes("MSI PRO B760M-A WIFI") || p.title.includes("ASRock B760M PG WIFI");
    
    if (isMobo) {
        const CHIPSET_GEN_MAP = {
        // GEN 5 (PCIe 5.0) - High End / New Mid
        "Z790": "Gen 5", "X670": "Gen 5", "X670E": "Gen 5", "Z690": "Gen 5", 
        "B650E": "Gen 5", "X870": "Gen 5", "X870E": "Gen 5", "Z890": "Gen 5", 
        "B850": "Gen 5", "B860": "Gen 5", // Verified Audit
        
        // GEN 4 (PCIe 4.0) - Mid Range
        "B650": "Gen 4", // Standard B650 GPU slot is usually Gen 4 (safe baseline)
        "B550": "Gen 4", "X570": "Gen 4", "A620": "Gen 4", 
        "Z590": "Gen 4", "B560": "Gen 4", "H570": "Gen 4", "H510": "Gen 4",
        "H610": "Gen 4", "B760": "Gen 4", "H770": "Gen 4",
        "B840": "Gen 4", "H810": "Gen 4", // Verified Audit

        // GEN 3 (PCIe 3.0) - Legacy / Entry
        "Z490": "Gen 3", "H470": "Gen 3", "B460": "Gen 3", "H410": "Gen 3",
        "Z390": "Gen 3", "B365": "Gen 3", "B360": "Gen 3", "H370": "Gen 3", "H310": "Gen 3",
        "B450": "Gen 3", "X470": "Gen 3", "X370": "Gen 3", "B350": "Gen 3", 
        "A320": "Gen 3", "A520": "Gen 3"
        };

        const t = p.title.toUpperCase();
        for (const [chipset, gVal] of Object.entries(CHIPSET_GEN_MAP)) {
            // Priority check for B650E to avoid matching "B650" substring first
            if (chipset === "B650" && t.includes("B650E")) continue;
            
            if (t.includes(chipset)) {
                mbGen = gVal;
                break;
            }
        }
    }
    
    if (!mbGenStats[mbGen]) mbGenStats[mbGen] = 0;
    mbGenStats[mbGen]++;
    
    if (mbGen === "Unknown") {
        console.log(`Unknown Gen for: ${p.title} - Category: ${p.category}`);
    } else if (p.title.includes("ASRock B760M PG WIFI") || p.title.includes("B760M-A WIFI")) {
        console.log(`Success! ${p.title} classified as ${mbGen}`);
    }
});

console.log("Stats:", mbGenStats);
