
import axios from 'axios';
import * as cheerio from 'cheerio';
import fs from 'fs/promises';
import path from 'path';

const BASE_URL = 'https://www.tunisianet.com.tn/301-pc-portable-tunisie';
const RAW_FILE_PATH = path.join('src', 'data', 'tunisianet_raw.json');
const MAX_PAGES = 60;

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function scrapePage(pageNumber) {
    const url = `${BASE_URL}?page=${pageNumber}`;
    console.log(`Fetching page ${pageNumber}: ${url}`);

    try {
        const { data } = await axios.get(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            },
            responseType: 'text' // Force text so we can check for JSON manually
        });

        let htmlContent = data;
        
        // Check if JSON
        try {
            const json = JSON.parse(data);
            if (json.rendered_products) {
                // console.log("Detected JSON response, extracting HTML...");
                htmlContent = json.rendered_products;
            }
        } catch (e) {
            // Not JSON, continue as HTML
        }

        const $ = cheerio.load(htmlContent);
        const products = [];

        // Select product items (adjust selector if needed, but generic is better)
        $('.item-product').each((i, el) => {
            const $el = $(el);
            
            // Extract Title
            const titleEl = $el.find('.product-title a');
            const title = titleEl.text().trim();
            const link = titleEl.attr('href');

            // Extract Image
            let image = $el.find('.product-thumbnail img').first().attr('src');
             // Try data-full-size if available
            const fullSize = $el.find('.product-thumbnail img').first().attr('data-full-size-image-url');
            if (fullSize) image = fullSize;

            // Extract Text for Price Regex
            // Use .price selector specifically to avoid noise
            const priceText = $el.find('.price').text().trim();
            
            // Regex for Price: Look for digits followed by "DT"
            // Handles "1 250,500 DT" or "1250DT" or "1&nbsp;250,500 DT"
            // Use \s in the separator group to capture normal space or NBSP
            const priceMatch = priceText.match(/(\d{1,3}(?:[\s\.]\d{3})*(?:,\d+)?)\s*DT/);
            let rawPrice = priceMatch ? priceMatch[1] : null;

            if (title && rawPrice) {
                products.push({
                    title,
                    price: rawPrice, // Keep raw for Refiner
                    image,
                    link, 
                    brand: null, // Will be filled by RegEx in Refiner or here
                    stock: $el.find('#stock_availability span').text().trim()
                });
            }
        });

        console.log(`Found ${products.length} products on page ${pageNumber}`);
        return products;

    } catch (error) {
        console.error(`Error scraping page ${pageNumber}:`, error.message);
        return [];
    }
}

async function main() {
    let allProducts = [];

    for (let i = 1; i <= MAX_PAGES; i++) {
        const products = await scrapePage(i);
        if (products.length === 0 && i > 1) { // If page 1 gives 0, still try? No, stop.
             if (i > 1) {
                 console.log("No more products found. Stopping.");
                 break;
             }
        }
        allProducts = [...allProducts, ...products];
        await sleep(1000); // Be polite
    }

    // Ensure directory exists
    const dir = path.dirname(RAW_FILE_PATH);
    await fs.mkdir(dir, { recursive: true });

    await fs.writeFile(RAW_FILE_PATH, JSON.stringify(allProducts, null, 2));
    console.log(`Saved ${allProducts.length} raw products to ${RAW_FILE_PATH}`);
}

main();
