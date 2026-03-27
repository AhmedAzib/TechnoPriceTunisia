const fs = require('fs');
const path = require('path');

// Mock data loading
const loadJSON = (file) => JSON.parse(fs.readFileSync(path.join(__dirname, 'frontend/src/data', file), 'utf8'));

const tunisianetData = loadJSON('tunisianet_clean.json');
const spacenetData = loadJSON('spacenet_products.json');
const mytekData = loadJSON('mytek_test.json');
const wikiData = loadJSON('wiki_clean.json');

const MASTER_DATA = [
  ...tunisianetData.map(p => ({ ...p, source: 'Tunisianet' })), 
  ...spacenetData.filter(p => {
        const t = (p.title || p.name || "").toLowerCase();
        return !t.includes('asus vivobook 15 x515ka') && 
               !t.includes('lenovo ideapad 1') &&
               !t.includes('hp 15-fd0421nk');
    }).map(p => ({ ...p, source: 'Spacenet' })),
  ...mytekData.map((p, index) => ({
      ...p,
      id: `MK-${index}`,
      source: 'MyTek'
  })),
  ...wikiData.map(p => ({ ...p, source: 'Wiki' }))
];

// Mock Normalization (Simplified from productUtils.js)
const normalizeProductData = (data) => {
    return data.map(p => {
        return {
            ...p,
            // We want to verify if 'source' persists
        };
    });
};

const normalized = normalizeProductData(MASTER_DATA);

// Analysis
const sources = {};
normalized.forEach(p => {
    const s = p.source;
    sources[s] = (sources[s] || 0) + 1;
});

console.log("Counts by Source:");
console.log(sources);

// Check for undefined source
const missingSource = normalized.filter(p => !p.source);
console.log("Missing Source Count:", missingSource.length);
if (missingSource.length > 0) {
    console.log("Sample missing source:", missingSource[0]);
}

// Check sample MyTek Item
const mytekItem = normalized.find(p => p.source === 'MyTek');
if(mytekItem) {
    console.log("Sample MyTek Source:", mytekItem.source);
} else {
    console.log("NO MyTek items found!");
}
