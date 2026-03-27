import { normalizeProductData } from './src/utils/productUtils.js';
import fs from 'fs';

let sbsRams = JSON.parse(fs.readFileSync('src/data/sbs_rams.json', 'utf8'));
sbsRams = sbsRams.map(p => ({ ...p, source: 'SBS Informatique', category: 'ram' }));

// Set up proxy on the first item's specs
const p = sbsRams[0];
p.specs = new Proxy(p.specs, {
    set(target, prop, value) {
        if (prop === 'valid' && value === false) {
             console.log('--- TRACE: specs.valid set to false ---');
             console.log(new Error().stack);
        }
        target[prop] = value;
        return true;
    }
});

normalizeProductData([p]);

