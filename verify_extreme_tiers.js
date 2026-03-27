
const GPU_PERFORMANCE_TIERS = {
    // Ultra Enthusiast (4K Ultra / 8K)
    "GeForce RTX 4090": "Ultra Enthusiast",
    "GeForce RTX 4080 Super": "Ultra Enthusiast",
    "GeForce RTX 4080": "Ultra Enthusiast",
    "Radeon RX 7900 XTX": "Ultra Enthusiast",
    
    // Enthusiast (1440p High Refresh / 4K)
    "GeForce RTX 4070 Ti Super": "Enthusiast",
    "GeForce RTX 4070 Ti": "Enthusiast",
    "GeForce RTX 4070 Super": "Enthusiast",
    "GeForce RTX 4070": "Enthusiast",
    "Radeon RX 7900 XT": "Enthusiast",
    "Radeon RX 7900 GRE": "Enthusiast",
    "GeForce RTX 3090 Ti": "Enthusiast",
    "GeForce RTX 3090": "Enthusiast",
    "GeForce RTX 3080 Ti": "Enthusiast",

    // High Performance (1440p / 1080p Ultra)
    "GeForce RTX 4060 Ti": "High Performance",
    "Radeon RX 7800 XT": "High Performance",
    "Radeon RX 7700 XT": "High Performance",
    "GeForce RTX 3080": "High Performance",
    "GeForce RTX 3070 Ti": "High Performance",
    "GeForce RTX 3070": "High Performance",
    "Radeon RX 6950 XT": "High Performance",
    "Radeon RX 6900 XT": "High Performance",
    "Radeon RX 6800 XT": "High Performance",

    // Mainstream (1080p High)
    "GeForce RTX 4060": "Mainstream",
    "GeForce RTX 3060 Ti": "Mainstream",
    "GeForce RTX 3060": "Mainstream",
    "GeForce RTX 4050": "Mainstream", 
    "Radeon RX 7600 XT": "Mainstream",
    "Radeon RX 7600": "Mainstream",
    "Radeon RX 6750 XT": "Mainstream",
    "Radeon RX 6700 XT": "Mainstream",
    "Intel Arc A770": "Mainstream",
    "Intel Arc A750": "Mainstream",

    // Entry Level (1080p Entry)
    "GeForce RTX 3050": "Entry Level",
    "GeForce GTX 1660 Super": "Entry Level",
    "GeForce GTX 1650": "Entry Level",
    "Radeon RX 6600": "Entry Level",
    "Radeon RX 6500 XT": "Entry Level",
    "Radeon RX 6400": "Entry Level",
    "Intel Arc A580": "Entry Level",
    "Intel Arc A380": "Entry Level",
    "Intel Arc B570": "Entry Level",
};

const testGPUs = [
    "GeForce RTX 4090",
    "MSI GeForce RTX 4060 Ti", // Should hit partial match
    "Intel Arc B570",
    "Radeon RX 7900 XTX",
    "Unknown GPU", // Should be Unknown
    "GeForce GTX 1650"
];

testGPUs.forEach(gpuModel => {
    let tier = 'Unknown';
    const cleanModel = gpuModel.trim();
    
    // Check exact match first
    if (GPU_PERFORMANCE_TIERS[cleanModel]) {
        tier = GPU_PERFORMANCE_TIERS[cleanModel];
    } else {
        // Try partial match only if exact fails (Safety fallback)
        const foundTier = Object.keys(GPU_PERFORMANCE_TIERS).find(k => cleanModel.includes(k));
        if (foundTier) {
            tier = GPU_PERFORMANCE_TIERS[foundTier];
        }
    }
    
    console.log(`GPU: "${gpuModel}" -> Tier: "${tier}"`);
});
