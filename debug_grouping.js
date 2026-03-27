
const generateVariantKey = (title) => {
    let t = (title || "Unknown Product").toString().toUpperCase();
    
    // 0. Remove Common Prefixes/Types (Noise)
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

    // 0.5. Remove Split RAM (e.g. 2 + 2Go) - catch this BEFORE standard RAM
    t = t.replace(/(?:^|[\s/])\d+\s?\+\s?\d+\s?(GO|GB|G)\b/g, ' '); 

    // 1. Remove standardized RAM patterns
    // Use (?:^|[\s/]) to match " /16Go" or " 16Go"
    t = t.replace(/(?:^|[\s/])(\d{1,3})\s?(GO|GB|G)\b/g, ' '); 

    // 2. Remove standardized Storage patterns
    t = t.replace(/(?:^|[\s/])(\d{3,4})\s?(GO|GB|G)\b/g, ' '); 
    t = t.replace(/(?:^|[\s/])(\d)\s?(TO|TB|T)\b/g, ' '); 
    
    t = t.replace(/\sSSD\b/g, ' ');
    t = t.replace(/\sHDD\b/g, ' ');
    t = t.replace(/\sNVME\b/g, ' ');
    
    // 3. Remove DDR mentions
    t = t.replace(/\sDDR\d\b/g, ' ');
    
    // 4. Remove CPU Info & Generations
    const cpuKeywords = [
        "INTEL", "AMD", "RYZEN", "ATHLON", "CELERON", "PENTIUM", 
        "CORE", "ULTRA", "I9", "I7", "I5", "I3", "PROCESSOR",
        "N4500", "N100", "N200", 
        "1315U", "10300H" 
    ];
    const cpuRegex = new RegExp(`\\b(${cpuKeywords.join('|')})\\b`, 'g');
    t = t.replace(cpuRegex, ' ');
    
    t = t.replace(/\d{1,2}(ÈME|È|TH)?\s?(GÉN|GEN|GENERATION|ÉN)/g, ' ');

    // 5. Remove Promotional Text (Robust)
    t = t.replace(/\s(AVEC|\+|PLUS)\s.*?(OFFERTE?|GRATUITE?|INCLUSE?)/g, ' ');
    t = t.replace(/\s(SACOCHE|SAC|SOURIS|CASQUE).*?(OFFERTE?|GRATUITE?|INCLUSE?)/g, ' ');
    
    // 6. COLORS (Expanded)
    const colors = [
        "NOIR", "BLACK", 
        "GRIS", "GREY", "GRAY", "SIDEROL", "SIDERAL", "SIDÉRAL", "SIDERALE", 
        "ARGENT", "SILVER", 
        "BLANC", "WHITE", 
        "BLEU", "BLUE", "CIEL", "NUIT", "SKY", "AZUR",
        "ROUGE", "RED", 
        "GOLD", "OR", "JAUNE", "YELLOW",
        "MIDNIGHT", "STARLIGHT", "LUMIÈRE STELLAIRE",
        "MINUIT", "COSMOS", "ECLIPSE", "PLATINUM", "TITAN",
        "VERT", "GREEN", "ROSE", "PINK", "PURPLE", "VIOLET",
        "FONCÉ", "FONCE", "CLAIR", "DARK", "LIGHT", "MATTE", "DEEP", "SHINY", "METALLIC"
    ];
    
    // Use \W bounds instead of \b to handle accents (e.g. FONCÉ) and separators (e.g. (Noir))
    const colorRegex = new RegExp(`(?:^|[\\s\\W])(${colors.join('|')})(?:$|[\\s\\W])`, 'g');
    
    // LOOP REPLACE
    let oldT = "";
    while (t !== oldT) {
        oldT = t;
        t = t.replace(colorRegex, ' ');
    }

    // 7. Cleanup Separators and Junk
    t = t.replace(/("|'|\-|_|\/|\\|\(|\)|\[|\]|\.|,|\|)/g, ' '); 
    t = t.replace(/\s+/g, ' ').trim();
    
    return t;
};

const titles = [
    "Smartphone LESIA YOUNG 3  2+2 Go 32Go - Rose",
    "Smartphone LESIA YOUNG 3  2+2 Go 32Go - Sky blue"
];

titles.forEach(t => {
    console.log(`Original: "${t}"`);
    console.log(`Key     : "${generateVariantKey(t)}"`);
    console.log("-".repeat(20));
});
