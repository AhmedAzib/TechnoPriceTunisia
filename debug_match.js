
const title = "Carte Graphique Gaming Gigabyte Geforce RTX 4070 Ti";
const titleUp = title.toUpperCase();
const key1 = "RTX 4070 TI";
const key2 = "RTX 4070";

console.log(`Title: '${title}'`);
console.log(`TitleUp: '${titleUp}'`);
console.log(`Key1: '${key1}'`);
console.log(`Match Key1: ${titleUp.includes(key1)}`);
console.log(`Match Key2: ${titleUp.includes(key2)}`);
