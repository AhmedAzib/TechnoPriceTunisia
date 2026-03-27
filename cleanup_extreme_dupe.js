
const fs = require('fs');
const path = 'c:/Users/USER/Documents/programmation/frontend/src/ProductsPage.jsx';
let content = fs.readFileSync(path, 'utf8');

// The block to remove (approximate unique signature)
// It starts with the SECOND specs.cuda_cores assignments and ends with the OLD Extreme Performance logic
// We know it follows the NEW assignment block.

const targetStart = `specs.cuda_cores = cudaCores;
          specs.psu = psu;

          // 17. Extreme Performance (Normalization) - Global
          // Logic: If map has it, use it. Otherwise Unknown.`;

// We will search for this string.
// Note: whitespace in the file view showed 10 spaces indentation?
// Let's find the second occurrence of "specs.cuda_cores = cudaCores;"
// The first one is around line 1199.
// The second one is around line 1222.

const firstIdx = content.indexOf("specs.cuda_cores = cudaCores;");
const secondIdx = content.indexOf("specs.cuda_cores = cudaCores;", firstIdx + 1);

if (secondIdx !== -1) {
    // Determine the end of the block to remove.
    // The duplicate block ends at line 1231: "}" followed by newline and then line 1233 (comment)
    // We want to remove up to the start of "const manualCudaMap" ? No, manualCudaMap is later.
    // Line 1231 is }
    // Line 1233 is // 14.b CUDA Cores Filter...
    
    const endMatch = "// 14.b CUDA Cores Filter";
    const endIdx = content.indexOf(endMatch, secondIdx);
    
    if (endIdx !== -1) {
        // We remove from secondIdx up to endIdx (exclusive), leaving lines before 14.b
        const toRemove = content.slice(secondIdx, endIdx);
        console.log("Removing block:\n" + toRemove.substring(0, 100) + "...");
        
        content = content.slice(0, secondIdx) + content.slice(endIdx);
        fs.writeFileSync(path, content, 'utf8');
        console.log("Cleanup successful.");
    } else {
        console.error("Could not find end of duplicate block.");
    }
} else {
    console.error("Could not find second occurrence of duplicate assignment.");
}
