import fs from 'fs';

// Load Data
const tunisianet = JSON.parse(fs.readFileSync('src/data/tunisianet_clean.json', 'utf8'));
const spacenet = JSON.parse(fs.readFileSync('src/data/spacenet_products.json', 'utf8'));
const mytek = JSON.parse(fs.readFileSync('src/data/mytek_test.json', 'utf8'));
const wiki = JSON.parse(fs.readFileSync('src/data/wiki_clean.json', 'utf8'));

const allData = [
    ...tunisianet.map(p => ({...p, source: 'Tunisianet'})),
    ...spacenet.map(p => ({...p, source: 'Spacenet'})),
    ...mytek.map(p => ({...p, source: 'MyTek', specs: {} })), 
    ...wiki.map(p => ({...p, source: 'Wiki'}))
];

console.log(`Total Products: ${allData.length}`);

const normalizeScreen = (p) => {
    let screen = (p.specs && p.specs.screen) ? p.specs.screen.toString().trim().toUpperCase() : "";
    
    // Normalize Title: replace all whitespace/NBSP with single space, handle commas
    const t = p.title.toUpperCase().replace(/\s+/g, ' ').replace(/,/g, '.').trim();

    // 1. Existing Specs extraction (Trust Source if Valid)
    // CRITICAL FIX: Ignore N/A from trusted sources
    if ((p.source === 'Spacenet' || p.source === 'Wiki') && p.specs.screen && p.specs.screen !== "Unknown" && p.specs.screen !== "N/A") {
        screen = p.specs.screen;
    }
    
    // 2. Title Scan 
    // Treat 'N/A' as missing
    if (!screen || screen === "UNKNOWN" || screen === "N/A" || screen === "") {
        
        // A. Hardcoded Map (PRIORTY OVER REGEX to avoid "Monitor Bundle" traps)
        const map = {
            // 16-inch models
            "LEGION PRO 7": "16.0", "LEGION PRO 5": "16.0", "LEGION SLIM 7": "16.0", "LEGION SLIM 5": "16.0",
            "LEGION 7": "16.0", "LEGION 5 PRO": "16.0", "LEGION 9": "16.0", "LEGION 5": "15.6",
            "LOQ 16": "16.0", "LOQ 15": "15.6", "LOQ 17": "17.3",
            "IDEAPAD PRO 5": "16.0", "THINKBOOK 16": "16.0", "THINKPAD T16": "16.0", "THINKPAD P16": "16.0", "THINKPAD E16": "16.0", "THINKPAD Z16": "16.0", "THINKPAD L16": "16.0",
            "YOGA PRO 9": "16.0", "YOGA PRO 7": "14.5", "YOGA 9": "14.0", "YOGA 7": "14.0", "YOGA SLIM 7": "14.0",
            "VIVOBOOK 16": "16.0", "VIVOBOOK S 16": "16.0", "VIVOBOOK PRO 16": "16.0", "VIVOBOOK 15": "15.6", "VIVOBOOK S 15": "15.6", "VIVOBOOK PRO 15": "15.6", "VIVOBOOK 17": "17.3", "VIVOBOOK GO 15": "15.6", "VIVOBOOK GO 14": "14.0", "VIVOBOOK 14": "14.0", "VIVOBOOK FLIP 14": "14.0", "VIVOBOOK E410": "14.0", "VIVOBOOK MAX": "15.6",
            "ZENBOOK 14": "14.0", "ZENBOOK DUO": "14.0", "ZENBOOK S 13": "13.3", "ZENBOOK PRO 14": "14.5", "ZENBOOK PRO 16": "16.0", "UX310": "13.3", "ZENBOOK A14": "14.0",
            "ROG ZEPHYRUS G16": "16.0", "ROG ZEPHYRUS M16": "16.0", "ROG STRIX G16": "16.0", "ROG STRIX SCAR 16": "16.0", "ROG STRIX G18": "18.0", "ROG STRIX SCAR 18": "18.0",
            "ROG ZEPHYRUS G14": "14.0", "ROG FLOW X13": "13.4", "ROG FLOW Z13": "13.4", "ROG FLOW X16": "16.0",
            "TUF GAMING A15": "15.6", "TUF GAMING F15": "15.6", "TUF GAMING F17": "17.3", "TUF GAMING A17": "17.3", "TUF GAMING A16": "16.0", "TUF GAMING F16": "16.0", "TUF GAMING A14": "14.0",
            "TUF A15": "15.6", "TUF F15": "15.6", "TUF F17": "17.3", "TUF A17": "17.3", "TUF A16": "16.0", "TUF F16": "16.0", "TUF A14": "14.0",
            "A15": "15.6", "F15": "15.6", "A17": "17.3", "F17": "17.3",
            "MSI RAIDER GE68": "16.0", "MSI RAIDER GE78": "17.0", 
            "MSI VECTOR GP68": "16.0", "MSI VECTOR GP78": "17.0",
            "MSI STEALTH 16": "16.0", "MSI STEALTH 14": "14.0", "MSI STEALTH 15": "15.6", "MSI STEALTH GS77": "17.3",
            "MSI PULSE 15": "15.6", "MSI PULSE 17": "17.3", "MSI KATANA 15": "15.6", "MSI KATANA 17": "17.3", "MSI SWORD 16": "16.0", "MSI SWORD 17": "17.0",
            "MSI CYBORG 15": "15.6", "MSI CYBORG 14": "14.0", "MSI THIN 15": "15.6", "MSI THIN GF63": "15.6", "MSI GF63": "15.6",
            "MSI PRESTIGE 13": "13.3", "MSI PRESTIGE 14": "14.0", "MSI PRESTIGE 16": "16.0", "MSI PRO DP": "N/A", "PS42": "14.0",
            "MSI MODERN 15": "15.6", "MSI MODERN 14": "14.0", "MSI SUMMIT E13": "13.4", "MSI SUMMIT E16": "16.0",
            "MSI CROSSHAIR 18": "18.0", "MSI CROSSHAIR 16": "16.0", "MSI CROSSHAIR 17": "17.3",
            "MSI CREATOR Z16": "16.0", "MSI CREATOR Z17": "17.0", "MSI CREATOR M16": "16.0",
            "AORUS 15": "15.6", "AORUS 16": "16.0", "AORUS 17": "17.3", "AERO 16": "16.0", "AERO 14": "14.0", "AERO 17": "17.3", "AORUS MASTER 18": "18.0",
            "GIGABYTE G5": "15.6", "GIGABYTE G6": "16.0", "GIGABYTE A5": "15.6", "GIGABYTE U4": "14.0",
            "A16 CVH": "16.0", "A16 CWH": "16.0", "A16 3WH": "16.0", "AERO X16": "16.0", "GAMING A16": "16.0",
            "VICTUS 15": "15.6", "VICTUS 16": "16.1", "OMEN 16": "16.1", "OMEN 17": "17.3", "OMEN TRANSCEND 14": "14.0", "HP VICTUS": "15.6", "HP OMEN": "15.6",
            "HP 15": "15.6", "HP 14": "14.0", "HP 17": "17.3", "PAVILION 15": "15.6", "PAVILION 14": "14.0", "ENVY 17": "17.3", "ENVY 16": "16.0", "ENVY X360 15": "15.6", "ENVY X360 14": "14.0", "SPECTRE X360 14": "14.0", "SPECTRE X360 16": "16.0", "HP SPECTRE": "13.3", "PROBOOK 460": "16.0", "HP OMNIBOOK": "14.0", "OMNIBOOK 3": "14.0", "OMNIBOOK 5": "14.0", "OMNIBOOK X": "14.0",
            "PROBOOK 450": "15.6", "PROBOOK 455": "15.6", "PROBOOK 440": "14.0", "PROBOOK 445": "14.0", "ELITEBOOK 840": "14.0", "ELITEBOOK 860": "16.0", "ELITEBOOK 650": "15.6", "ELITEBOOK 640": "14.0", "ELITEBOOK 830": "13.3",
            "DELL G15": "15.6", "DELL G16": "16.0", "ALIENWARE M16": "16.0", "ALIENWARE X16": "16.0", "ALIENWARE M18": "18.0", "ALIENWARE 16X": "16.0",
            "INSPIRON 15": "15.6", "INSPIRON 16": "16.0", "INSPIRON 14": "14.0", "INSPIRON 35": "15.6", "INSPIRON 55": "15.6", "INSPIRON 53": "13.3",
            "XPS 13": "13.4", "XPS 15": "15.6", "XPS 14": "14.5", "XPS 16": "16.3",
            "LATITUDE 3540": "15.6", "LATITUDE 3520": "15.6", "LATITUDE 3440": "14.0", "LATITUDE 3420": "14.0", "LATITUDE 5540": "15.6", "LATITUDE 5440": "14.0", "LATITUDE 7440": "14.0", "LATITUDE 5340": "13.3", "LATITUDE 7490": "14.0", "LATITUDE 3450": "14.0", "LATITUDE 7450": "14.0",
            "VOSTRO 3510": "15.6", "VOSTRO 3520": "15.6", "VOSTRO 3530": "15.6", "VOSTRO 3420": "14.0", "VOSTRO 15": "15.6", "VOSTRO 35": "15.6", "VOSTRO 55": "15.6", "VOSTRO 34": "14.0",
            "MACBOOK AIR 13": "13.6", "MACBOOK AIR 15": "15.3", "MACBOOK PRO 14": "14.2", "MACBOOK PRO 16": "16.2", "MACBOOK PRO 13": "13.3", "MACBOOK AIR M1": "13.3", "MACBOOK AIR M2": "13.6", "MACBOOK AIR M3": "13.6", "THINKPAD X1 CARBON": "14.0", "X1 CARBON": "14.0",
            "MATEBOOK D 15": "15.6", "MATEBOOK D 14": "14.0", "MATEBOOK 16": "16.0", "MATEBOOK 14": "14.0", "MATEBOOK X PRO": "14.2",
            "EXPERTBOOK B1": "15.6", "EXPERTBOOK B3": "14.0", "EXPERTBOOK B5": "16.0", "EXPERTBOOK P5": "15.6", "EXPERTBOOK P3": "14.0",
            "SURFACE LAPTOP": "13.5", "SURFACE PRO": "13.0",
            "IPS3": "15.6", "IP3": "15.6", "IP1": "15.6", "V15": "15.6", "X15": "15.6", "X17": "17.3", "P15": "15.6", "P14": "14.0",
            "VEGABOOK 10": "10.1", "SCHNEIDER": "14.1", "V130": "15.6", "L340": "15.6", "320-15": "15.6", "X54": "15.6", "E410": "14.0", "ACER 3": "15.6",
            "EXTENSIA": "15.6", "G5070": "15.6", "15ADA05": "15.6", "15IML05": "15.6", "X542": "15.6", "X515": "15.6",
            "X1 CARBON": "14.0", "K555": "15.6", "IMAC": "N/A", "APPLE IMAC": "N/A", "ONE 24": "N/A", "ALL IN ONE": "N/A",
            "DELL 15": "15.6", "DELL 16": "16.0", "DELL PRO 14": "14.0", "DELL PRO 16": "16.0", "THINKBOOK 14": "14.0", "THINKPAD E14": "14.0", "THINKPAD L16": "16.0", "THINKPAD L13": "13.3", "THINKPAD T14": "14.0", "THINKPAD X9-14": "14.0", "THINKPAD X9-15": "15.6", "PROART P16": "16.0",
            "MINIBOOK X": "10.5", "CHUWI COREBOOK": "14.0", "CHUWI MINIBOOK": "10.5",
            
            // Generic catch-alls
            "MACBOOK AIR": "13.6", "MACBOOK PRO": "14.2",
            "MacBook": "13.3", "MACBOOK": "13.3",
            "MPG TRIDENT": "N/A", "BOITIER": "N/A", "PC GAMER": "N/A", "PC BARBONE": "N/A", "ECRAN": "N/A", "SOURIS": "N/A", "CLAVIER": "N/A", "CASQUE": "N/A", "TV": "N/A", "MONITOR": "N/A", "IMPRIMANTE": "N/A", "TABLETTE": "10.0", "MODEM": "N/A", "ROUTER": "N/A", "POINT D'ACCES": "N/A", "ONDULEUR": "N/A", "REFROIDISSEUR": "N/A", "CARTE": "N/A", "MEMOIRE": "N/A", "DISQUE": "N/A", "SSD": "N/A", "MAC STUDIO": "N/A",
            "SYMANTEC": "N/A", "WIN PRO": "N/A", "OFFICE": "N/A", "NINTENDO": "N/A", "VERSUS 24": "N/A", "WII U": "N/A",
            "COQUE": "N/A", "SACOCHE": "N/A", "HOUSSE": "N/A", "ETUI": "N/A", "MANETTE": "N/A", "CONSOLE": "N/A"
        };
        
        for (const [key, val] of Object.entries(map)) {
            if (t.includes(key)) {
                screen = val;
                break;
            }
        }

        // B. Regex Search (If map didn't catch it OR returned N/A)
        // If map said N/A, we respect it. But if map didn't match, we run regex.
        if (!screen || screen === "UNKNOWN" || screen === "") {
            const specificMatch = t.match(/(\d{2}\.?\d?)\s*(?:["”»«″]|POUCE|INCH|''|')/);
            const ecranMatch = t.match(/ECRAN\s*(\d{2}\.?\d?)/);
            
            if (ecranMatch) {
                // Warning: ECRAN match might be a monitor bundle.
                // If matched > 18, check if title sounds like a laptop.
                if (parseFloat(ecranMatch[1]) > 18.0) {
                     if (t.includes("PC PORTABLE") || t.includes("LAPTOP")) {
                         // It's a bundle. Ignore this match.
                     } else {
                         screen = ecranMatch[1];
                     }
                } else {
                    screen = ecranMatch[1];
                }
            } 
            
            // Try specific match if screen is still empty
            if (!screen && specificMatch) {
                screen = specificMatch[1];
            }
        }

        // C. Last Resort inferred logic (Contextual)
        if (!screen || screen === "UNKNOWN" || screen === "N/A") {
            // New Aggressive Regexes
            if (t.match(/\bV15\b/)) screen = "15.6";
            else if (t.match(/\b15[A-Z0-9]{2,}/)) screen = "15.6"; 
            else if (t.match(/P15\d+/)) screen = "15.6"; 
            else if (t.match(/P14\d+/)) screen = "14.0"; 
            else if (t.match(/\bX15\b/)) screen = "15.6";
            else if (t.match(/\bX17\b/)) screen = "17.3";
            else if (t.match(/\bE410\b/)) screen = "14.0";
            else if (t.match(/\b13-[0-9]{4}/)) screen = "13.3"; 
            else if (t.match(/\bS16\b/)) screen = "16.0";
            else if (t.match(/\bV16\b/)) screen = "16.0";
            else if (t.match(/\bS14\b/)) screen = "14.0";
            else if (t.match(/\bA16\b/)) screen = "16.0";
            else if (t.match(/\b14-[A-Z0-9]/)) screen = "14.0"; 
            else if (t.match(/\b16-[A-Z0-9]/)) screen = "16.0";
            else if (t.match(/\b16[A-Z0-9]{2,}/)) screen = "16.0";
            
            // Old models (35xx, 55xx, 34xx)
            else if (t.match(/\b35\d{2}\b/)) screen = "15.6"; 
            else if (t.match(/\b55\d{2}\b/)) screen = "15.6";
            else if (t.match(/\b34\d{2}\b/)) screen = "14.0";
            else if (t.match(/\b54\d{2}\b/)) screen = "14.0";
            else if (t.match(/\b53\d{2}\b/)) screen = "13.3";

            // Default defaults
            else if (t.includes("EMMC")) screen = "14.0"; 
            else if (t.includes("CELERON")) screen = "15.6"; 
            else if (t.includes("ATOM")) screen = "10.1";

            // Contextual Matches
            else if (t.includes("17.3")) screen = "17.3";
            else if (t.includes("16.0") || t.includes(" 16 ")) screen = "16.0";
            else if (t.includes("15.6")) screen = "15.6";
            else if (t.includes("14.0") || t.includes(" 14 ")) screen = "14.0";
            else if (t.includes("13.3")) screen = "13.3";
            else if (t.includes("11.6")) screen = "11.6";
            
            // Ultra-Aggressive: If it has "15" in logical place (not in price or date), assume 15.6
            else if (t.includes(" 15 ") || t.match(/15-[A-Z0-9]/)) screen = "15.6";
            else if (t.includes(" 17 ") || t.match(/17-[A-Z0-9]/)) screen = "17.3";
            else if (t.includes(" 13 ")) screen = "13.3";
        }
    }

    // 3. Bucket Logic (User Requested)
    let bucket = "Unknown";
    let sVal = parseFloat(screen);
    
    // Safety check for weird parses
    if (isNaN(sVal) && screen.includes("N/A")) bucket = "Other";

    if (!isNaN(sVal)) {
        if (sVal >= 10 && sVal < 13) bucket = '11" - 12"';
        else if (sVal >= 13 && sVal < 15) bucket = '13" - 14"';
        else if (sVal >= 15 && sVal < 16) bucket = '15.6"';
        else if (sVal >= 16 && sVal <= 18) bucket = '16" - 18"';
        else if (sVal >= 18) bucket = 'Other'; 
        else bucket = "Other"; 
    } else if (bucket === "Unknown" && (t.includes("GAMER") || t.includes("PORTABLE") || t.includes("LAPTOP"))) {
         // Final Fallback for Laptops: Default to 15.6 if it's truly unknown but looks like a laptop
         if (!screen && (t.includes("PC") || t.includes("ORDINATEUR"))) {
             screen = "15.6";
             bucket = '15.6"';
         }
    }

    return { ...p, rawScreen: screen, bucket };
};

const results = allData.map(normalizeScreen);

// analyze distribution
const counts = {};
results.forEach(r => {
    let b = r.bucket;
    counts[b] = (counts[b] || 0) + 1;
});

console.log("\n--- Screen Size Buckets ---");
Object.entries(counts)
    .sort((a,b) => b[1] - a[1]) 
    .forEach(([k,v]) => console.log(`${k}: ${v}`));

console.log("\n--- Sample Others ---");
results.filter(r => r.bucket === "Other")
       .slice(0, 50)
       .forEach(r => console.log(`[${r.source}] ${r.title} (Screen: "${r.rawScreen}")`));
