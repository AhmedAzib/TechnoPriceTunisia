const fs = require('fs');
const path = require('path');

// MOCK: Copy of generateVariantKey from productUtils.js
// We must use the EXACT logic currently in the file
const generateVariantKey = (product) => {
    let t = (product.title || product.name || "Unknown Product").toString().toUpperCase();
    
    // 1. Remove standardized RAM patterns
    t = t.replace(/\s(\d{1,3})\s?(GO|GB|G)\b/g, ' '); 

    // 2. Remove standardized Storage patterns
    t = t.replace(/\s(\d{3,4})\s?(GO|GB|G)\b/g, ' '); 
    t = t.replace(/\s(\d)\s?(TO|TB|T)\b/g, ' '); 
    t = t.replace(/\sSSD\b/g, ' ');
    t = t.replace(/\sHDD\b/g, ' ');
    t = t.replace(/\sNVME\b/g, ' ');
    
    // 3. Remove DDR mentions
    t = t.replace(/\sDDR\d\b/g, ' ');
    
    // 4. Remove Promotional Text
    t = t.replace(/\s(AVEC|\+|PLUS)\s.*?(OFFERTE?|GRATUITE?|INCLUSE?)/g, ' ');
    t = t.replace(/\s(SACOCHE|SAC|SOURIS|CASQUE).*?(OFFERTE?|GRATUITE?|INCLUSE?)/g, ' ');

    // 5. Cleanup
    t = t.replace(/\s+\//g, '/'); 
    t = t.replace(/\/\s+/g, '/');
    t = t.replace(/\s+/g, ' ').trim();
    
    if (t.endsWith('/')) t = t.slice(0, -1).trim();

    return t;
};

// --- DATA SCANNERS ---
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

// --- AUDIT ---
const groups = {};
MASTER_DATA.forEach(p => {
    const key = generateVariantKey(p);
    if (!groups[key]) groups[key] = [];
    groups[key].push(p.title);
});

console.log("--- GROUPING AUDIT ---");
console.log(`Total Products: ${MASTER_DATA.length}`);
console.log(`Total Groups: ${Object.keys(groups).length}`);

// Find "Near Misses" - keys that are ALMOST identical but different
// We sort keys effectively
const sortedKeys = Object.keys(groups).sort();
const likelyDupes = [];

for (let i = 0; i < sortedKeys.length - 1; i++) {
    const k1 = sortedKeys[i];
    const k2 = sortedKeys[i+1];
    
    // Simple diff check: if they share the first 20 chars
    if (k1.slice(0, 20) === k2.slice(0, 20)) {
        likelyDupes.push({ k1, k2 });
    }
}

console.log(`Potential Dupes (Split Groups): ${likelyDupes.length}`);
console.log("Top 10 Potential Split Groups:");
likelyDupes.slice(0, 20).forEach(d => {
    console.log(`  [KEY 1]: ${d.k1}`);
    console.log(`  [KEY 2]: ${d.k2}`);
    console.log(`     -> Count 1: ${groups[d.k1].length}, Count 2: ${groups[d.k2].length}`);
    console.log("-");
});
