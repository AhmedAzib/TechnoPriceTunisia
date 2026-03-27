import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Mock Data Loading (Load a sample of data)
const dataDir = "c:\\Users\\USER\\Documents\\programmation\\frontend\\src\\data";
let allProducts = [];

const files = fs.readdirSync(dataDir).filter(f => f.endsWith('_mobiles.json'));
files.forEach(f => {
    try {
        const content = fs.readFileSync(path.join(dataDir, f), 'utf8');
        const json = JSON.parse(content);
        allProducts = allProducts.concat(json);
    } catch (e) {}
});

console.log(`Loaded ${allProducts.length} products.`);

// Replicate Logic from MobilesPage.jsx
const normalized = allProducts.map(p => {
    let specs = { ...p.specs } || {};
    
    // --- COPY PASTE LOGIC START ---
    
    // 2. Infer others if Unknown
    // Force Helio for known models (Override "Octa Core" or generic values)
    const tLower = (p.title || "").toLowerCase();
    const isHelioModel = (
        // Samsung
        (tLower.includes('galaxy a05') || tLower.includes('galaxy a06') || (tLower.includes('galaxy a15') && !tLower.includes('5g')) || (tLower.includes('galaxy a16') && !tLower.includes('5g'))) ||
        // Xiaomi
        (tLower.includes('redmi 13c') || tLower.includes('redmi 12c') || tLower.includes('redmi 12 ') || tLower.includes('redmi a3') || tLower.includes('redmi a2')) ||
        // Infinix / Tecno (4G)
        ((tLower.includes('hot 40') || tLower.includes('hot 30') || tLower.includes('spark 20') || tLower.includes('spark 10') || tLower.includes('camon 20') || tLower.includes('note 30')) && !tLower.includes('5g'))
    );

    if (isHelioModel && specs.cpu !== "MediaTek Helio") {
         specs.cpu = "MediaTek Helio";
    }

    // Also normalize existing "Helio" text
    if (specs.cpu && specs.cpu.toLowerCase().includes('helio') && specs.cpu !== "MediaTek Helio") {
        specs.cpu = "MediaTek Helio";
    }
    
    // --- COPY PASTE LOGIC END ---
    
    return { title: p.title, cpu: specs.cpu };
});

const counts = {};
normalized.forEach(p => {
    const c = p.cpu || 'Unknown';
    counts[c] = (counts[c] || 0) + 1;
});

console.log("\nCPU COUNTS:");
Object.keys(counts).sort((a,b) => counts[b] - counts[a]).forEach(k => {
    if (counts[k] > 5) console.log(`${k}: ${counts[k]}`);
});

console.log("\nChecking Specific Models:");
const check = ["Samsung Galaxy A05", "Xiaomi Redmi 13C", "Infinix Hot 40"];
check.forEach(m => {
    const found = normalized.find(p => p.title.includes(m));
    if(found) console.log(`${m} -> ${found.cpu}`);
    else console.log(`${m} -> Not Found`);
});
