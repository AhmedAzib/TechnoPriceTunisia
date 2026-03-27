
const generateVariantKey = (title) => {
    let t = (title || "Unknown Product").toString().toUpperCase();
    
    // ... Simplified standard cleaners ...
    t = t.replace(/HONOR-PLAY10-BLACK/g, ' '); 
    t = t.replace(/HONOR-PLAY\d+[\w-]*/g, ' ');
    t = t.replace(/BG6M/g, ' '); 
    t = t.replace(/SMARTPHONE/g, ' ');
    t = t.replace(/MOBILE/g, ' ');
    t = t.replace(/TÉLÉPHONE/g, ' ');
    t = t.replace(/TELEPHONE/g, ' ');
    t = t.replace(/GSM/g, ' ');

    t = t.replace(/\b[45]G\b/g, ' ');
    t = t.replace(/(?:^|[\s\(])\d{1,2}\s?[\/]\s?\d{2,4}\s?(?:GO|GB|G)?\b/g, ' ');
    t = t.replace(/(?:^|[\s/\(])\d+\s?\+\s?\d+\s?(GO|GB|G)\b/g, ' '); 
    t = t.replace(/(?:^|[\s/\(])(\d{1,3})\s?(GO|GB|G)\b/g, ' '); 
    t = t.replace(/(?:^|[\s/\(])(\d{3,4})\s?(GO|GB|G)\b/g, ' '); 
    t = t.replace(/(?:^|[\s/\(])(\d)\s?(TO|TB|T)\b/g, ' '); 

    const colors = [
        "NOIR", "BLACK", "TWILIGHT", "GOLD", "IRIS", "BLUE", "TITANIUM", "SILVER", "SEELK", "BLEU"
    ]; 
    const colorRegex = new RegExp(`(?:^|[\\s\\W])(${colors.join('|')})(?:$|[\\s\\W])`, 'g');
    let oldT = "";
    while (t !== oldT) { oldT = t; t = t.replace(colorRegex, ' '); }

    t = t.replace(/("|'|\-|_|\/|\\|\(|\)|\[|\]|\.|,|\||–)/g, ' '); 
    t = t.replace(/\s+/g, ' ').trim();
    t = t.replace(/PLAY(\d)/g, 'PLAY $1');
    
    // THE NEW LOGIC
    const originalTitle = (title || "").toUpperCase();
    if (originalTitle.includes("SMART 10")) {
        const has4GB = /(?:^|[\s/\(])4\s?(?:GO|GB|G)/.test(originalTitle);
        const has128GB = /(?:^|[\s/\(])128\s?(?:GO|GB|G)/.test(originalTitle);
        const has256GB = /(?:^|[\s/\(])256\s?(?:GO|GB|G)/.test(originalTitle);
        
        if (has4GB && has128GB) {
           t += " 4 128";
        } else if (has4GB && has256GB) {
           t += " 4 256";
        }
    }
    
    return t;
};

const titles = [
    "Smartphone INFINIX Smart 10 3/64G - TWILIGHT GOLD",
    "Smartphone INFINIX Smart 10 4Go 128Go - SEELK BLACK",
    "Smartphone INFINIX Smart 10 4Go 256Go - SEELK BLACK"
];

titles.forEach(t => {
    console.log(`Original: "${t}"`);
    console.log(`Key     : "${generateVariantKey(t)}"`);
    console.log("-".repeat(20));
});
