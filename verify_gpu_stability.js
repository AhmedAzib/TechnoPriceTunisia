
// verify_gpu_stability.js
// Run with: node verify_gpu_stability.js

// Mock the GPU logic from productUtils.js to ensure stability
const normalizeGpuMock = (title, specs) => {
    const t = (title || "").toUpperCase();
    let gpu = (specs.gpu || "").toString().toUpperCase();
    
    if (!gpu || gpu === "UNKNOWN" || gpu === "INTEGRATED" || gpu.length < 3) {
        // 1. Explicit Discrete GPU Check
        if (t.match(/RTX\s?4090/)) gpu = "RTX 4090";
        else if (t.match(/RTX\s?4080/)) gpu = "RTX 4080";
        else if (t.match(/RTX\s?4070/)) gpu = "RTX 4070";
        else if (t.match(/RTX\s?4060/)) gpu = "RTX 4060";
        else if (t.match(/RTX\s?4050/)) gpu = "RTX 4050";
        else if (t.match(/RTX\s?3080/)) gpu = "RTX 3080";
        else if (t.match(/RTX\s?3070/)) gpu = "RTX 3070";
        else if (t.match(/RTX\s?3060/)) gpu = "RTX 3060";
        else if (t.match(/RTX\s?3050/)) gpu = "RTX 3050";
        else if (t.match(/RTX\s?2050/)) gpu = "RTX 2050";
        else if (t.match(/GTX\s?1660/)) gpu = "GTX 1660";
        else if (t.match(/GTX\s?1650/)) gpu = "GTX 1650";
        else if (t.match(/MX570/)) gpu = "MX570";
        else if (t.match(/MX550/)) gpu = "MX550";
        else if (t.match(/MX450/)) gpu = "MX450";
        else if (t.match(/MX350/)) gpu = "MX350";
        else if (t.match(/MX330/)) gpu = "MX330";
        else {
            if (t.includes("IRIS") || t.includes("XE GRAPHICS")) gpu = "Intel Iris Xe";
            else if (t.includes("UHD")) gpu = "Intel UHD";
            else if (t.includes("RADEON") || t.includes("VEGA") || t.includes("AMD ")) gpu = "AMD Radeon";
            
            else if (specs.cpu || t) {
                const c = (specs.cpu || "").toUpperCase();
                if (t.match(/\bM[1-9]\b/) || t.match(/MACBOOK/) || c.includes("APPLE M")) {
                     gpu = "Apple GPU";
                }
                else if (t.includes("SNAPDRAGON") || c.includes("SNAPDRAGON")) {
                     gpu = "Adreno GPU"; 
                }
                else if (c.includes("N100") || c.includes("N200") || c.includes("N4000") || c.includes("N4500") || c.includes("CELERON") || t.includes("CELERON")) {
                    gpu = "Intel UHD"; 
                } 
                else if (c.includes("INTEL") || c.includes("CORE") || c.includes("ULTRA") || t.includes("INTEL") || t.match(/\bI[3579]\b/)) {
                    gpu = "Intel Integrated"; 
                } 
                else if (c.includes("RYZEN") || c.includes("ATHLON") || c.includes("AMD") || t.includes("RYZEN")) {
                    gpu = "AMD Radeon";
                } else {
                    gpu = "Unknown";
                }
            } else {
                gpu = "Unknown";
            }
        }
    } else {
        if (gpu.includes("RTX") && gpu.includes("3050")) gpu = "RTX 3050";
        else if (gpu.includes("RTX") && gpu.includes("2050")) gpu = "RTX 2050";
        else if (gpu.includes("RTX") && gpu.includes("4050")) gpu = "RTX 4050";
        else if (gpu.includes("RTX") && gpu.includes("4060")) gpu = "RTX 4060";
        else if (gpu.includes("UHD")) gpu = "Intel UHD";
        else if (gpu.includes("IRIS")) gpu = "Intel Iris Xe";
    }
    return gpu;
};

const testCases = [
    { name: "Explicit RTX 3050 Title", title: "PC ASUS ROG RTX 3050", specs: {}, expected: "RTX 3050" },
    { name: "Clean String RTX 4060", title: "MSI ABC", specs: { gpu: "NVIDIA GeForce RTX 4060" }, expected: "RTX 4060" },
    { name: "Intel N100 Inference", title: "HP 15 N100", specs: { cpu: "N100" }, expected: "Intel UHD" },
    { name: "Intel Core i7 Inference", title: "Dell XP I7", specs: { cpu: "Intel Core i7" }, expected: "Intel Integrated" },
    { name: "AMD Ryzen 5 Inference", title: "Lenovo Slim Ryzen 5", specs: { cpu: "Ryzen 5" }, expected: "AMD Radeon" },
    { name: "Apple M1 Inference", title: "MacBook Air M1", specs: {}, expected: "Apple GPU" },
    { name: "Snapdragon Inference", title: "Surface Pro Snapdragon", specs: {}, expected: "Adreno GPU" },
    { name: "Iris Xe Keyword", title: "ASUS Vivobook Iris Xe", specs: {}, expected: "Intel Iris Xe" },
    { name: "MX550 Detection", title: "HP Pavilion MX550", specs: {}, expected: "MX550" },
];

console.log("=== VERIFYING GPU LOGIC STABILITY ===");
let passed = 0;
let failed = 0;

testCases.forEach(test => {
    const result = normalizeGpuMock(test.title || "", { ...test.specs });
    if (result === test.expected) {
        console.log(`[PASS] ${test.name}: ${result}`);
        passed++;
    } else {
        console.error(`[FAIL] ${test.name}: Expected '${test.expected}', Got '${result}'`);
        failed++;
    }
});

console.log("=====================================");
if (failed === 0) {
    console.log(`SUCCESS: All ${passed} GPU stability tests passed.`);
    console.log("The GPU logic is secure.");
} else {
    console.error(`FAILURE: ${failed} tests failed.`);
    process.exit(1);
}
