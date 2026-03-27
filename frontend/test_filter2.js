import { normalizeProductData } from './src/utils/productUtils.js';
import fs from 'fs';

let sbsRams = JSON.parse(fs.readFileSync('src/data/sbs_rams.json', 'utf8'));
sbsRams = sbsRams.map(p => ({ ...p, source: 'SBS Informatique', category: 'ram' }));

// Instead of relying on the exported function which filters, let's just log what filter would see
const p = sbsRams[0];

// The filter is:
// p => (p.source === 'TechSpace' || p.source === 'TunisiaTech') || (p.specs.category !== 'Invalid' && p.price >= 0 && p.specs.valid !== false && p.title.toUpperCase() !== "PROCESSEUR" && !p.title.toUpperCase().includes("J4025M"))
// Let's run normalizeProductData but mock the filter

const origFilter = Array.prototype.filter;
Array.prototype.filter = function(cb) {
    if (this.length > 0 && this[0] && this[0].id === 'sbs-ram-0') {
         console.log('--- SBS RAM 0 At Filter Stage ---');
         console.log('Source:', this[0].source);
         console.log('Specs Category:', this[0].specs?.category);
         console.log('Price:', this[0].price);
         console.log('Specs Valid:', this[0].specs?.valid);
         console.log('Title:', this[0].title);
         
         const passes = (this[0].source === 'TechSpace' || this[0].source === 'TunisiaTech') || 
                       (this[0].specs?.category !== 'Invalid' && 
                        this[0].price >= 0 && 
                        this[0].specs?.valid !== false && 
                        this[0].title.toUpperCase() !== "PROCESSEUR" && 
                        !this[0].title.toUpperCase().includes("J4025M"));
         console.log('Would pass filter:', passes);
    }
    return origFilter.call(this, cb);
};

const result = normalizeProductData(sbsRams);

console.log('Final length:', result.length);
