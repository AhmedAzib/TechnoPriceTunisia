const fs = require('fs');
const path = require('path');

// Mock data loading
const loadJSON = (file) => {
    try {
        return JSON.parse(fs.readFileSync(path.join(__dirname, 'frontend/src/data', file), 'utf8'));
    } catch (e) {
        return [];
    }
};

const MASTER_DATA = [
  ...loadJSON('tunisianet_clean.json'), 
  ...loadJSON('spacenet_products.json'),
  ...loadJSON('mytek_test.json'),
  ...loadJSON('wiki_clean.json')
];

// --- THE NEW LOGIC TO TEST ---
const normalizeSpecs = (title, specs) => {
    const t = title.toUpperCase();
    
    // 1. Try to extract from Title if missing or generic
    if (!specs.storage || specs.storage === 'Unknown' || specs.storage === 'SSD') {
        const tbMatch = t.match(/(\d)\s?(To|TB|Tera)/i);
        if (tbMatch) {
            specs.storage = `${tbMatch[1]}TB`;
        } else {
             const gbMatches = [...t.matchAll(/(\d{3,4})\s?(Go|GB|G)\b/gi)];
             let bestStorage = null;
             for (const m of gbMatches) {
                 const val = parseInt(m[1]);
                 if (val > 64) { 
                     bestStorage = val + "GB";
                     break; 
                 }
             }
             if (bestStorage) specs.storage = bestStorage;
        }
    }

    // 2. Normalize
    if (specs.storage) {
         let cleanStorage = specs.storage.toString().toUpperCase()
            .replace(/\s/g, '')
            .replace('GO', 'GB')
            .replace('TO', 'TB')
            .replace('SSD', '')
            .replace('HDD', '');
         
         if (cleanStorage.match(/^\d+$/)) cleanStorage += "GB";
         if (cleanStorage === "1000GB" || cleanStorage === "1024GB") cleanStorage = "1TB";
         if (cleanStorage === "2000GB" || cleanStorage === "2048GB") cleanStorage = "2TB";
         specs.storage = cleanStorage;
    } else {
        specs.storage = 'Unknown';
    }
    return specs;
};

// --- RUN VERIFICATION ---
console.log("Starting Verification...");
let unknownCount = 0;
let fixedCount = 0;

MASTER_DATA.forEach(p => {
    const originalStorage = (p.specs && p.specs.storage) ? p.specs.storage : "Unknown";
    const specs = { storage: originalStorage }; // clone
    
    normalizeSpecs(p.title || p.name || "", specs);
    
    if (specs.storage === 'Unknown') {
        unknownCount++;
        // console.log("Still Unknown:", p.title); // Optional debug
    } else if (originalStorage === 'Unknown' || !originalStorage) {
        fixedCount++;
    }
});

console.log(`\nResults:`);
console.log(`Fixed Items: ${fixedCount}`);
console.log(`Remaining Unknowns: ${unknownCount}`);
