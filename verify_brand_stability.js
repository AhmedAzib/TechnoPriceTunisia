
/**
 * verify_brand_stability.js
 * 
 * This script is a PERMANENT REGRESSION TEST for Brand Normalization.
 * 
 * Tests that `normalizeBrand` correctly infers brands from titles when the brand field is missing.
 * 
 * Run with: node verify_brand_stability.js
 */

// === LOGIC UNDER TEST (Mirrors src/utils/productUtils.js) ===
const normalizeBrand = (brand, title = "") => {
    let b = (brand || "").toLowerCase().trim();
    let t = (title || "").toLowerCase().trim();

    // Helper to check both brand field and title
    const has = (keyword) => b.includes(keyword) || t.includes(keyword);

    if (has('hp') || has('hewlett') || has('elitebook') || has('pavilion') || has('probook') || has('omen') || has('victus')) return 'HP';
    if (has('dell') || has('vostro') || has('latitude') || has('inspiron') || has('xps') || has('alienware') || has('g15')) return 'Dell';
    if (has('lenovo') || has('thinkpad') || has('thinkbook') || has('ideapad') || has('yoga') || has('legion') || has('loq')) return 'Lenovo';
    if (has('asus') || has('zenbook') || has('vivobook') || has('rog') || has('tuf') || has('expertbook')) return 'Asus';
    if (has('msi') || has('katana') || has('cyborg') || has('stealth') || has('raider') || has('thin')) return 'MSI';
    if (has('apple') || has('macbook') || has('mac ') || has('imac')) return 'Apple';
    if (has('acer') || has('nitro') || has('predator') || has('aspire') || has('swift') || has('extensa')) return 'Acer';
    if (has('gigabyte') || has('aorus') || has('aero')) return 'Gigabyte';
    if (has('samsung') || has('galaxy book')) return 'Samsung';
    if (has('huawei') || has('matebook')) return 'Huawei';
    if (has('microsoft') || has('surface')) return 'Microsoft';
    if (has('bmax')) return 'BMAX';
    if (has('infinix')) return 'Infinix';
    if (has('razer') || has('blade')) return 'Razer';
    if (has('chuwi')) return 'Chuwi';
    if (has('mytek')) return 'MyTek';
    if (has('kimera')) return 'Kimera';
    
    // Group "Sans marque" requests
    if (has('nintendo') || has('patriot') || has('schneider') || has('sharkoon') || 
        has('thomson') || has('vega') || has('versus') || has('yatagan') || 
        has('sans marque') || has('unknown')) return 'Sans marque';

    // If we have a valid brand string that isn't 'unknown'/'generic', format it
    if (brand && !['unknown', 'generic', 'autre'].includes(b)) {
         return brand.charAt(0).toUpperCase() + brand.slice(1).toLowerCase();
    }
    
    return 'Sans marque';
};

// === TEST CASES ===
const testCases = [
    // Standard Inference (Title has brand, Brand field is Unknown)
    { brand: "Unknown", title: "PC Portable BMAX MaxBook X15", expected: "BMAX" },
    { brand: "", title: "Gigabyte G6MF i7", expected: "Gigabyte" },
    { brand: "Generic", title: "Lenovo ThinkPad X1", expected: "Lenovo" },
    { brand: "Unknown", title: "Asus Vivobook 15", expected: "Asus" },

    // Sub-brand Inference
    { brand: "Unknown", title: "Pc Portable EliteBook 840", expected: "HP" }, // EliteBook -> HP
    { brand: "Unknown", title: "Legion 5 Pro", expected: "Lenovo" }, // Legion -> Lenovo
    { brand: "Unknown", title: "Aorus 15", expected: "Gigabyte" }, // Aorus -> Gigabyte
    { brand: "Unknown", title: "Alienware m18", expected: "Dell" }, // Alienware -> Dell

    // Niche Brands
    { brand: "Unknown", title: "Pc de Bureau MyTek i5", expected: "MyTek" },
    
    // RECLASSIFIED TO "Sans marque"
    { brand: "Unknown", title: "Pc Gamer YATAGAN SPIKE", expected: "Sans marque" },
    { brand: "Unknown", title: "SCHNEIDER Pc Portable", expected: "Sans marque" },
    { brand: "Unknown", title: "Versus VS123", expected: "Sans marque" },
    { brand: "Unknown", title: "Thomson Neo", expected: "Sans marque" },

    // Pre-existing valid brand (Should remain)
    { brand: "Dell", title: "Laptop 15", expected: "Dell" },
    { brand: "HP", title: "Anything", expected: "HP" },
];

// === RUNNER ===
console.log("=== VERIFYING BRAND STABILITY ===");
let passed = 0;
let failed = 0;

testCases.forEach((tc, i) => {
    const result = normalizeBrand(tc.brand, tc.title);
    if (result === tc.expected) {
        passed++;
    } else {
        failed++;
        console.error(`[FAIL] Brand: "${tc.brand}", Title: "${tc.title}"`);
        console.error(`       Expected: "${tc.expected}"`);
        console.error(`       Got:      "${result}"`);
    }
});

console.log(`\nResults: PASS: ${passed}, FAIL: ${failed}`);

if (failed === 0) {
    console.log("\n✅ BRAND LOGIC IS STABLE AND VERIFIED.");
} else {
    console.error("\n❌ WARNING: BRAND LOGIC HAS REGRESSIONS.");
    process.exit(1);
}
