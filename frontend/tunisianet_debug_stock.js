
import axios from 'axios';
import * as cheerio from 'cheerio';
import fs from 'fs/promises';

const URL = 'https://www.tunisianet.com.tn/301-pc-portable-tunisie?page=1';

async function debug() {
    console.log(`Fetching ${URL}...`);
    try {
        const { data } = await axios.get(URL, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        });

        let htmlContent = data;
        try {
            if (typeof data === 'object') {
                 // axios might auto-parse JSON
                 if (data.rendered_products) htmlContent = data.rendered_products;
            } else {
                const json = JSON.parse(data);
                if (json.rendered_products) {
                    htmlContent = json.rendered_products;
                }
            }
        } catch (e) {}

        const $ = cheerio.load(htmlContent);
        const products = $('.item-product');
        
        console.log(`Found ${products.length} products.`);
        
            let debugHtml = "";
            for (let i = 0; i < 3; i++) {
                debugHtml += `\n<!-- PRODUCT ${i+1} -->\n` + $(products[i]).html() + "\n";
            }
            await fs.writeFile('debug_products.html', debugHtml);
            console.log("Saved debug_products.html");
    } catch (e) {
        console.error("Error:", e.message);
    }
}

debug();
