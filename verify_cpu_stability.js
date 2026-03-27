
/**
 * verify_cpu_stability.js
 * 
 * This script is a PERMANENT REGRESSION TEST for the Critical CPU Normalization Logic.
 * 
 * USER INSTRUCTION: "save the filter of cpu to make sure it will never change... make sure its saved 100%"
 * 
 * If you modify `src/utils/productUtils.js`, you MUST update this script to match and run it
 * to ensure no regressions are introduced.
 * 
 * Run with: node verify_cpu_stability.js
 */

// === LOGIC UNDER TEST (Mirrors src/utils/productUtils.js) ===
function standardizeCpu(cpuString) {
    let specs = { cpu: cpuString };

    // ==============================================================================
    // === CRITICAL: CPU STANDARDIZATION LOGIC - DO NOT MODIFY WITHOUT TESTING ===
    // This logic forcefully unifies all Intel variants (Core/Ultra/i-Series) into 
    // standard "Intel Core iX" buckets (i3, i5, i7, i9).
    // ANY CHANGE HERE MUST BE VERIFIED WITH `verify_cpu_stability.js`.
    // ==============================================================================
    if (specs.cpu && (specs.cpu.includes("Intel") || specs.cpu.includes("Core") || specs.cpu.includes("Ultra"))) {
        // Match numbers 3, 5, 7, 9 preceded by Core/Ultra/Space
        let targetNum = null;
        
        if (specs.cpu.match(/Core\s?i?\s?([3579])/i)) {
             targetNum = specs.cpu.match(/Core\s?i?\s?([3579])/i)[1];
        } else if (specs.cpu.match(/Ultra\s?([3579])/i)) {
             targetNum = specs.cpu.match(/Ultra\s?([3579])/i)[1];
        } else if (specs.cpu.match(/Intel\s?Core\s?([3579])/i)) { 
             targetNum = specs.cpu.match(/Intel\s?Core\s?([3579])/i)[1];
        }
        
        if (targetNum) {
            specs.cpu = `Intel Core i${targetNum}`;
        }
    }
    // ==============================================================================
    
    return specs.cpu;
}

// === TEST CASES ===
const testCases = [
    // Core Ultra Series 1 & 2 -> Core iX
    { input: "Intel Core Ultra 7", expected: "Intel Core i7" },
    { input: "Core Ultra 7", expected: "Intel Core i7" },
    { input: "Ultra 7 155H", expected: "Intel Core i7" },
    { input: "Intel Core Ultra 5", expected: "Intel Core i5" },
    { input: "Core Ultra 9", expected: "Intel Core i9" },

    // New Gen Intel Core (missing 'i') -> Core iX
    { input: "Intel Core 5", expected: "Intel Core i5" },
    { input: "Core 5 120U", expected: "Intel Core i5" },
    { input: "Core 3", expected: "Intel Core i3" },
    { input: "Intel Core 7 150U", expected: "Intel Core i7" },

    // Implicit U-Series (detected in extraction, passed here as e.g. "Intel Core 7") 
    // This test assumes extraction already did some work, or we test the raw standardization
    // The standardization logic mainly fixes "Core 5" -> "Core i5" conversions.
    
    // Existing Correct Formats (Should remain unchanged or re-affirmed)
    { input: "Intel Core i7", expected: "Intel Core i7" },
    { input: "Intel Core i5-12400F", expected: "Intel Core i5" },
    { input: "Intel Core i9", expected: "Intel Core i9" },
    { input: "Intel Core i3", expected: "Intel Core i3" },

    // Edge Cases / Typos
    { input: "Intel Core i 7", expected: "Intel Core i7" }, // Space after i
    { input: "Core i5", expected: "Intel Core i5" },
    
    // Non-Intel (Should pass through untouched by THIS logic)
    { input: "AMD Ryzen 7", expected: "AMD Ryzen 7" },
    { input: "Ryzen 5 5600X", expected: "Ryzen 5 5600X" },
    { input: "Apple M3", expected: "Apple M3" },
    { input: "Snapdragon X", expected: "Snapdragon X" }
];

// === RUNNER ===
console.log("=== VERIFYING CPU STABILITY ===");
let passed = 0;
let failed = 0;

testCases.forEach((tc, i) => {
    const result = standardizeCpu(tc.input);
    if (result === tc.expected) {
        passed++;
        // console.log(`[PASS] "${tc.input}" -> "${result}"`);
    } else {
        failed++;
        console.error(`[FAIL] Input: "${tc.input}"`);
        console.error(`       Expected: "${tc.expected}"`);
        console.error(`       Got:      "${result}"`);
    }
});

console.log("\nResults:");
console.log(`PASS: ${passed}`);
console.log(`FAIL: ${failed}`);

if (failed === 0) {
    console.log("\n✅ CPU LOGIC IS STABLE AND VERIFIED.");
} else {
    console.error("\n❌ WARNING: CPU LOGIC HAS REGRESSIONS.");
    process.exit(1);
}
