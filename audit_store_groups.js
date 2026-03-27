const fs = require('fs');
const path = require('path');

// --- EXACT CURRENT LOGIC FROM productUtils.js ---
const generateVariantKey = (product) => {
    let t = (product.title || product.name || "Unknown Product").toString().toUpperCase();
    
    // 0. Remove Common Prefixes/Types (Noise)
    t = t.replace(/PC PORTABLE/g, ' ');
    t = t.replace(/ORDINATEUR PORTABLE/g, ' ');
    t = t.replace(/LAPTOP/g, ' ');
    t = t.replace(/NOTEBOOK/g, ' ');
    t = t.replace(/GAMER/g, ' ');
    t = t.replace(/GAMING/g, ' ');
    t = t.replace(/ULTRABOOK/g, ' ');

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
    
    // 4. Remove CPU Info
    const cpuKeywords = [
        "INTEL", "AMD", "RYZEN", "ATHLON", "CELERON", "PENTIUM", 
        "CORE", "ULTRA", "I9", "I7", "I5", "I3", "PROCESSOR"
    ];
    const cpuRegex = new RegExp(`\\b(${cpuKeywords.join('|')})\\b`, 'g');
    t = t.replace(cpuRegex, ' ');

    // 5. Remove Promotional Text
    t = t.replace(/\s(AVEC|\+|PLUS)\s.*?(OFFERTE?|GRATUITE?|INCLUSE?)/g, ' ');
    t = t.replace(/\s(SACOCHE|SAC|SOURIS|CASQUE).*?(OFFERTE?|GRATUITE?|INCLUSE?)/g, ' ');
    
    // 6. COLORS
    const colors = [
        "NOIR", "BLACK", 
        "GRIS", "GREY", "GRAY", "SIDEROL", "SIDERAL", "SIDERALE", 
        "ARGENT", "SILVER", 
        "BLANC", "WHITE", 
        "BLEU", "BLUE", "CIEL",
        "ROUGE", "RED", 
        "GOLD", "OR", 
        "MIDNIGHT", "STARLIGHT", "LUMIÈRE STELLAIRE",
        "MINUIT", "COSMOS", "ECLIPSE", "PLATINUM", "TITAN",
        "VERT", "GREEN", "ROSE", "PINK"
    ];
    const colorRegex = new RegExp(`\\b(${colors.join('|')})\\b`, 'g');
    t = t.replace(colorRegex, ' ');

    // 7. Cleanup
    t = t.replace(/("|'|\-|_|\/|\\|\(|\)|\[|\]|\.|,)/g, ' '); 
    t = t.replace(/\s+/g, ' ').trim();
    
    return t;
};

// --- LOAD DATA ---
const loadJSON = (file, sourceName) => {
    try {
        const data = JSON.parse(fs.readFileSync(path.join(__dirname, 'frontend/src/data', file), 'utf8'));
        return data.map(p => ({ ...p, source: sourceName }));
    } catch (e) {
        return [];
    }
};

const MASTER_DATA = [
  ...loadJSON('tunisianet_clean.json', 'Tunisianet'), 
  ...loadJSON('spacenet_products.json', 'Spacenet'),
  ...loadJSON('mytek_test.json', 'MyTek'),
  ...loadJSON('wiki_clean.json', 'Wiki')
];

// --- AUDIT STORE DISTRIBUTION ---
const groups = {};
MASTER_DATA.forEach(p => {
    const key = generateVariantKey(p);
    if (!groups[key]) groups[key] = { key, products: [], stores: new Set() };
    groups[key].products.push(p);
    groups[key].stores.add(p.source);
});

let totalGroups = 0;
let multiStoreGroups = 0;
let spacenetInMixed = 0;
let wikiInMixed = 0;

Object.values(groups).forEach(g => {
    // Only count if group has > 1 product (otherwise no grouping happened)
    if (g.products.length > 1) {
        totalGroups++;
        if (g.stores.size > 1) {
            multiStoreGroups++;
            if (g.stores.has('Spacenet')) spacenetInMixed++;
            if (g.stores.has('Wiki')) wikiInMixed++;
        }
    }
});

console.log(`Total Groups > 1 item: ${totalGroups}`);
console.log(`Multi-Store Groups: ${multiStoreGroups} (Groups with products from >1 store)`);
console.log(`   - Containing Spacenet: ${spacenetInMixed}`);
console.log(`   - Containing Wiki: ${wikiInMixed}`);

// DEBUG: Show Spacenet/Wiki items that are NOT in mixed groups (Isolated)
// Maybe they have different naming conventions?
console.log("\n--- ISOLATED WIKI EXAMPLES (Top 5) ---");
let wikiIsolatedCount = 0;
Object.values(groups).forEach(g => {
    if (g.stores.size === 1 && g.stores.has('Wiki') && wikiIsolatedCount < 5) {
        console.log(`KEY: [${g.key}]`);
        console.log(`   Title: ${g.products[0].title}`);
        wikiIsolatedCount++;
    }
});

console.log("\n--- ISOLATED SPACENET EXAMPLES (Top 5) ---");
let spacenetIsolatedCount = 0;
Object.values(groups).forEach(g => {
    if (g.stores.size === 1 && g.stores.has('Spacenet') && spacenetIsolatedCount < 5) {
        console.log(`KEY: [${g.key}]`);
        console.log(`   Title: ${g.products[0].title}`);
        spacenetIsolatedCount++;
    }
});
