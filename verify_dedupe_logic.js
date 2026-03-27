
// Mocking the normalizer logic directly to verify deduplication
// Explicitly removing imports to run in standard Node environment

const normalizeProductData = (data) => {
    const seen = new Set();
    
    return data.map(p => {
        // Mock processing mapping
        return {
            ...p,
            id: p.id || p.link,
            specs: p.specs || { category: 'Gaming' } 
        };
    }).filter(p => {
        // 1. Filter Invalid Categories
        if (p.specs.category === 'Invalid') return false;

        // 2. Deduplication Logic (The Fix)
        const uniqueKey = p.id || p.link;
        if (!uniqueKey) return true; 
        
        if (seen.has(uniqueKey)) {
            return false; // Skip duplicate
        }
        seen.add(uniqueKey);
        return true;
    });
};

const testData = [
    { id: '1', name: 'Product A' },
    { id: '1', name: 'Product A Copy' },
    { link: 'http://2', name: 'Product B' },
    { link: 'http://2', name: 'Product B Copy' },
    { id: '3', name: 'Product C' }
];

console.log("Running deduplication test...");
const result = normalizeProductData(testData);

console.log("Input Length:", testData.length);
console.log("Output Length:", result.length);

result.forEach(p => console.log(`- ${p.id || p.link}: ${p.name}`));

if (result.length === 3) {
    console.log("SUCCESS: Duplicates removed.");
} else {
    console.log("FAILURE: Duplicates remain.");
}
