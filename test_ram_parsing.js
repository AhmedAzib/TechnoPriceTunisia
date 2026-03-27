import { normalizeProductData } from './frontend/src/utils/productUtils.js';

const testProducts = [
    {
        title: "Barrette Mémoire SODIMM 2 Go DDR3L / 1600 MHz",
        category: "ram",
        source: "Tunisianet",
        price: 27
    },
    {
        title: "Barrette Mémoire SODIMM Team Group 4 Go DDR3L / 1600 MHz",
        category: "ram",
        source: "Tunisianet",
        price: 39
    }
];

const results = normalizeProductData(testProducts);
console.log(JSON.stringify(results.map(r => r.specs), null, 2));
