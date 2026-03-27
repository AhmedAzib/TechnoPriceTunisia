
import fs from 'fs';
import path from 'path';

const RAW_FILE = path.join('src', 'data', 'tunisianet_raw.json');

try {
    const data = JSON.parse(fs.readFileSync(RAW_FILE, 'utf-8'));
    console.log(`Total products: ${data.length}`);

    const links = new Set();
    const uniqueCounts = {};
    let duplicates = 0;

    data.forEach(p => {
        if (links.has(p.link)) {
            duplicates++;
            return;
        }
        links.add(p.link);

        const s = p.stock || "NULL";
        uniqueCounts[s] = (uniqueCounts[s] || 0) + 1;
    });

    console.log(`Unique Links: ${links.size}`);
    console.log(`Duplicates: ${duplicates}`);
    console.log("Unique Stock Status Counts:");
    console.log(uniqueCounts);

} catch (err) {
    console.error(err);
}
