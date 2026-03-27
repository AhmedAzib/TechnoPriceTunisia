
const samples = [
    "PC PORTABLE HP ENVYX360 15-FE0002NK / I5-1335U / 8G / 512G / IRISXe / 15.6\" / SILVER"
];

const checkRam = (title) => {
    let r = "";
    const t = title.toUpperCase();
    
    // Hardcoded Maps Check
    const modelRAMMap = {
        "MR942FN/A": "16", 
        "13-4150NF": "8",   
        "13-AF000NK": "8",  
        "IMAC ( APPLE64)": "8", 
        "MACBOOK PRO RETINA – 13 POUCES": "8", 
        "IMAC RETINA 5K – 27 POUCES": "8"     
    };
    for (const [key, val] of Object.entries(modelRAMMap)) {
        if (t.includes(key)) {
            r = val + "GB";
            console.log(`Matched Map: ${r}`);
        }
    }

    const matches = [...t.matchAll(/(\d+)\s*(GB|GO|G)(?![A-Z])/g)];
    console.log(`Matches:`, matches.map(m => m[0]));

    let bestCandidate = null;
    
    for (const m of matches) {
        const val = parseInt(m[1]);
        if (val >= 2 && val <= 96) {
            bestCandidate = val;
            break; 
        }
    }
    
    if (bestCandidate) r = bestCandidate + "GB";
    
    console.log(`Title: ${title} -> Detected: ${r}`);
};

samples.forEach(checkRam);
