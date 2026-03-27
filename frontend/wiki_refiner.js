
import fs from 'fs/promises';
import path from 'path';

const RAW_FILE_PATH = path.join('src', 'data', 'wiki_raw.json');
const CLEAN_FILE_PATH = path.join('src', 'data', 'wiki_clean.json');

// Helper to clean price
function cleanPrice(raw) {
    if (!raw) return 0;
    // already floats in python script but just in case
    return parseFloat(raw);
}

const BRANDS = ['HP', 'DELL', 'LENOVO', 'ASUS', 'MSI', 'ACER', 'APPLE', 'INFINIX', 'SAMSUNG', 'BMAX', 'GIGABYTE', 'MICROSOFT'];

function detectBrand(title) {
    const t = title.toUpperCase();
    for (const b of BRANDS) {
        if (t.includes(b)) return b;
    }
    return "Unknown";
}

function extractSpecs(title) {
    const t = title.toUpperCase();
    const specs = {
        ram: "Unknown",
        storage: "Unknown",
        cpu: "Unknown",
        gpu: "Unknown",
        screen: "Unknown"
    };

    // RAM (Integer)
    const ramMatch = t.match(/(\d+)\s*(?:GO|GB)/);
    if (ramMatch) {
         specs.ram = parseInt(ramMatch[1], 10);
    } else {
        specs.ram = 0;
    }

    // Storage (Integer -> GB)
    const tbMatch = t.match(/(\d+)\s*(?:TO|TB)/);
    const gbMatch = t.match(/(\d+)\s*(?:GO|GB)\s*(?:SSD|HDD|NVME)?/);
    
    if (tbMatch) {
        specs.storage = parseInt(tbMatch[1], 10) * 1024;
    } else if (gbMatch) {
        specs.storage = parseInt(gbMatch[1], 10);
    } else {
        specs.storage = 0;
    }
    
    // CPU
    if (t.includes("I9")) specs.cpu = "i9";
    else if (t.includes("I7")) specs.cpu = "i7";
    else if (t.includes("I5")) specs.cpu = "i5";
    else if (t.includes("I3")) specs.cpu = "i3";
    else if (t.includes("RYZEN 9")) specs.cpu = "Ryzen 9";
    else if (t.includes("RYZEN 7")) specs.cpu = "Ryzen 7";
    else if (t.includes("RYZEN 5")) specs.cpu = "Ryzen 5";
    else if (t.includes("RYZEN 3")) specs.cpu = "Ryzen 3";
    else if (t.includes("CELERON")) specs.cpu = "Celeron";
    else if (t.includes("N100")) specs.cpu = "N100";
    else if (t.includes("N200")) specs.cpu = "N200";
    else if (t.includes("ULTRA 5")) specs.cpu = "Ultra 5";
    else if (t.includes("ULTRA 7")) specs.cpu = "Ultra 7";
    else if (t.includes("ULTRA 9")) specs.cpu = "Ultra 9";

    // GPU
    if (t.includes("RTX 4090")) specs.gpu = "RTX 4090";
    else if (t.includes("RTX 4080")) specs.gpu = "RTX 4080";
    else if (t.includes("RTX 4070")) specs.gpu = "RTX 4070";
    else if (t.includes("RTX 4060")) specs.gpu = "RTX 4060";
    else if (t.includes("RTX 4050")) specs.gpu = "RTX 4050";
    else if (t.includes("RTX 3050")) specs.gpu = "RTX 3050";
    else if (t.includes("RTX 2050")) specs.gpu = "RTX 2050";
    
    // Screen
    if (t.includes("17.3")) specs.screen = "17.3";
    else if (t.includes("16")) specs.screen = "16.0";
    else if (t.includes("15.6")) specs.screen = "15.6";
    else if (t.includes("14")) specs.screen = "14.0";
    else if (t.includes("13.3")) specs.screen = "13.3";

    return specs;
}

async function main() {
    try {
        const rawData = await fs.readFile(RAW_FILE_PATH, 'utf-8');
        const products = JSON.parse(rawData);
        
        const cleanProducts = products
            .map((p, index) => {
                const title = p.title || "";
                if (!title) return null;

                const specs = extractSpecs(title);
                const brand = detectBrand(title);

                return {
                    id: `WK-${index}`,
                    title: title,
                    price: cleanPrice(p.price),
                    oldPrice: 0,
                    image: p.image,
                    link: p.link,
                    brand: brand,
                    source: "Wiki",
                    specs: specs,
                    availability: "in-stock"
                };
            })
            .filter(p => {
                if (!p) return false;
                if (p.price < 300) return false;

                const t = p.title.toLowerCase();
                const blacklist = [
                    /monitor/i, /casque/i, /headset/i, /souris/i, /mouse/i, 
                    /clavier/i, /keyboard/i, /cable/i, /câble/i, /adaptateur/i, /sacoche/i, 
                    /imprimante/i, /printer/i, /accessoire/i, /toner/i, /cartouche/i, 
                    /manette/i, /webcam/i, /micro/i, /tapis/i, /hub/i, /support/i,
                    /refroidisseur/i, /nettoyant/i, /projecteur/i, /routeur/i,
                    /switch/i, /barrette/i, /cle usb/i, /clé usb/i, /sd card/i, 
                    /tv box/i, /tablette/i, /serveur/i, /server/i, /onduleur/i,
                    /carte graphique/i, /station d'accueil/i, /docking/i
                ];

                // 1. Direct Blacklist (Safe bans)
                if (blacklist.some(regex => regex.test(p.title))) return false;

                // 2. Conditional Bans (Ecran, Desktop, Components)
                const titleLower = p.title.toLowerCase();
                const isLaptop = titleLower.includes('portable') || titleLower.includes('laptop') || titleLower.includes('macbook');

                // Ban "Ecran" or "Écran" only if it's NOT a laptop (laptops often say "Ecran 15.6")
                if ((titleLower.includes('ecran') || titleLower.includes('écran')) && !isLaptop) {
                     // Double check: if it looks like a screen product
                     return false;
                }

                // Ban "PC" / "Desktop" / "Unité Centrale" if not a laptop
                // Ban "PC" / "Desktop" / "Unité Centrale" if not a laptop
                const desktopTerms = ['pc de bureau', 'desktop', 'all in one', 'aio', 'unite centrale', 'unité centrale', 'mini pc', 'station work', 'pc gamer', 'pc gaming'];
                if (desktopTerms.some(term => titleLower.includes(term)) && !isLaptop) {
                    return false;
                }

                // Ban "PC Gamer" or "Gaming" if it doesn't clearly say "Portable", "Laptop" or "MacBook"
                // (Unless we trust that we scraped the 'laptops' category, but user complains about bad items.
                //  Wiki often lists Desktops in weird places or search results mix them.)
                // HOWEVER: Many laptops are just "MSI Katana 15...". They might not say "Portable".
                // Safest bet for Wiki: If URL or breadcrumb isn't available, check for "Desktop" cues.
                // Let's assume if it doesn't match Desktop terms, it MIGHT be a laptop. 
                // BUT user said "PC Gamer" items were desktops. 
                // Let's rely on exclusion of known Desktop terms.
                
                // Re-instating the logic that blocked "Pack" only if it's a pack of accessories? 
                // "Pack" often implies a bundle. User said "no ...". 
                if (titleLower.includes('pack ') && !isLaptop) return false;

                return true;
            });

        await fs.writeFile(CLEAN_FILE_PATH, JSON.stringify(cleanProducts, null, 2));
        console.log(`Refined ${cleanProducts.length} products. Saved to ${CLEAN_FILE_PATH}`);

    } catch (err) {
        console.error("Error refining data:", err);
    }
}

main();
