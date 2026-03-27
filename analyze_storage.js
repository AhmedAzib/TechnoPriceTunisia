const fs = require('fs');
const path = require('path');

// Mock data loading
const loadJSON = (file) => {
    try {
        return JSON.parse(fs.readFileSync(path.join(__dirname, 'frontend/src/data', file), 'utf8'));
    } catch (e) {
        console.error("Error loading " + file, e.message);
        return [];
    }
};

const tunisianetData = loadJSON('tunisianet_clean.json');
const spacenetData = loadJSON('spacenet_products.json');
const mytekData = loadJSON('mytek_test.json');
const wikiData = loadJSON('wiki_clean.json');

// Combined Data
const MASTER_DATA = [
  ...tunisianetData, 
  ...spacenetData,
  ...mytekData,
  ...wikiData
];

// Helper from productUtils (Partial) - we will refine this locally then copy back
const normalizeStorage = (p) => {
    let t = (p.title || p.name || "").toUpperCase();
    let s = (p.specs && p.specs.storage) ? p.specs.storage.toString().toUpperCase() : "";

    // Existing Logic (Simplified representation of what's currently in productUtils.js)
    if (s) {
         let cleanStorage = s.replace(/\s/g, '').replace('GO', 'GB').replace('TO', 'TB');
         if (cleanStorage.match(/^\d+$/)) cleanStorage += "GB";
         return cleanStorage;
    }
    
    return "Unknown";
};

// Analysis
console.log("Total Products:", MASTER_DATA.length);

const unknownStorage = MASTER_DATA.filter(p => {
    const s = normalizeStorage(p);
    // filtering loose "unknowns" or empty/bad values
    return !s || s === "Unknown" || s === "UNKNOWN" ;
});

console.log("Total Unknown Storage:", unknownStorage.length);

if (unknownStorage.length > 0) {
    console.log("\n--- Top 50 Unknown Storage Examples ---");
    unknownStorage.slice(0, 50).forEach(p => {
        console.log(`[${p.source || 'NoSource'}] Title: ${p.title || p.name}`);
        if(p.specs && p.specs.storage) console.log(`   > Original Spec: ${p.specs.storage}`);
    });
}
