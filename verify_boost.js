
const fs = require('fs');

// Load Data
const spacenet = require('./frontend/src/data/spacenet_gpu.json');
const products = [...spacenet]; 

const processProduct = (p) => {
    let boost = p.specs?.boost_clock || 'Unknown';
    let cleanBoost = "Unknown";

    // Simulate ProductsPage.jsx NEW Logic
    
    // 1. Validation Logic
    if (boost !== "Unknown") {
         if (boost.length > 15 || !boost.match(/\d/)) {
              boost = "Unknown";
         }
    }
    
    // 2. Map Fallback (Simulated)
    const map = { "RX 7600": "2755 MHz" };
    if (boost === "Unknown") {
        if (p.title.includes("RX 7600")) {
            boost = map["RX 7600"];
        }
    }

    if (boost !== "Unknown") {
        if (!boost.toLowerCase().includes('mhz')) {
             boost += ' MHz';
        }
    }
    
    return { title: p.title, boost: boost };
};

const targetTitle = "Carte Graphique Gigabyte AMD Radeon RX 7600 Gaming OC 8Go GDDR6";

console.log("--- FINDING TARGET ---");
const found = products.find(p => p.title === targetTitle);

if (found) {
    const res = processProduct(found);
    console.log(`Title: ${res.title}`);
    console.log(`Extracted Boost: ${res.boost}`);
} else {
    console.log("Target not found!");
}
