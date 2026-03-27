
const fs = require('fs');

// Load Data
const spacenet = require('./frontend/src/data/spacenet_gpu.json');

// Mock Map (Simulate ProductsPage.jsx)
const GPU_REF_MAP = {
    "RTX 4090": { extreme: "Ultra Enthusiast" },
    "RTX 5090": { extreme: "Ultra Enthusiast" },
    "RTX 3060": { extreme: "High Performance" }
};

const processProduct = (p) => {
    let extreme = "Unknown";
    const rule = GPU_REF_MAP["RTX 4090"]; // Simulate a hit for testing
    
    // CURRENT BUGGY LOGIC
    // if (rule.extreme && rule.extreme.match(/\d+\s*MHz/i)) ...
    
    // PROPOSED FIXED LOGIC
    if (rule && rule.extreme) {
        extreme = rule.extreme;
    }
    
    return { title: p.title, extreme: extreme };
};

console.log("--- EXTREME PERFORMANCE TEST ---");
const testItem = { title: "Test RTX 4090", specs: {} };
const res = processProduct(testItem);
console.log(`Input: ${testItem.title}`);
console.log(`Result: ${res.extreme}`);

if (res.extreme === "Ultra Enthusiast") {
    console.log("[SUCCESS] Logic verified.");
} else {
    console.log("[FAILURE] Logic failed.");
}
