
const fs = require('fs');
const path = 'c:/Users/USER/Documents/programmation/frontend/src/ProductsPage.jsx';
let content = fs.readFileSync(path, 'utf8');

// 1. Define the Map (User Values)
const overrides = {
    // Zotac 5070 (The "this one" linked to 2587)
    "Carte Graphique Zotac Gaming GeForce RTX 5070 12Go GDDR7": "2587 MHz",
    
    // User Manual List
    "Carte Graphique Gaming OC MSI GeForce RTX 5050 8Go GDDR6": "2647 MHz",
    "Carte Graphique Gaming MSI GeForce RTX 5060 8Go GDDR7 Shadow 2X OC Bulk": "2535 MHz",
    "Carte Graphique Gigabyte GeForce RTX 5060 8Go GDDR7 WINDFORCE OC": "2497 MHz",
    "Carte Graphique Gaming MSI GeForce RTX 5060 8Go GDDR7 Ventus 2X OC": "2635 MHz",
    "Carte Graphique Gaming MSI GeForce RTX 5060 8Go GDDR7 Inspire 2X OC": "2550 MHz",
    "Carte Graphique Gaming MSI GeForce RTX 5070 12Go GDDR7 Shadow 2X OC": "2557 MHz",
    "Carte Graphique Gaming MSI GeForce RTX 5070 12Go GDDR7 Ventus 2X OC Blanc": "2557 MHz",
    "Carte Graphique Gaming MSI GeForce RTX 5070 12Go GDDR7 Ventus 2X OC": "2557 MHz"
};

// 2. Helper to verify if overrides exist in content
const overridesStr = JSON.stringify(overrides, null, 4).replace(/"(\d+ MHz)"/g, '"$1"'); // cleanup quotes if needed
// Actually constructing the code block string is better
const overrideBlock = `
          // MANUAL OVERRIDES: EXTREME PERFORMANCE (User Request - Strict MHz)
          const SPACENET_EXTREME_OVERRIDES = {
               "Carte Graphique Zotac Gaming GeForce RTX 5070 12Go GDDR7": "2587 MHz",
               "Carte Graphique Gaming OC MSI GeForce RTX 5050 8Go GDDR6": "2647 MHz",
               "Carte Graphique Gaming MSI GeForce RTX 5060 8Go GDDR7 Shadow 2X OC Bulk": "2535 MHz",
               "Carte Graphique Gigabyte GeForce RTX 5060 8Go GDDR7 WINDFORCE OC": "2497 MHz",
               "Carte Graphique Gaming MSI GeForce RTX 5060 8Go GDDR7 Ventus 2X OC": "2635 MHz",
               "Carte Graphique Gaming MSI GeForce RTX 5060 8Go GDDR7 Inspire 2X OC": "2550 MHz",
               "Carte Graphique Gaming MSI GeForce RTX 5070 12Go GDDR7 Shadow 2X OC": "2557 MHz",
               "Carte Graphique Gaming MSI GeForce RTX 5070 12Go GDDR7 Ventus 2X OC Blanc": "2557 MHz",
               "Carte Graphique Gaming MSI GeForce RTX 5070 12Go GDDR7 Ventus 2X OC": "2557 MHz"
          };
`;

// 3. Inject Map (Insert after SPACENET_BOOST_OVERRIDES)
if (!content.includes("SPACENET_EXTREME_OVERRIDES")) {
    const boostEnd = content.indexOf("};", content.indexOf("SPACENET_BOOST_OVERRIDES")) + 2;
    content = content.slice(0, boostEnd) + "\n" + overrideBlock + content.slice(boostEnd);
    console.log("Injected SPACENET_EXTREME_OVERRIDES map.");
}

// 4. Rewrite Extraction Logic (Strict Map + Regex, NO TIERS)
const startMarker = `// 17. Extreme Performance (Normalization) - Global`;
const endMarker = `// 14.b CUDA Cores Filter`; // Assuming this follows
const newLogic = `
          // 17. Extreme Performance (Normalization) - Global
          // Logic: 
          // 1. Check SPACENET_EXTREME_OVERRIDES (Highest Priority)
          // 2. Check Strict Description Regex ("Extreme Performance: XXX MHz")
          // 3. Default to "Unknown" (REMOVED TIER LOGIC "Ultra Enthusiast" etc.)
          
          if (SPACENET_EXTREME_OVERRIDES[p.title]) {
              specs.extreme_performance = SPACENET_EXTREME_OVERRIDES[p.title];
          } 
          else {
              let ep = "Unknown";
              // Fallback: Strict Regex from Description only if explicitly stated "Extreme Performance"
              // (This preserves the "1000% safe" - no guessing)
              const m = (p.description || "").match(/(?:PERFORMANCES?\s*EXTR\S+MES?|EXTREME\s*PERFORMANCE|MODE\s*OC|OC\s*MODE)\s*[:\-]?\s*(\d+(?:\s*\d+)?)\s*MHZ/i);
              if (m) {
                   ep = \`\${m[1].replace(/\\s/g, '')} MHz\`;
              }
              specs.extreme_performance = ep;
          }
`;

// Locate the block
const regex = /\/\/ 17\. Extreme Performance \(Normalization\) - Global[\s\S]*?specs\.extreme_performance = 'Unknown';\s+}/;
// Note: My previous edit replaced lines. I need to be careful with matching.
// Providing a robust replacement by exact string match of the PREVIOUS content I put there.

const prevLogic = `// 17. Extreme Performance (Normalization) - Global
          // Logic: If map has it, use it. Otherwise Unknown.
          if (rule && rule.extreme) {
              specs.extreme_performance = rule.extreme;
          } else {
              if (!specs.extreme_performance) specs.extreme_performance = 'Unknown';
          }`;

// Try to match the simplified block I put in Step 850
// Since whitespace might vary, I'll search for the unique strings.
if (content.indexOf("if (rule && rule.extreme)") !== -1 && content.indexOf("specs.extreme_performance = rule.extreme;") !== -1) {
    // Replace the specific block
    const blockStart = content.indexOf("// 17. Extreme Performance (Normalization) - Global");
    const blockEnd = content.indexOf("}", content.indexOf("specs.extreme_performance = 'Unknown'")) + 1;
    
    if (blockStart !== -1 && blockEnd !== -1) {
        content = content.slice(0, blockStart) + newLogic.trim() + content.slice(blockEnd);
        console.log("Updated Extraction Logic to use Strict Overrides.");
    } else {
        console.error("Could not find extraction logic bounds.");
        process.exit(1);
    }
} else {
    // Maybe it's already updated?
    if (content.includes("SPACENET_EXTREME_OVERRIDES[p.title]")) {
        console.log("Logic already updated.");
    } else {
        console.error("Could not find previous extraction logic to replace.");
        process.exit(1);
    }
}

fs.writeFileSync(path, content, 'utf8');
console.log("Done.");
