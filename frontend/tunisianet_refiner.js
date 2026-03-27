
import fs from 'fs/promises';
import path from 'path';

const RAW_FILE_PATH = path.join('src', 'data', 'tunisianet_raw.json');
const CLEAN_FILE_PATH = path.join('src', 'data', 'tunisianet_clean.json');

// Helper to clean price
function cleanPrice(raw) {
    if (!raw) return 0;
    // Remove spaces, dots (thousands), convert comma to dot
    // "1 234,500" -> "1234.500"
    const cleaned = raw.replace(/\s/g, '').replace(/,/g, '.'); 
    return parseFloat(cleaned);
}

const BRANDS = ['HP', 'DELL', 'LENOVO', 'ASUS', 'MSI', 'ACER', 'APPLE', 'INFINIX', 'SAMSUNG'];

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
        cpu: "Unknown" // Optional
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
    
    // CPU Simple Heuristics
    if (t.includes("I7") || t.includes("i7")) specs.cpu = "i7";
    else if (t.includes("I5") || t.includes("i5")) specs.cpu = "i5";
    else if (t.includes("I3") || t.includes("i3")) specs.cpu = "i3";
    else if (t.includes("RYZEN 7")) specs.cpu = "Ryzen 7";
    else if (t.includes("RYZEN 5")) specs.cpu = "Ryzen 5";

    return specs;
}

async function main() {
    try {
        const rawData = await fs.readFile(RAW_FILE_PATH, 'utf-8');
        const products = JSON.parse(rawData);
        
        const seenLinks = new Set();
        
        const cleanProducts = products
            .map((p, index) => {
                const price = cleanPrice(p.price);
                if (!price || price === 0) return null; // Safety Guard
                
                const title = p.title || "";
                if (!title) return null;

                // Deduplication
                if (seenLinks.has(p.link)) return null;
                seenLinks.add(p.link);

                const specs = extractSpecs(title);
                const brand = detectBrand(title);

                // Stock Logic
                // Raw stock often comes doubled like "En stockEn stock".
                // We just need to check inclusion of keywords.
                const rawStock = (p.stock || "").toLowerCase();
                let availability = "in-stock";
                if (rawStock.includes("sur commande")) {
                    availability = "on-order";
                } else if (rawStock.includes("hors stock") || rawStock.includes("épuisé") || rawStock.includes("rupture")) {
                    return null; // Explicitly remove if we ever find these
                }

                return {
                    id: `TN-${index}`, // Index is still unique for this run, even with nulls in map (filtered later)
                    title: title,
                    price: price,
                    oldPrice: 0,
                    image: p.image,
                    link: p.link,
                    brand: brand,
                    source: "Tunisianet",
                    specs: {
                        cpu: specs.cpu,
                        ram: specs.ram,
                        storage: specs.storage,
                        gpu: "Unknown", 
                        screen: "Unknown"
                    },
                    availability: availability
                };
            })
            .filter(p => p !== null);

        await fs.writeFile(CLEAN_FILE_PATH, JSON.stringify(cleanProducts, null, 2));
        console.log(`Refined ${cleanProducts.length} products. Saved to ${CLEAN_FILE_PATH}`);

    } catch (err) {
        console.error("Error refining data:", err);
    }
}

main();
