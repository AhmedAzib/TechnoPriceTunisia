
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Mock browser environment variables if needed
const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Import the ACTUAL logic
import { normalizeSpecs, normalizeBrand } from './frontend/src/utils/productUtils.js';

const FILES = [
    './frontend/src/data/tunisianet_clean.json',
    './frontend/src/data/spacenet_products.json',
    './frontend/src/data/mytek_test.json',
    './frontend/src/data/wiki_clean.json'
];

console.log("=== VERIFYING CATEGORY CLASSIFICATION ===");

let totalProducts = 0;
let unknownCats = 0;
let catCounts = {};
let unknownExamples = [];

FILES.forEach(filePath => {
    const fullPath = path.join(__dirname, filePath);
    if (fs.existsSync(fullPath)) {
        console.log(`Loading ${filePath}...`);
        const data = JSON.parse(fs.readFileSync(fullPath, 'utf8'));
        
        data.forEach(p => {
            totalProducts++;
            const title = p.name || p.title || "";
            // Need to persist previous normalization steps (Brand/GPU) for Category logic to work best
            // So we start with raw then apply all
            let specs = { ...p.specs };
            const brand = normalizeBrand(p.brand, title);
            
            // PRE-FILL specs with normalized GPU if needed by category logic
            // But normalizeSpecs calls standardizers internally?
            // Wait, normalizeSpecs *calls* the logic I just added.
            // But inside normalizeSpecs, I used (specs.gpu || "") which might be raw.
            // However, GPU is normalized *before* Category in the function?
            // Let's check... I inserted Category logic AFTER GPU logic in productUtils.js.
            // So specs.gpu will be the CLEAN one (e.g. "RTX 3050").
            
            // Run normalization
            normalizeSpecs(title, specs, brand, p.category);
            
            const cat = specs.category;
            
            catCounts[cat] = (catCounts[cat] || 0) + 1;
            
            if (!cat || cat === 'Unknown') {
                unknownCats++;
                if (unknownExamples.length < 50) {
                    unknownExamples.push({ title, result: cat });
                }
            }
        });
    } else {
        console.warn(`File not found: ${fullPath}`);
    }
});

console.log("-".repeat(30));
console.log(`Total Products: ${totalProducts}`);
console.log(`Unknown Categories: ${unknownCats} (${((unknownCats/totalProducts)*100).toFixed(2)}%)`);
console.log("-".repeat(30));
console.log("Category Distribution:");
Object.entries(catCounts)
    .sort(([,a], [,b]) => b - a)
    .forEach(([c, count]) => console.log(`${c}: ${count}`));

if (unknownCats > 0) {
    console.log("-".repeat(30));
    console.log("Top 50 Remaining Unknowns:");
    unknownExamples.forEach(ex => {
        console.log(`Title: ${ex.title}`);
    });
}
