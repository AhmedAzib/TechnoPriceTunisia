
const fs = require('fs');

// Load Data
const spacenet = require('./frontend/src/data/spacenet_gpu.json');
const products = [...spacenet]; 

const processProduct = (p) => {
    let boost = p.specs?.boost_clock || 'Unknown';
    let source = "Scraper";
    
    // 1. Sanitize Scraper Data (Simulate existing logic)
    if (boost !== 'Unknown') {
        if (boost.length > 15 || !boost.match(/\d/)) {
            boost = 'Unknown';
        }
    }
    
    // 2. Regex Fallback (Proposed)
    if (boost === 'Unknown') {
        const desc = (p.specs?.description || "") + " " + (p.description || "");
        // Look for "boost ... 2xxx MHz" or "fréquence ... 2xxx MHz"
        // Key phrases in French: "fréquence boostée jusqu’à 2647 MHz", "Boost Clock 2535 MHz"
        // Restrict scan to reasonable proximity to avoid false positives?
        
        const boostMatch = desc.match(/(?:boost|fréquence|clock).*?(\d{4})\s*MHz/i);
        if (boostMatch) {
            boost = boostMatch[1] + " MHz";
            source = "Regex";
        }
    }
    
    // 3. Map Fallback (Simulated Generic)
    if (boost === 'Unknown') {
        boost = "Map Value (Generic)";
        source = "Map";
    }

    return { title: p.title, boost: boost, source: source };
};

console.log("--- BOOST CLOCK REGEX TEST ---");
const results = [];

products.forEach(p => {
    const res = processProduct(p);
    if (res.source === "Regex") {
        results.push(res);
    }
});

console.log(`Found ${results.length} items via Regex.`);
results.slice(0, 20).forEach(r => {
    console.log(`[${r.source}] ${r.title.substring(0, 50)}... -> ${r.boost}`);
});
