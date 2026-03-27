const fs = require('fs');

// Read the productUtils.js file as text to extract the logic, or we can just import it if we make it a module.
// But productUtils uses some imports and DOM stuff maybe? Let's just create a mock script with the same logic for testing.

const skymilAmdData = JSON.parse(fs.readFileSync('C:/Users/USER/Documents/programmation/frontend/src/data/skymil_amd_mobos.json', 'utf8'));

skymilAmdData.forEach(p => {
    let t = p.title.toUpperCase();
    let maxMem = "Unknown";
    let speed = "Unknown";

    // 64GB Group
    if (t.includes("A520MHP")) maxMem = "64GB";
    if (t.includes("A620M-PLUS WIFI")) maxMem = "64GB";

    // 128GB Group
    if (t.includes("B550M-K")) maxMem = "128GB";
    if (t.includes("A620M-F GAMING WIFI")) maxMem = "128GB";
    if (t.includes("B550M PRO-VDH") && !t.includes("WIFI")) maxMem = "128GB";
    if (t.includes("B550M PRO-VDH WIFI")) maxMem = "128GB";
    if (t.includes("B550 PHANTOM GAMING 4")) maxMem = "128GB";
    if (t.includes("TUF GAMING B550M-PLUS WIFI II")) maxMem = "128GB";
    if (t.includes("B550 PRO4")) maxMem = "128GB";

    // 192GB Group
    if (t.includes("A620M GAMING X")) maxMem = "192GB";
    if (t.includes("PRIME B650-PLUS WIFI")) maxMem = "192GB";
    if (t.includes("A620-PRO WIFI")) maxMem = "192GB";
    if (t.includes("B650M GAMING PLUS WIFI")) maxMem = "192GB";
    if (t.includes("PRIME B840-PLUS WIFI")) maxMem = "192GB";
    if (t.includes("TUF GAMING B650-PLUS WIFI")) maxMem = "192GB";
    if (t.includes("PRO B850-P WIFI")) maxMem = "192GB";
    if (t.includes("X870 EAGLE WIFI7")) maxMem = "192GB";
    if (t.includes("ROG STRIX B650-A GAMING WIFI")) maxMem = "192GB";
    if (t.includes("ROG STRIX B850-A GAMING WIFI AM5")) maxMem = "192GB";
    if (t.includes("X870 GAMING X WIFI7")) maxMem = "192GB";
    if (t.includes("PRO X870E-P WIFI")) maxMem = "192GB";
    if (t.includes("TUF GAMING X870-PLUS WIFI")) maxMem = "192GB";
    if (t.includes("B850 EDGE TI WIFI WHITE")) maxMem = "192GB";
    if (t.includes("X870 AORUS ELITE WIFI7 ICE")) maxMem = "192GB";
    if (t.includes("X870E AORUS ELITE WIFI7")) maxMem = "192GB";
    if (t.includes("X870E AORUS PRO")) maxMem = "192GB";
    if (t.includes("X870E AORUS PRO ICE")) maxMem = "192GB";
    if (t.includes("MPG X870E EDGE TI WIFI")) maxMem = "192GB";

    // 256GB Group
    if (t.includes("PRO B840M-P WIFI6E")) maxMem = "256GB";
    if (t.includes("PRIME B650M-A WIFI II")) maxMem = "256GB";
    if (t.includes("PRO B840-P WIFI")) maxMem = "256GB";
    if (t.includes("B650 PG LIGHTNING")) maxMem = "256GB";
    if (t.includes("B850 EAGLE WIFI6E")) maxMem = "256GB";
    if (t.includes("B850 GAMING WIFI6")) maxMem = "256GB";
    if (t.includes("B650 PRO RS")) maxMem = "256GB";
    if (t.includes("B850M GAMING PLUS WIFI")) maxMem = "256GB";
    if (t.includes("B650 STEEL LEGEND WIFI")) maxMem = "256GB";
    if (t.includes("TUF GAMING B850-PLUS WIFI")) maxMem = "256GB";
    if (t.includes("B850 GAMING PLUS WIFI")) maxMem = "256GB";
    if (t.includes("X870 PRO RS WIFI")) maxMem = "256GB";
    if (t.includes("ROG STRIX B650E-F GAMING WIFI D5")) maxMem = "256GB";
    if (t.includes("ROG STRIX B850-F GAMING WIFI AM5")) maxMem = "256GB";
    if (t.includes("X870 STEEL LEGEND WIFI")) maxMem = "256GB";
    if (t.includes("CROSSHAIR X870E HERO")) maxMem = "256GB";

    // SPEED
    let speedOverrides = [
        { k: "A520MHP", v: "4266 MHz" },
        { k: "B550M-K", v: "4866 MHz" },
        { k: "B550M PRO-VDH", v: "4400 MHz" },
        { k: "A620M-PLUS WIFI", v: "6400 MHz" },
        { k: "A620M-F GAMING WIFI", v: "6400 MHz" },
        { k: "A620M GAMING X", v: "6400 MHz" },
        { k: "B650M GAMING PLUS WIFI", v: "7200 MHz" },
        { k: "PRO B840M-P WIFI6E", v: "8000 MHz" },
        { k: "B650M-HDV/M.2", v: "6400 MHz" },
        { k: "B850M GAMING PLUS WIFI", v: "8200 MHz" },
        { k: "X870 PRO RS WIFI", v: "8000 MHz" }
    ];

    for (const ov of speedOverrides) {
         if (t.includes(ov.k.toUpperCase())) {
              speed = ov.v;
              break; 
         }
    }

    console.log(`[${speed}] [${maxMem}] ${p.title}`);
});
