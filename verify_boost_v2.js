
const fs = require('fs');

// Load Data
const spacenet = require('./frontend/src/data/spacenet_gpu.json');
const products = [...spacenet]; 

const processProduct = (p) => {
    let boost = p.specs?.boost_clock || 'Unknown';
    let source = "Scraper";
    
    // 1. Sanitize Scraper Data (Simulate logic)
    if (boost !== 'Unknown') {
        if (boost.length > 15 || !boost.match(/\d/)) {
            boost = 'Unknown';
        }
    }
    
    // 2. Regex Fallback (Simulate logic)
    if (boost === 'Unknown') {
        const fullDesc = (p.specs?.description || "") + " " + (p.description || "");
        const dMatch = fullDesc.match(/(?:boost|fréquence|clock).*?(\d{4})\s*MHz/i);
        if (dMatch) {
            boost = dMatch[1] + " MHz";
            source = "Regex";
        }
    }

    // 3. Rule Fallback (Simulate Logic)
    const titleUp = p.title.toUpperCase();
    
    // VRAM Extraction (Robust: Specs -> Title)
    let vramVal = 0;
    const vramMatch = (p.specs?.memory || (p.specs?.vram || "")).match(/(\d+)/);
    if (vramMatch) {
         vramVal = parseInt(vramMatch[0]);
    } else {
         const titleVram = p.title.match(/(\d+)\s*(?:Go|GB|G)/i);
         if (titleVram) vramVal = parseInt(titleVram[1]);
    }
    
    let ruleBoost = "Unknown";
    // RTX 3050 6GB
    if (titleUp.includes("RTX 3050") && vramVal === 6) {
        ruleBoost = "1470 MHz"; 
    }
    // Generic Map Fallback (Simplified)
    else if (titleUp.includes("RTX 5050")) ruleBoost = "2400 MHz";
    else if (titleUp.includes("RTX 3050")) ruleBoost = "1777 MHz";
    
    if (boost === "Unknown" && ruleBoost !== "Unknown") {
        boost = ruleBoost;
        source = "Map/Rule";
    }

    return { title: p.title, boost: boost, source: source };
};

console.log("--- FINAL BOOST VERIFICATION ---");
const targets = ["RTX 3050", "RTX 5050"];
const results = [];

products.forEach(p => {
    const titleUp = p.title.toUpperCase();
    if (targets.some(t => titleUp.includes(t))) {
        const res = processProduct(p);
        console.log(`[${res.source}] ${res.title.substring(0, 50)}... -> ${res.boost}`);
    }
});
