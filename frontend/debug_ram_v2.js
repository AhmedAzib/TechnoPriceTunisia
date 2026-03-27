
const samples = [
    "Pc Portable HP 15-DW3042NK i7 8G 512GO SSD  Silver",
    "PC PORTABLE HP 15s-fq5001nk i5 8G 256 Go SSD W11 – Silver",
    "Pc Portable LENOVO IDEAPAD FLEX 5 14ABR8 AMD RYZEN 5 8G 512GO SSD Gris",
    "Pc portable HP Spectre x360 – 13-4150nf",
    "PC Portable HP SPECTRE – 13-AF000NK i5-8250U/256 SSD"
];

const checkRam = (title) => {
    let r = "";
    const t = title.toUpperCase();
    
    const matches = [...t.matchAll(/(\d+)\s*(GB|GO|G)(?![A-Z])/g)];
    // console.log(`Matches for "${title}":`, matches.map(m => m[0]));

    let bestCandidate = null;
    
    for (const m of matches) {
        const val = parseInt(m[1]);
        // console.log(`  Candidate: ${val}`);
        if (val >= 2 && val <= 96) {
            bestCandidate = val;
            break; 
        }
    }
    
    if (bestCandidate) r = bestCandidate + "GB";
    else r = "Unknown";
    
    console.log(`Title: ${title} -> Detected: ${r}`);
};

samples.forEach(checkRam);
