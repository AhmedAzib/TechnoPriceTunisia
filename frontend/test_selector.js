
import * as cheerio from 'cheerio';
import fs from 'fs/promises';

async function test() {
    const raw = await fs.readFile('debug_tunisianet.html', 'utf-8');
    
    let html = raw;
    try {
        const json = JSON.parse(raw);
        if (json.rendered_products) {
            console.log("Detected JSON response, extracting HTML...");
            html = json.rendered_products;
        }
    } catch (e) {
        console.log("Not JSON, treating as HTML");
    }

    const $ = cheerio.load(html);
    
    const items = $('.item-product');
    console.log(`Found ${items.length} items`);

    items.each((i, el) => {
        const title = $(el).find('.product-title a').text().trim();
        const price = $(el).find('.price').text().trim();
        
        // Regex for Price: Look for digits followed by "DT"
        const priceMatch = price.match(/(\d{1,3}(?:[ \.]\d{3})*(?:,\d+)?)\s*DT/);
        const extractedPrice = priceMatch ? priceMatch[1] : 'None';

        console.log(`[${i}] ${title} | ${price} | Clean: ${extractedPrice}`);
    });
}

test();
