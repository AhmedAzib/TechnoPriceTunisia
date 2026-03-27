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

const normalizeHz = (p) => {
    let hz = "60Hz"; // Default standard
    let val = 0;
    let method = "Unknown";
    
    const t = (p.title + " " + (p.specs.screen||"") + " " + (p.specs.hz||"")).toUpperCase().replace(/\s+/g, ' ');
    
    // 1. Regex Extraction
    const match = t.match(/(\d{2,3})\s*(?:HZ|HERTZ|HZE)/);
    
    if (match) {
        val = parseInt(match[1]);
        method = "Regex";
    } 
    
    // 2. Inference Logic
    if (val === 0) {
        method = "Inference - NonGaming";
        const isGaming = t.includes("RTX") || t.includes("GTX") || t.includes("GAMER") || t.includes("LEGION") || t.includes("ROG") || t.includes("TUF") || t.includes("NITRO") || t.includes("VICTUS") || t.includes("OMEN") || t.includes("KATANA") || t.includes("G15") || t.includes("LOQ");

        if (isGaming) {
            method = "Inference - Gaming";
            if (t.includes("TUF") || t.includes("KATANA") || t.includes("VICTUS") || t.includes("NITRO") || t.includes("LOQ") || t.includes("MSI THIN") || t.includes("CYBORG") || t.includes("SWORD") || t.includes("PULSE") || t.includes("AORUS") || t.includes("CROSSHAIR") || t.includes("ALPHA")) {
                val = 144;
                method = "Inference - Core Gamer";
            }
            else if (t.includes("LEGION") || t.includes("OMEN") || t.includes("ZEPHYRUS") || t.includes("STRIX") || t.includes("AERO") || t.includes("RAIDER") || t.includes("ALIENWARE") || t.includes("SCAR")) {
                val = 165;
                method = "Inference - Premium";
            }
            else if (t.includes("G15") || t.includes("IDEAPAD GAMING") || t.includes("G5") || t.includes("PAVILION GAMING") || t.includes("VIVOBOOK PRO") || t.includes("VIVOBOOK 16X") || t.includes("VIVOBOOK 15X") || t.includes("DELL G3") || t.includes("BRAVO")) {
                val = 120;
                method = "Inference - Entry";
            }
            else if (t.includes("VOSTRO") || t.includes("LATITUDE") || t.includes("THINKBOOK") || t.includes("ASUS X") || t.includes("HP 15") || t.includes("PROBOOK") || t.includes("PRESTIGE") || t.includes("MODERN") || t.includes("SUMMIT") || t.includes("EXPERTBOOK")) {
                val = 60;
                method = "Inference - Workstation";
            }
            else {
                val = 144; 
                method = "Inference - Default Gamer Fallback";
            }
        } else {
             if (t.includes("OLED") && (t.includes("2.8K") || t.includes("3K"))) {
                 val = 90; 
                 method = "Inference - OLED";
             } else {
                 val = 60;
             }
        }
    }

    // Bucketing
    let bucket = "Unknown";
    if (val <= 60) bucket = "60 Hz";
    else if (val <= 120) bucket = "120 Hz"; 
    else if (val <= 144) bucket = "144 Hz"; 
    else if (val <= 165) bucket = "165 Hz"; 
    else if (val >= 200) bucket = "240 Hz+"; 
    else bucket = "Unknown"; 

    return { ...p, bucket, val, method };
};

const results = allData.map(normalizeHz);

console.log("\n--- INSPECTING 144Hz 'Default Gamer Fallback' ---");
// These are the ones inflating the count
const suspicious = results.filter(r => r.method === "Inference - Default Gamer Fallback");
console.log(`Count: ${suspicious.length}`);
suspicious.slice(0, 50).forEach(r => console.log(`[${r.source}] ${r.title}`));

console.log("\n--- INSPECTING 144Hz 'Regex' (Just to be sure) ---");
const regex144 = results.filter(r => r.bucket === "144 Hz" && r.method === "Regex");
console.log(`Count: ${regex144.length}`);
regex144.slice(0, 10).forEach(r => console.log(`[${r.source}] ${r.title}`));
