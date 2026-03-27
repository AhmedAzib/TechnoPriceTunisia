
import fs from 'fs';

// Load Raw Data
const spacenet = JSON.parse(fs.readFileSync('src/data/spacenet_products.json', 'utf8'));
const mytek = JSON.parse(fs.readFileSync('src/data/mytek_test.json', 'utf8'));

// Combine
const data = [
    ...spacenet.map(p => ({...p, source: 'Spacenet'})),
    ...mytek.map(p => ({...p, source: 'MyTek'}))
];

console.log(`Loaded ${data.length} products from Spacenet & MyTek.`);

// Normalization Logic (Copied EXACTLY from ProductsPage.jsx)
const normalize = (p) => {
    const specs = { ...p.specs };
    let r = (specs.ram) ? specs.ram.toString().trim().toUpperCase() : "";
    
    // DEBUG: Capture raw if it matches user query
    const rawR = r;
    const hasMemoire = p.specs && JSON.stringify(p.specs).toUpperCase().includes("MÉMOIRE");
    
    // VALIDITY CHECK
    const rVal = parseInt(r.replace(/[^0-9]/g, ''));
    if (isNaN(rVal) || rVal > 96) {
        r = "";
    }
    
    if (!r || r === 'UNKNOWN' || r === '') {
        // Hardcoded Maps
        const modelRAMMap = {
            "MR942FN/A": "16", "13-4150NF": "8", "13-AF000NK": "8", 
            "IMAC ( APPLE64)": "8", "MACBOOK PRO RETINA – 13 POUCES": "8", "IMAC RETINA 5K – 27 POUCES": "8"     
        };
        for (const [key, val] of Object.entries(modelRAMMap)) {
            if (p.title.toUpperCase().includes(key)) {
                r = val + "GB";
                break;
            }
        }
        
        if (!r) {
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
        if (match) specs.ram = match[1] + "GB"; 
        else if (r.match(/^\d+$/)) specs.ram = r + "GB";
    } else {
        specs.ram = "Unknown";
    }
    
    // N/A Check
    const tCheck = p.title.toUpperCase();
    if (tCheck.includes("BOITIER") || tCheck.includes("ALIMENTATION") || tCheck.includes("BARETTE") || tCheck.includes("NINTENDO") || tCheck.includes("REFROIDISSEUR") || tCheck.includes("VENTILATEUR") || tCheck.includes("PROTECTION") || tCheck.includes("SUITE") || tCheck.includes("ANTIVIRUS") || tCheck.includes("OFFICE") || tCheck.includes("LICENCE") || tCheck.includes("DSP OEI") || tCheck.includes("ECOUTEUR") || tCheck.includes("VERSUS")) {
        specs.ram = "N/A";
    }

    return { ...p, specs, _rawRam: rawR, _hasMemoire: hasMemoire };
};

const results = data.map(normalize);

// Filter for Unknowns
const unknowns = results.filter(p => p.specs.ram === 'Unknown');
console.log(`\nTotal Unknowns: ${unknowns.length}`);

// Analysis
unknowns.forEach(u => {
    console.log(`[UNKNOWN] Source: ${u.source} | Title: ${u.title}`);
    console.log(`   Raw RAM: "${u._rawRam}"`);
    console.log(`   Full Specs: ${JSON.stringify(u.specs)}`);
    if (u._hasMemoire) console.log("   --> Contains 'MÉMOIRE' in specs!");
});

// Check specifically for items with "Mémoire RAM" related values that failed
const memoireItems = results.filter(p => JSON.stringify(p).toUpperCase().includes("MÉMOIRE") && p.specs.ram === 'Unknown');
if (memoireItems.length > 0) {
    console.log(`\n--- Items containing 'MÉMOIRE' that ended up UNKNOWN ---`);
    memoireItems.forEach(m => console.log(` - ${m.title} (Raw RAM: ${m._rawRam})`));
}
