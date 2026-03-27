import fs from 'fs';

// Load Data
const tunisianet = JSON.parse(fs.readFileSync('src/data/tunisianet_clean.json', 'utf8'));
const spacenet = JSON.parse(fs.readFileSync('src/data/spacenet_products.json', 'utf8'));
const mytek = JSON.parse(fs.readFileSync('src/data/mytek_test.json', 'utf8'));
const wiki = JSON.parse(fs.readFileSync('src/data/wiki_clean.json', 'utf8'));

// Minimal Normalization for testing
const allData = [
    ...tunisianet.map(p => ({...p, source: 'Tunisianet'})),
    ...spacenet.map(p => ({...p, source: 'Spacenet'})),
    ...mytek.map(p => ({...p, source: 'MyTek'})), 
    ...wiki.map(p => ({...p, source: 'Wiki'}))
];

console.log(`Total Products: ${allData.length}`);

// LOGIC TO TEST:
// Remove RAM (4Go, 8GB, etc)
// Remove Storage (256Go, 512SSD, 1To, etc)
// Remove "SSD", "HDD", "DDR4", "DDR5"
const generateVariantKey = (product) => {
    let t = product.title.toUpperCase();
    
    // 1. Remove standardized RAM patterns
    // 4Go, 8 Go, 16GB, 32G, etc.
    t = t.replace(/\s(\d{1,3})\s?(GO|GB|G)\b/g, ' '); 

    // 2. Remove standardized Storage patterns
    // 256Go, 512 Go, 1To, 1 TB, 256 SSD, 512SSD
    t = t.replace(/\s(\d{3,4})\s?(GO|GB|G)\b/g, ' '); // 256 GB
    t = t.replace(/\s(\d)\s?(TO|TB|T)\b/g, ' '); // 1 TB
    t = t.replace(/\sSSD\b/g, ' ');
    t = t.replace(/\sHDD\b/g, ' ');
    t = t.replace(/\sNVME\b/g, ' ');
    
    // 3. Remove DDR mentions
    t = t.replace(/\sDDR\d\b/g, ' ');

    // 4. Remove Promotional Text (Sacoche, Souris, Offert, Gratuit)
    t = t.replace(/\sAVEC\s.*?(OFFERT|GRATUIT|INCLUS)/g, ' '); // "Avec Sacoche Offerte"
    t = t.replace(/\s(\+|plus)\s.*?(OFFERT|GRATUIT|INCLUS)/g, ' '); // "+ Sacoche Offerte"
    t = t.replace(/\sSACOCHE.*?OFFERTE?/g, ' ');
    t = t.replace(/\sSAC\s.*?OFFERT?/g, ' ');
    t = t.replace(/\sSOURIS.*?OFFERTE?/g, ' ');
    
    // 5. Cleanup cleanup
    t = t.replace(/\s+\//g, '/'); // Remove spaces around slashes specific to Tunisianet naming
    t = t.replace(/\/\s+/g, '/');
    t = t.replace(/\s+/g, ' ').trim();
    
    // Remove trailing / if exists (Tunisianet format often ends with specs)
    // E.g. "Name / CPU / " -> "Name / CPU"
    
    return t;
};

const groups = {};

allData.forEach(p => {
    const key = generateVariantKey(p);
    if (!groups[key]) groups[key] = [];
    groups[key].push(p);
});

// Analyze Groups
const multiItemGroups = Object.values(groups).filter(g => g.length > 1);

console.log(`\nTotal Groups Found: ${Object.keys(groups).length}`);
console.log(`Groups with Variants: ${multiItemGroups.length}`);

console.log("\n--- SAMPLE GROUPS (Verify if they are truly identical besides RAM/Storage) ---");
multiItemGroups.slice(0, 20).forEach(g => {
    console.log(`\nGROUP KEY: "${generateVariantKey(g[0])}" (Count: ${g.length})`);
    g.forEach(p => console.log(`   - [${p.source}] ${p.title}`));
});
