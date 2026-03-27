
const generateVariantKey = (title) => {
    let t = (title || "Unknown Product").toString().toUpperCase();
    
    // 0. Remove Common Prefixes/Types (Noise)
    t = t.replace(/HONOR-PLAY10-BLACK/g, ' '); 
    t = t.replace(/HONOR-PLAY\d+[\w-]*/g, ' '); 
    t = t.replace(/BG6M/g, ' '); 
    t = t.replace(/SMARTPHONE/g, ' ');
    t = t.replace(/MOBILE/g, ' ');
    t = t.replace(/TÉLÉPHONE/g, ' ');
    t = t.replace(/TELEPHONE/g, ' ');
    t = t.replace(/GSM/g, ' ');
    t = t.replace(/PC PORTABLE/g, ' ');
    t = t.replace(/ORDINATEUR PORTABLE/g, ' ');
    t = t.replace(/LAPTOP/g, ' ');
    t = t.replace(/NOTEBOOK/g, ' ');
    t = t.replace(/GAMER/g, ' ');
    t = t.replace(/GAMING/g, ' ');
    t = t.replace(/ULTRABOOK/g, ' ');

    // 0.2. Remove Network
    t = t.replace(/\b[45]G\b/g, ' ');

    // 0.5. Remove Split RAM 
    t = t.replace(/(?:^|[\s/\(])\d+\s?\+\s?\d+\s?(GO|GB|G)\b/g, ' '); 

    // 1. Remove standardized RAM patterns
    t = t.replace(/(?:^|[\s/\(])(\d{1,3})\s?(GO|GB|G)\b/g, ' '); 

    // 2. Remove standardized Storage patterns
    t = t.replace(/(?:^|[\s/\(])(\d{3,4})\s?(GO|GB|G)\b/g, ' '); 
    t = t.replace(/(?:^|[\s/\(])(\d)\s?(TO|TB|T)\b/g, ' '); 
    
    // ... skipping middle ...

    // 6. COLORS (Expanded)
    const colors = [
        "NOIR", "BLACK", "TWILIGHT", "GOLD", "IRIS", "BLUE", "TITANIUM", "SILVER", "SEELK"
    ]; // Simplified list
    
    const colorRegex = new RegExp(`(?:^|[\\s\\W])(${colors.join('|')})(?:$|[\\s\\W])`, 'g');
    
    let oldT = "";
    while (t !== oldT) {
        oldT = t;
        t = t.replace(colorRegex, ' ');
    }

    // 7. Cleanup Separators - Including EN-DASH
    t = t.replace(/("|'|\-|_|\/|\\|\(|\)|\[|\]|\.|,|\||–)/g, ' '); 
    t = t.replace(/\s+/g, ' ').trim();
    
    // 8. Normalization
    t = t.replace(/PLAY(\d)/g, 'PLAY $1');

    return t;
};

const titles = [
    "Smartphone INFINIX Smart 10 3/64G - TWILIGHT GOLD",
    "Smartphone INFINIX Smart 10 3Go 64Go - IRIS BLUE",
    "Smartphone INFINIX Smart 10 3Go 64Go - TITANIUM SILVER",
    "Smartphone INFINIX Smart 10 3Go 64Go - SEELK BLACK",
    "Smartphone Infinix SMART 10 4G / 3 Go / 64 Go / Noir"
];

titles.forEach(t => {
    console.log(`Original: "${t}"`);
    console.log(`Key     : "${generateVariantKey(t)}"`);
    console.log("-".repeat(20));
});
