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

// CURRENT LOGIC (Simplified wrapper for testing)
const getStorage = (title, existingSpec) => {
    const t = (title || "").toUpperCase();
    let spec = existingSpec || "";
    
    // Logic Copy-Paste from Step 85
    if (!spec || spec === 'Unknown' || spec === 'SSD') {
        const tbMatch = t.match(/(\d)\s?(To|TB|Tera|T)\b/i); 
        if (tbMatch && !t.match(/(\d)T\s?Processor/i)) {
            spec = `${tbMatch[1]}TB`;
        } else {
             const gbMatches = [...t.matchAll(/(\d{2,4})\s?(Go|GB|G)\b/gi)];
             let bestStorage = null;
             
             for (const m of gbMatches) {
                 const val = parseInt(m[1]);
                 if (val >= 64) { 
                     bestStorage = val + "GB";
                     break; 
                 }
             }
             
             if (!bestStorage) {
                 const ssdMatch = t.match(/(\d{3})\s?SSD/i); 
                 if (ssdMatch) {
                     bestStorage = ssdMatch[1] + "GB";
                 }
             }
             
             if (bestStorage) {
                 spec = bestStorage;
             }
        }
    }
    
    // Normalization
    if (spec && spec !== 'Unknown' && spec !== 'SSD') {
         let clean = spec.toString().toUpperCase()
            .replace(/\s/g, '')
            .replace('GO', 'GB')
            .replace('TO', 'TB')
            .replace('SSD', '')
            .replace('HDD', ''); 
         
         if (clean.match(/^\d+$/)) clean += "GB";
         if (clean === "1000GB" || clean === "1024GB") clean = "1TB";
         if (clean === "2000GB" || clean === "2048GB") clean = "2TB";
         return clean;
    }
    
    return "Unknown";
};

// SEARCH FOR FAILURES
console.log("Searching for failed 512/256/128 extractions...");
let failures = [];

MASTER_DATA.forEach(p => {
    const t = p.title || p.name || "";
    const original = (p.specs && p.specs.storage) ? p.specs.storage : "Unknown";
    const result = getStorage(t, original);
    
    if (result === "Unknown") {
        // We only care about titles that LOOK like they have storage
        const lowerT = t.toLowerCase();
        if (lowerT.includes("512") || lowerT.includes("256") || lowerT.includes("128") || lowerT.includes("1t")) {
            failures.push({ title: t, original: original, result: result });
        }
    }
});

console.log(`Found ${failures.length} potential failures.`);
if (failures.length > 0) {
    console.log("--- Top 20 Failures ---");
    failures.slice(0, 20).forEach(f => console.log(`[Fail] ${f.title}`));
}
