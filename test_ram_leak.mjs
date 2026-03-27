import fs from 'fs';
import { MASTER_DATA } from './frontend/src/data/masterData.js';
import { normalizeProductData } from './frontend/src/utils/productUtils.js';

const normalized = normalizeProductData(MASTER_DATA);

console.log("=== ITEMS IN RAM CATEGORY ===");
const rams = normalized.filter(p => (p.specs && p.specs.category === 'ram') || p.category === 'ram');

console.log(`Found ${rams.length} items grouped as RAM.`);
rams.forEach(p => {
    // Only print if it looks suspicious (not ADATA, PNY, etc, or if it mentions PC or Laptop)
    const t = p.title.toLowerCase();
    
    // Check if it's potentially a computer
    if (t.includes('ordinateur') || t.includes('pc ') || t.includes('laptop') || t.includes('ideapad') || t.includes('macbook') || t.includes('desktop') || t.includes('gamer')) {
        // Exclude safe words "PC Portable" if it's a "Barrette"
        if (!(t.includes('barrette') && t.includes('pc portable'))) {
             console.log(`[SUSPICIOUS] - ${p.title} | Source: ${p.source} | Raw Cat: ${p.category}`);
        }
    }
});
