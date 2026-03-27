
const fs = require('fs');
const path = 'c:/Users/USER/Documents/programmation/frontend/src/ProductsPage.jsx';
let content = fs.readFileSync(path, 'utf8');

const newMapBody = `
               // GT 610
               "Carte Graphique AXLE GT610 2Go DDR3": "1000 MHz",
               "Enter Carte Graphique GT610 2Go DDR3": "1000 MHz",
               
               // GT 730 (Remove from filter)
               "Carte Graphique Enter NVIDIA GeForce GT730 4Go DDR3": "Unknown",
               "Carte Graphique Arktek Nvidia Geforce GT730 4Go": "Unknown",
               
               // RTX 3050
               "Carte Graphique Zotac Gaming GeForce RTX 3050 6Go GDDR6 Twin Edge OC": "1477 MHz",
               "Carte Graphique GeForce MSI RTX 3050 Ventus 2X XS 8Go OC GDDR6": "1807 MHz",
               
               // RTX 5050
               "Carte Graphique Gaming MSI GeForce RTX 5050 8Go GDDR6 Shadow 2X OC": "2572 MHz",
               "Carte Graphique Gaming OC MSI GeForce RTX 5050 8Go GDDR6": "2632 MHz",
               
               // RTX 5060 / Ti
               "Carte Graphique Gaming Zotac GeForce RTX 5060 Twin Edge 8Go GDDR7": "2572 MHz", // Updated (was 2497)
               "Carte Graphique Gaming MSI GeForce RTX 5060 8Go GDDR7 Shadow 2X OC Bulk": "2527 MHz", // Updated (was 2572)
               "Carte Graphique Gigabyte GeForce RTX 4060 Windforce OC 8Go GDDR6": "2475 MHz",
               "Carte Graphique Gigabyte GeForce RTX 5060 8Go GDDR7 WINDFORCE OC": "2512 MHz", // Updated (was 2527)
               "Carte Graphique Gaming MSI GeForce RTX 5060 8Go GDDR7 Ventus 2X OC": "2527 MHz",
               "Carte Graphique Gaming MSI GeForce RTX 5060 8Go GDDR7 Inspire 2X OC": "2535 MHz",
               "Carte Graphique Zotac Gaming GeForce RTX 5060 8Go GDDR7 AMP": "2550 MHz",
               "Carte Graphique Zotac Gaming GeForce RTX 5060 8Go GDDR7 SOLO": "2497 MHz",
               "Carte Graphique Gaming Zotac GeForce RTX 5060 Ti 8Go GDDR7 Twin Edge": "2602 MHz",
               
               // RTX 5070
               "Carte Graphique Gaming MSI GeForce RTX 5070 12Go GDDR7 Shadow 2X OC": "2542 MHz", // Updated (was 2602)
               "Carte Graphique Zotac Gaming GeForce RTX 5070 12Go GDDR7": "2587 MHz",
               "Carte Graphique Zotac Gaming GeForce RTX 5070 12Go GDDR7 Twin Edge": "2512 MHz",
               "Carte Graphique Gaming MSI GeForce RTX 5070 12Go GDDR7 Ventus 2X OC Blanc": "2542 MHz",
               "Carte Graphique Gaming MSI GeForce RTX 5070 12Go GDDR7 Ventus 2X OC": "2542 MHz",
               "Carte Graphique Zotac Gaming GeForce RTX 5070 12Go GDDR7 Twin Edge OC": "2542 MHz",
               "Carte Graphique Gigabyte GeForce RTX 5070 12Go Eagle OC SFF GDDR7": "2587 MHz",
               
               // RTX 4070 Ti (Remove)
               "Carte Graphique Gaming Gigabyte Geforce RTX 4070 Ti": "Unknown"`;

// Regex to find the object body
const regex = /(const SPACENET_BOOST_OVERRIDES = \{)([\s\S]*?)(\};)/;
const match = content.match(regex);

if (match) {
    const newContent = content.replace(regex, `$1${newMapBody}\n          $3`);
    fs.writeFileSync(path, newContent, 'utf8');
    console.log("Successfully updated SPACENET_BOOST_OVERRIDES V2");
} else {
    console.error("Could not find SPACENET_BOOST_OVERRIDES object in file");
    process.exit(1);
}
