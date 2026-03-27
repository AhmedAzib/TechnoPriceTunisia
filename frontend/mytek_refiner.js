
const fs = require('fs/promises');
const path = require('path');

const RAW_FILE = path.join(__dirname, 'src', 'data', 'mytek_raw.json');
const CLEAN_FILE = path.join(__dirname, 'src', 'data', 'mytek_clean.json');

// --- HELPER: CLEAN PRICE ---
function cleanPrice(priceStr) {
    if (!priceStr) return 0;
    let clean = String(priceStr)
        .replace(/\s+/g, '')       // Remove spaces
        .replace(/TND/i, '')       // Remove currency
        .replace(/DT/i, '')
        .replace(/,/g, '.');       // Fix decimals
    // Remove non-numeric start (e.g. "À partir de")
    clean = clean.replace(/^[^\d]+/, ''); 
    return parseFloat(clean) || 0;
}

// --- HELPER: STANDARDIZE SPECS ---
function extractSpecs(title) {
    const t = title.toLowerCase();
    
    let specs = {
        cpu: 'Unknown',
        ram: 0,      // Integer default
        storage: 0,  // Integer default
        gpu: 'Unknown',
        screen: 'Unknown'
    };

    // 1. CPU
    if (t.includes('i9')) specs.cpu = 'Intel Core i9';
    else if (t.includes('i7')) specs.cpu = 'Intel Core i7';
    else if (t.includes('i5')) specs.cpu = 'Intel Core i5';
    else if (t.includes('i3')) specs.cpu = 'Intel Core i3';
    else if (t.includes('ryzen 9')) specs.cpu = 'AMD Ryzen 9';
    else if (t.includes('ryzen 7')) specs.cpu = 'AMD Ryzen 7';
    else if (t.includes('ryzen 5')) specs.cpu = 'AMD Ryzen 5';
    else if (t.includes('ryzen 3')) specs.cpu = 'AMD Ryzen 3';
    else if (t.includes('m3')) specs.cpu = 'Apple M3';
    else if (t.includes('m2')) specs.cpu = 'Apple M2';
    else if (t.includes('m1')) specs.cpu = 'Apple M1';
    else if (t.includes('celeron')) specs.cpu = 'Celeron';
    else if (t.includes('pentium')) specs.cpu = 'Pentium';
    else if (t.includes('athlon')) specs.cpu = 'Athlon';

    // 2. RAM (Integer Extraction)
    // "16 go" or "16gb"
    const ramMatch = t.match(/(\d+)\s*(go|gb)/);
    if (ramMatch) {
         specs.ram = parseInt(ramMatch[1], 10);
    }

    // 3. STORAGE (Integer Extraction -> GB)
    // "512 go ssd" or "1 to"
    const tbMatch = t.match(/(\d+)\s*(to|tb)/);
    const gbMatch = t.match(/(\d+)\s*(go|gb)\s*(ssd|hdd|emmc)/);
    
    if (tbMatch) {
        specs.storage = parseInt(tbMatch[1], 10) * 1024; // Convert to GB
    } else if (gbMatch) {
        specs.storage = parseInt(gbMatch[1], 10);
    }

    // 4. GPU generic
    if (t.includes('rtx')) specs.gpu = 'NVIDIA RTX';
    else if (t.includes('gtx')) specs.gpu = 'NVIDIA GTX';
    else if (t.includes('radeon')) specs.gpu = 'AMD Radeon';
    else if (t.includes('intel') || t.includes('iris') || t.includes('uhd')) specs.gpu = 'Intel Integrated';
    
    // 5. Screen generic
    if (t.includes('17.3')) specs.screen = '17.3"';
    else if (t.includes('16"')) specs.screen = '16.0"';
    else if (t.includes('15.6')) specs.screen = '15.6"';
    else if (t.includes('14"')) specs.screen = '14.0"';
    else if (t.includes('13.3')) specs.screen = '13.3"';
    else if (t.includes('13.6')) specs.screen = '13.6"';

    return specs;
}

// --- HELPER: BRAND DETECTION ---
function detectBrand(title) {
    const brands = ["MSI", "ASUS", "LENOVO", "HP", "DELL", "ACER", "APPLE", "GIGABYTE", "HUAWEI", "SAMSUNG", "INFINIX", "MICROSOFT", "RAZER"];
    const t = title.toUpperCase();
    for (const b of brands) {
        if (t.includes(b)) return b.charAt(0) + b.slice(1).toLowerCase(); // Capitalize
    }
    return "Autre";
}

async function refine() {
    try {
        const rawData = await fs.readFile(RAW_FILE, 'utf-8');
        const products = JSON.parse(rawData);
        
        console.log(`Raw Products: ${products.length}`);
        
        const seenLinks = new Set();
        let skippedStock = 0;
        let skippedType = 0;

        const cleanProducts = products.map((p, index) => {
            const title = p.title || "";
            const tLower = title.toLowerCase();

            // 1. DEDUPLICATION
            if (seenLinks.has(p.link)) return null;
            seenLinks.add(p.link);

            // 2. STOCK FILTER (Crucial: "Clean Shop")
            // MyTek: "En stock", "Sur commande" -> OK. "Epuisé" -> Trash.
            // Scraper output: "En stock", "Epuisé", "Unknown"
            const stock = (p.stock || "").toLowerCase();
            
            // Whitelist approach: Must contain "stock" or "commande" to be safe?
            // Or Blacklist "epuisé" / "rupture".
            // User said: "If Sold Out... ignore it."
            if (stock.includes("épuisé") || stock.includes("indisponible") || stock.includes("hors stock")) {
                skippedStock++;
                return null;
            }
            // If unknown, maybe keep? Or strict?
            // Let's assume strict: if we don't know it's active, drop it?
            // Actually, safe blacklist is better.

            // 3. TYPE FILTER ("Mobile Only")
            // Exclude desktop words
            const badWords = ["pc de bureau", "desktop", "all-in-one", "tout-en-un", "ecran", "moniteur", "imprimante", "accessoire", "sacoche", "souris"];
            if (badWords.some(w => tLower.includes(w))) {
                // Double check if it says "portable" clearly
                if (!tLower.includes("portable") && !tLower.includes("laptop") && !tLower.includes("macbook")) {
                    skippedType++;
                    return null;
                }
            }

            // 4. SPECS & DATA
            const specs = extractSpecs(title);
            const price = cleanPrice(p.price);
            const brand = detectBrand(title);
            
            // Availability Logic
            const availability = stock.includes("commande") ? "on-order" : "in-stock";

            return {
                id: `MYTEK-${index}`,
                title: title,
                price: price,
                image: p.image,
                link: p.link,
                brand: brand,
                source: "MyTek",
                specs: specs,
                availability: availability
            };
        }).filter(p => p !== null);

        console.log(`Skipped (Stock): ${skippedStock}`);
        console.log(`Skipped (Type): ${skippedType}`);
        console.log(`Final Clean Count: ${cleanProducts.length}`);

        await fs.writeFile(CLEAN_FILE, JSON.stringify(cleanProducts, null, 2));
        console.log(`Saved to ${CLEAN_FILE}`);

    } catch (error) {
        console.error("Refiner Error:", error);
    }
}

refine();
