import fs from 'fs';

// Read sbs_rams.json
const sbsRams = JSON.parse(fs.readFileSync('src/data/sbs_rams.json', 'utf8'));

// Format like masterData.js does
const mappedSbsRams = sbsRams.map(p => ({ ...p, source: 'SBS Informatique', category: 'ram' }));

console.log(`Total SBS RAMs before normalizer: ${mappedSbsRams.length}`);

// Let's do a basic mock of what normalizeProductData does to see if it throws or filters
let validCount = 0;
let invalidReasons = {};

mappedSbsRams.forEach(p => {
    let isValid = true;
    let title = (p.title || "").toLowerCase();
    
    // Check if it has a price
    if (!p.price || p.price === 0) {
        isValid = false;
        invalidReasons['no_price'] = (invalidReasons['no_price'] || 0) + 1;
    }
    
    if (isValid) validCount++;
});

console.log(`Total valid: ${validCount}`);
console.log(`Reasons for invalid:`, invalidReasons);

