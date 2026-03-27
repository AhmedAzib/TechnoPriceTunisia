const fs = require('fs');

const mytekRams = JSON.parse(fs.readFileSync('./frontend/src/data/mytek_rams.json', 'utf-8'));
const { normalizeProductData } = require('./frontend/src/utils/productUtils.js');

const normalized = normalizeProductData(mytekRams);

console.log("RAM CATEGORY TEST");
normalized.forEach(r => {
    console.log(`Title: ${r.title}`);
    console.log(`Category: ${r.category}`);
    console.log(`Specs Category: ${r.specs ? r.specs.category : 'N/A'}`);
    console.log("---");
});
