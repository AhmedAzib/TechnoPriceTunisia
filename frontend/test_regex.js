
const t = "LENOVO LOQ 15IAX9E – PC PORTABLE GAMER I5 12 GÉN RTX 3050 16GO 512 SSD";
const regex = /(\d+)\s*(GB|GO|G|SSD|NVME)/g;
const matches = [...t.matchAll(regex)];

console.log(`Testing Title: ${t}`);
console.log(`Regex: ${regex}`);
console.log(`Matches Found: ${matches.length}`);

for (const m of matches) {
    console.log(`Match: '${m[0]}' -> Val: ${m[1]} Unit: ${m[2]}`);
    const val = parseInt(m[1]);
    if (val > 64) console.log(`  -> CANDIDATE! ${val}`);
}
