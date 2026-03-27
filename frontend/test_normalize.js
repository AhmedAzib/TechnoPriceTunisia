import { normalizeProductData } from './src/utils/productUtils.js';
import fs from 'fs';

const sbsRams = JSON.parse(fs.readFileSync('src/data/sbs_rams.json', 'utf8'));
const mapped = sbsRams.map(p => ({ ...p, source: 'SBS Informatique', category: 'ram' }));

const result = normalizeProductData(mapped);

console.log(`Input length: ${mapped.length}`);
console.log(`Output length: ${result.length}`);

if (result.length < mapped.length) {
    console.log("Some products were filtered out!");
}
if (result.length > 0) {
    console.log("First normalized product:", result[0]);
}

