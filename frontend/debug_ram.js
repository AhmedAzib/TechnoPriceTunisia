
const samples = [
    "PC PORTABLE LENOVO IPS3 R5-7520U 16G / 512 Go SSD / GREY + SACOCHE LENOVO",
    "PC Portable DELL Latitude 5440 i5 13è Gén 8G 512Go SSD - Gris",
    "PC Portable ASUS Vivobook 15 X1502VA i7 13è Gén 8G 512Go SSD - Silver",
    "Pc Portable DELL Vostro 3530 i5 13è Gén 24G 512Go SSD - Noir",
    "PC Portable HP 15-fd0080nk i5 13è Gén 16G 512Go SSD - Noir",
    "Boitier Pc Gamer Sharkoon REV220 Noir",
    "Boite D'alimentation Gamer MSI MPG A1000GS PCIE5 1000W"
];

const checkRam = (title) => {
    let r = "Unknown";
    const t = title.toUpperCase();
    
    // CURRENT REGEX
    // Matches "16G", "16GB", "16GO" (case insensitive due to toUpperCase)
    const titleRamMatch = t.match(/(\d+)\s*(GB|GO|G)(?![A-Z])/);
         
    // Specific fallback for "8Go" where "o" might be considered a letter
    const frenchMatch = t.match(/(\d+)\s*GO/);
    
    if (frenchMatch) r = frenchMatch[1] + "GB";
    else if (titleRamMatch) r = titleRamMatch[1] + "GB";
    
    console.log(`Title: ${title}`);
    console.log(`  -> Detected: ${r}`);
    
    // NEW PROPOSED REGEX (Testing)
    // Looking for space or end of string or non-word chars
    const matchSimple = t.match(/(\d+)\s*G\b/); 
    const matchSimple2 = t.match(/(\d+)\s*G(?=[\s\W]|$)/);
    // console.log(`  -> RegEx Test 1: ${matchSimple ? matchSimple[1] : 'null'}`);
    // console.log(`  -> RegEx Test 2: ${matchSimple2 ? matchSimple2[1] : 'null'}`);
};

samples.forEach(checkRam);
