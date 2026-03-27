
const generateVariantKey = (product) => {
    let t = (product.title || product.name || "Unknown Product").toString().toUpperCase();
    
    // Simulate main cleaning (skipping all the heavy regex for brevity, assuming they work as 't' ends up as "INFINIX SMART 10")
    // But wait, if 't' cleaning fails, the key is wrong.
    // The user says specs are wrong, implying key maps to wrong override or default inferred specs.
    // If key was "INFINIX SMART 10 4 128", it would map to the 4GB override.
    // Since it maps to 3GB override, key must be "INFINIX SMART 10".
    
    // So let's simulate 't' being cleaned to "INFINIX SMART 10"
    t = "INFINIX SMART 10"; 

    // 9. Special Suffixing for Split Models (e.g. Infinix Smart 10 4GB vs 3GB)
    const originalTitle = (product.title || product.name || "").toUpperCase();
    
    console.log(`Checking Original: "${originalTitle}"`);
    
    if (originalTitle.includes("SMART 10")) {
        // Regex exactly as in file
        const has4GB = /(?:^|[\s/\(])4\s?(?:GO|GB|G)/.test(originalTitle);
        const has128GB = /(?:^|[\s/\(])128\s?(?:GO|GB|G)/.test(originalTitle);
        const has256GB = /(?:^|[\s/\(])256\s?(?:GO|GB|G)/.test(originalTitle);
        
        console.log(`Has 4GB: ${has4GB}`);
        console.log(`Has 128GB: ${has128GB}`);
        console.log(`Has 256GB: ${has256GB}`);
        
        if (has4GB && has128GB) {
           t += " 4 128";
        } else if (has4GB && has256GB) {
           t += " 4 256";
        }
    }
    
    return t;
};

const products = [
    { title: "Smartphone INFINIX Smart 10 4Go 128Go - SEELK BLACK" },
    { title: "Smartphone INFINIX Smart 10 4Go 256Go - SEELK BLACK" },
    { name: "Infinix Smart 10 4Go 128Go Titanium Silver" } // Test 'name' prop
];

products.forEach(p => {
    console.log(`Product:`, p);
    console.log(`Key     : "${generateVariantKey(p)}"`);
    console.log("-".repeat(20));
});
