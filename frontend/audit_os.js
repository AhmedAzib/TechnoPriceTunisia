import fs from 'fs';

// Load Data
const tunisianet = JSON.parse(fs.readFileSync('src/data/tunisianet_clean.json', 'utf8'));
const spacenet = JSON.parse(fs.readFileSync('src/data/spacenet_products.json', 'utf8'));
const mytek = JSON.parse(fs.readFileSync('src/data/mytek_test.json', 'utf8'));
const wiki = JSON.parse(fs.readFileSync('src/data/wiki_clean.json', 'utf8'));

const allData = [
    ...tunisianet.map(p => ({...p, source: 'Tunisianet'})),
    ...spacenet.map(p => ({...p, source: 'Spacenet'})),
    ...mytek.map(p => ({...p, source: 'MyTek', specs: p.specs || {} })), 
    ...wiki.map(p => ({...p, source: 'Wiki'}))
];

const normalizeOS = (p) => {
    const tOS = p.title.toUpperCase().replace(/\s+/g, ' ');
    let pOS = (p.specs && p.specs.system) ? p.specs.system.toString().toUpperCase() : "";
    
    let bucket = "FreeDOS"; 

    // 1. Explicit Windows
    let isWindows = 
        pOS.includes("WINDOWS") || 
        tOS.includes("WINDOWS") || 
        tOS.match(/\bWIN\s?1[01]/) || 
        tOS.match(/\bW1[01]\b/) ||    
        tOS.includes("WIN 10") || 
        tOS.includes("WIN 11");

    // 2. Business Line Inference (Tier A)
    // Only if NOT explicitly No-OS
    const noOsKeywords = ["FREEDOS", "UKNOWN", "SANS", "UBUNTU", "LINUX", "BOOT-UP", "DOS"];
    const isExplicitlyFree = noOsKeywords.some(k => tOS.includes(k));

    if (!isWindows && !isExplicitlyFree) {
        // High Confidence Windows Models
        const tierA = [
            "ELITEBOOK", "LATITUDE", "PRECISION", "ZBOOK", "XPS", 
            "SURFACE", "THINKPAD X", "THINKPAD T", "THINKPAD P", "THINKPAD Z", 
            "EXPERTBOOK B5", "EXPERTBOOK B7", "EXPERTBOOK B9", 
            "ZENBOOK PRO"
        ];
        
        // Exclude Mac
        if (!tOS.includes("MACBOOK") && !tOS.includes("IMAC") && !tOS.includes("APPLE")) {
             if (tierA.some(k => tOS.includes(k))) {
                 isWindows = true;
             }
        }
    }

    if (isWindows) {
        bucket = "Windows";
    }

    return { ...p, rawOS: p.specs.system || "undefined", bucket, tOS };
};

const results = allData.map(normalizeOS);

const counts = {};
results.forEach(r => {
    let b = r.bucket;
    counts[b] = (counts[b] || 0) + 1;
});

console.log("\n--- Final OS Buckets ---");
Object.entries(counts)
    .sort((a,b) => b[1] - a[1]) 
    .forEach(([k,v]) => console.log(`${k}: ${v}`));
