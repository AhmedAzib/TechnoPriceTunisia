const fs = require('fs');
const path = require('path');

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

// --- EXACT COPY OF CURRENT LOGIC FROM productUtils.js ---
const normalizeSpecs = (title, specs) => {
    const t = title || "";
    const titleUpper = t.toUpperCase();

    // --- STORAGE Normalization ---
    // 0. Sanity Check: If existing spec looks like RAM (<= 32GB), wipe it so we scan the title.
    if (specs.storage) {
        const raw = specs.storage.toString().toUpperCase().replace(/\D/g, '');
        const val = parseInt(raw);
        // If it's small (<= 32) and not clearly TB, it's probably RAM (4, 8, 16, 32)
        if (val > 0 && val <= 32 && !specs.storage.toString().toUpperCase().includes('T')) {
            specs.storage = null;
        }
    }
    
    // 1. Try to extract from Title if missing or generic
    if (!specs.storage || specs.storage === 'Unknown' || specs.storage === 'SSD') {
        
        // A. Look for Terabyte patterns (1To, 2TB, 1T, etc.) - Priority
        const tbRegex = /(\d)\s?(TO|TB|TERA|T)\b/i;
        const tbMatch = t.match(tbRegex);
        
        // Safety: ensure it's not "7T Processor" or part of a model like "G7"
        const isProcessor = t.match(/(\d)T\s?PROCESSOR/i) || t.match(/CORE\s?T/i);
        
        if (tbMatch && !isProcessor) {
            specs.storage = `${tbMatch[1]}TB`;
        } else {
             // B. Look for Gigabyte patterns
             // We use a broader search then filter
             const broadRegex = /(\d{2,4})\s?(?:GO|GB|G|SSD|NVME|HDD)/gi;
             const potentialMatches = [...t.matchAll(broadRegex)];
             
             let bestStorage = null;
             
             for (const m of potentialMatches) {
                 const val = parseInt(m[1]); // The number
                 
                 // Heuristic:
                 if (val > 32 && val < 5000) {
                     bestStorage = val + "GB";
                     // Prefer standard sizes if found
                     if ([128, 256, 512, 1000, 1024].includes(val)) {
                         break; // Found a winner
                     }
                 }
             }
             
             if (bestStorage) {
                 specs.storage = bestStorage;
             }
        }
    }

    // 2. Normalize and Bucket whatever we have
    if (specs.storage) {
         let clean = specs.storage.toString().toUpperCase()
            .replace(/\s/g, '')
            .replace(/GO/g, 'GB')
            .replace(/TO/g, 'TB')
            .replace(/TERA/g, 'TB')
            .replace(/SSD/g, '') // strip text
            .replace(/HDD/g, '')
            .replace(/NVME/g, '')
            .replace(/PCIE/g, ''); 
            
         // Remove non-alphanumeric tail
         clean = clean.replace(/[^0-9TGB]/g, '');

         // Fix numeric-only result
         if (clean.match(/^\d+$/)) clean += "GB";
         
         // Standardize Buckets
         if (clean === "1000GB" || clean === "1024GB") clean = "1TB";
         if (clean === "2000GB" || clean === "2048GB") clean = "2TB";
         if (clean === "500GB" || clean === "512GB") clean = "512GB"; 
         
         specs.storage = clean;
    } else {
        specs.storage = 'Unknown';
    }
    return specs;
};

// --- RUN CHECK ---
console.log("Checking for Unknown Storage...");
let failCount = 0;
const failures = [];

MASTER_DATA.forEach(p => {
    // We only care if the spec is missing/unknown initially OR if it remains unknown
    const original = p.specs?.storage || 'Unknown';
    
    // Simulate runtime object
    const pSim = { 
        title: p.title || p.name || "",
        specs: { storage: original }
    };
    
    normalizeSpecs(pSim.title, pSim.specs);
    
    if (pSim.specs.storage === 'Unknown') {
        failCount++;
        failures.push(pSim.title);
    }
});

console.log(`Total Failures with Current Logic: ${failCount}`);
if (failCount > 0) {
    console.log("--- First 50 Failures ---");
    failures.slice(0, 50).forEach(t => console.log(t));
}
