const fs = require('fs');

// --- PROPOSED NEW LOGIC ---
const generateVariantKey = (title) => {
    if (!title) return "UNKNOWN";
    let t = title.toString().toUpperCase();
    
    // 0. Remove Common Prefixes/Types (Noise)
    t = t.replace(/PC PORTABLE/g, ' ');
    t = t.replace(/ORDINATEUR PORTABLE/g, ' ');
    t = t.replace(/LAPTOP/g, ' ');
    t = t.replace(/NOTEBOOK/g, ' ');
    t = t.replace(/GAMER/g, ' ');
    t = t.replace(/GAMING/g, ' ');
    t = t.replace(/ULTRABOOK/g, ' ');

    // 1. Remove standardized RAM patterns
    t = t.replace(/\s(\d{1,3})\s?(GO|GB|G)\b/g, ' '); 

    // 2. Remove standardized Storage patterns
    t = t.replace(/\s(\d{3,4})\s?(GO|GB|G)\b/g, ' '); 
    t = t.replace(/\s(\d)\s?(TO|TB|T)\b/g, ' '); 
    t = t.replace(/\sSSD\b/g, ' ');
    t = t.replace(/\sHDD\b/g, ' ');
    t = t.replace(/\sNVME\b/g, ' ');
    
    // 3. Remove DDR mentions
    t = t.replace(/\sDDR\d\b/g, ' ');
    
    // 4. Remove CPU Info & Generations
    // Handle "11Gén", "12Gen", "13è Gén", "N100" (Specific low-end cpu)
    const cpuKeywords = [
        "INTEL", "AMD", "RYZEN", "ATHLON", "CELERON", "PENTIUM", 
        "CORE", "ULTRA", "I9", "I7", "I5", "I3", "PROCESSOR",
        "N4500", "N100", "N200", // Celerons often part of title
        "1315U", "10300H" // Specific SKUs
    ];
    const cpuRegex = new RegExp(`\\b(${cpuKeywords.join('|')})\\b`, 'g');
    t = t.replace(cpuRegex, ' ');
    
    // Remove "Gen 12", "11ème Gén", "13Gén"
    t = t.replace(/\d{1,2}(ÈME|È|TH)?\s?(GÉN|GEN|GENERATION)/g, ' ');
    
    // 5. Remove Promotional Text (Robust)
    t = t.replace(/\s(AVEC|\+|PLUS)\s.*?(OFFERTE?|GRATUITE?|INCLUSE?)/g, ' ');
    t = t.replace(/\s(SACOCHE|SAC|SOURIS|CASQUE).*?(OFFERTE?|GRATUITE?|INCLUSE?)/g, ' ');
    
    // 6. COLORS (Expanded)
    const colors = [
        "NOIR", "BLACK", 
        "GRIS", "GREY", "GRAY", "SIDEROL", "SIDERAL", "SIDERALE", 
        "ARGENT", "SILVER", 
        "BLANC", "WHITE", 
        "BLEU", "BLUE", "CIEL",
        "ROUGE", "RED", 
        "GOLD", "OR", 
        "MIDNIGHT", "STARLIGHT", "LUMIÈRE STELLAIRE",
        "MINUIT", "COSMOS", "ECLIPSE", "PLATINUM", "TITAN",
        "VERT", "GREEN",
        "ROSE", "PINK"
    ];
    // Regex to remove colors (word boundary essential)
    const colorRegex = new RegExp(`\\b(${colors.join('|')})\\b`, 'g');
    t = t.replace(colorRegex, ' ');

    // 7. Cleanup Separators and Junk
    // Convert all separators to spaces
    t = t.replace(/("|'|\-|_|\/|\\|\(|\)|\[|\]|\.|,)/g, ' '); 
    // Remove specific junk chars like "///" or multiple spaces
    t = t.replace(/\s+/g, ' ').trim();
    
    // 8. Trim Complex Model Codes (Experimental)
    // Wiki/Spacenet attach codes like "MGN63FN/A" or "9S7-17L541-419" or "F13MG-404XFR"
    // Heuristic: Remove words that are >5 chars AND contain both Letters and Numbers
    const words = t.split(' ');
    const cleanWords = words.filter(w => {
        const hasNum = /\d/.test(w);
        const hasLet = /[A-Z]/.test(w);
        // If it looks like a model code (Letters + Numbers) and is "long" or specific format
        // e.g. X1502VA is a model code. We WANT that.
        // But MGN63FN/A is a variant code. 
        // 9S7... is a variant code.
        // It's HARD to distinguish "X1502VA" (Model) from "MGN63FN" (Variant).
        // Usually Model is earlier in string?
        
        // Let's just try matching the failed cases first.
        return true; 
    });
    
    t = cleanWords.join(' ');

    return t;
};

// --- TEST CASES (From Audit) ---
const cases = [
    ["APPLE MACBOOK AIR M1 - GRIS", "APPLE MACBOOK AIR M1 GRIS SIDÉRAL MGN63FN/A"],
    ["APPLE MACBOOK AIR M2 – MIDNIGHT", "APPLE MACBOOK AIR M2 – SILVER"],
    ["APPLE MACBOOK AIR M4 - BLEU CIEL", "APPLE MACBOOK AIR M4 - LUMIÈRE STELLAIRE"],
    ["Pc Portable ASUS Vivobook 15 X1502VA", "PC Portable ASUS Vivobook 15 X1502VA / i5"],
    ["Lenovo IdeaPad Slim 3 15AMN8", "Pc Portable LENOVO IdeaPad Slim 3 15AMN8 / AMD Athlon"],
    ["HP 15 fd0421nk – PC Portable N100 4Go 256Go SSD Noir", "HP 15 FD0421NK – N100"],
    ["Lenovo IP1 15IJL7 – Pc Portable Celeron N4500 8Go 256Go SSD Gris", "LENOVO IP1 15IJL7 – N4500"],
    ["MSI Modern 15 F13MG-404XFR – PC Portable i3-1315U 8 Go 512 Go SSD Gris", "MSI MODERN 15 F13MG 404XFR – 1315U"],
    ["Apple MacBook Air M1 8Go 256 Go Gris sidéral MGN63FN/A", "APPLE MACBOOK AIR M1 - GRIS"],
    ["Pc Portable Gamer Dell 5500 G5 I5-10300H 8Go 1To SSD Noir", "DELL 5500 G5 10300H"],
    ["Pc Portable Dell Latitude 3520 i5 11Gén 8Go 512Go Noir", "DELL LATITUDE 3520 ÉN"],
    ["Pc Portable MSI Gaming Katana i5 12Gén 8Go 512Go SSD RTX 4050 6G (9S7-17L541-419)", "MSI KATANA ÉN RTX 4050 9S7 17L541 419"]
];

console.log("--- TESTING NEW VARIANT KEY LOGIC ---");
cases.forEach((pair, idx) => {
    const k1 = generateVariantKey(pair[0]);
    const k2 = generateVariantKey(pair[1]);
    const match = k1 === k2;
    console.log(`\nCase ${idx + 1}: ${match ? 'MATCH ✅' : 'FAIL ❌'}`);
    console.log(`  Org 1: ${pair[0]}`);
    console.log(`  Key 1: ${k1}`);
    console.log(`  Org 2: ${pair[1]}`);
    console.log(`  Key 2: ${k2}`);
});
