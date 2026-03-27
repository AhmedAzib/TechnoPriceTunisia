
import axios from 'axios';
import fs from 'fs/promises';

const URL = 'https://www.tunisianet.com.tn/301-pc-portable-tunisie';

async function fetchAndSave() {
    try {
        const response = await axios.get(URL, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            responseType: 'text' // Force text
        });
        await fs.writeFile('debug_tunisianet.html', response.data);
        console.log('Saved HTML to debug_tunisianet.html');
    } catch (e) {
        console.error(e);
    }
}

fetchAndSave();
