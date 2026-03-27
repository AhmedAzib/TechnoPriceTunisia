
const fs = require('fs');

// Load Data
const spacenet = require('./frontend/src/data/spacenet_gpu.json');
const products = [...spacenet]; 

const processProduct = (p) => {
    let boost = p.specs?.boost_clock || 'Unknown';
    let raw = boost;

    // Simulate ProductsPage.jsx validation logic (Global Scope simulation)
    if (boost !== 'Unknown') {
        if (boost.length > 15 || !boost.match(/\d/)) {
            boost = 'Unknown';
        }
    }

    // Checking if it looks like a frequency
    // ... logic from ProductsPage ...
    
    // Fallback Map Simulation (Partial)
    // In the real app, we have a huge map. Here I just want to see what strict validation leaves behind.
    // If it returns 'Unknown', the app would fallback to the Map.
    // If it returns a Value, the app USES that Value.
    // I need to know which Values are "Wrongly Classed" (e.g. Base Clock).

    return { title: p.title, boost: boost, raw: raw };
};

console.log("--- BOOST CLOCK SCAN ---");
const buckets = { "Valid": [], "Unknown (Will use Map)": [], "Garbage (Should be Unknown)": [] };

products.forEach(p => {
    const res = processProduct(p);
    if (res.boost === 'Unknown') {
        buckets["Unknown (Will use Map)"].push(`${res.title} (Raw: "${res.raw.substring(0,30)}...")`);
    } else {
        // Simple heuristic for "Is this reasonable?"
        // Boost clocks are usually 1000 - 3000.
        const val = parseInt(res.boost.match(/\d+/)[0]);
        if (val < 1000 || val > 3000) {
             buckets["Garbage (Should be Unknown)"].push(`${res.title} -> ${res.boost} (Raw: "${res.raw}")`);
        } else {
             buckets["Valid"].push(`${res.title} -> ${res.boost}`);
        }
    }
});

console.log(`\n=== VALID EXTRACTED (${buckets["Valid"].length}) ===`);
buckets["Valid"].forEach(s => console.log(s));

console.log(`\n=== SUSPICIOUS / OUT OF RANGE (<1000 or >3000) (${buckets["Garbage (Should be Unknown)"].length}) ===`);
buckets["Garbage (Should be Unknown)"].forEach(s => console.log(s));

console.log(`\n=== UNKNOWN (Sent to Map) (${buckets["Unknown (Will use Map)"].length}) ===`);
// Sample only 10 to save space
buckets["Unknown (Will use Map)"].slice(0, 10).forEach(s => console.log(s));
