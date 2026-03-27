
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Mock browser environment variables if needed
const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Import the ACTUAL logic
// We might need to adjust the path if productUtils imports other things, 
// but currently it looks standalone.
import { normalizeSpecs } from './frontend/src/utils/productUtils.js';

const FILES = [
    './frontend/src/data/tunisianet_clean.json',
    './frontend/src/data/spacenet_products.json',
    './frontend/src/data/mytek_test.json',
    './frontend/src/data/wiki_clean.json'
];

console.log("=== VERIFYING GPU CLASSIFICATION ===");

let totalProducts = 0;
let unknownGPUs = 0;
let gpuCounts = {};
let unknownExamples = [];

FILES.forEach(filePath => {
    const fullPath = path.join(__dirname, filePath);
    if (fs.existsSync(fullPath)) {
        console.log(`Loading ${filePath}...`);
        const data = JSON.parse(fs.readFileSync(fullPath, 'utf8'));
        
        data.forEach(p => {
            totalProducts++;
            const title = p.name || p.title || "";
            const specs = p.specs || {};
            const brand = p.brand || "Unknown"; // Mock brand if needed
            
            // WE MUST CLONE specs to avoid mutating original data in memory if we were saving
            // checking logic only.
            const specsCopy = { ...specs };
            
            // Run normalization
            normalizeSpecs(title, specsCopy, brand);
            
            const gpu = specsCopy.gpu;
            
            gpuCounts[gpu] = (gpuCounts[gpu] || 0) + 1;
            
            if (!gpu || gpu === 'Unknown' || gpu === 'Integrated' || gpu === "INTEGRATED") {
                unknownGPUs++;
                if (unknownExamples.length < 50) {
                    unknownExamples.push({ title, raw: specs.gpu, result: gpu });
                }
            }
        });
    } else {
        console.warn(`File not found: ${fullPath}`);
    }
});

console.log("-".repeat(30));
console.log(`Total Products: ${totalProducts}`);
console.log(`Unknown GPUs: ${unknownGPUs} (${((unknownGPUs/totalProducts)*100).toFixed(2)}%)`);
console.log("-".repeat(30));
console.log("Top 20 GPU Classifications:");
Object.entries(gpuCounts)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 20)
    .forEach(([gpu, count]) => console.log(`${gpu}: ${count}`));

if (unknownGPUs > 0) {
    console.log("-".repeat(30));
    console.log("Top 50 Remaining Unknowns:");
    unknownExamples.forEach(ex => {
        console.log(`[${ex.result}] Title: ${ex.title} (Raw: ${ex.raw})`);
    });
}
