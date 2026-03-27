import json
import re

FILE = 'src/data/mytek_motherboards.json' # Using one data source as sample, logic applies to all

# Proposed Safety Map (Synced with ProductsPage.jsx)
CHIPSET_GEN_MAP = {
    # GEN 5 (PCIe 5.0) - High End
    "Z790": "Gen 5", "X670": "Gen 5", "X670E": "Gen 5", "Z690": "Gen 5", 
    "B650E": "Gen 5", "X870": "Gen 5", "X870E": "Gen 5", "Z890": "Gen 5", 
    "B850": "Gen 5", "B860": "Gen 5",
    
    # GEN 4 (PCIe 4.0)
    "B650": "Gen 4", # Standard B650 GPU slot is Gen 4. (M.2 might be 5)
    "B550": "Gen 4", "X570": "Gen 4", "A620": "Gen 4",
    "Z590": "Gen 4", "B560": "Gen 4", "H570": "Gen 4", "H510": "Gen 4",
    "H610": "Gen 4", "B760": "Gen 4", "H770": "Gen 4",
    "B840": "Gen 4", "H810": "Gen 4", # Added per audit

    # GEN 3 (PCIe 3.0)
    "Z490": "Gen 3", "H470": "Gen 3", "B460": "Gen 3", "H410": "Gen 3",
    "Z390": "Gen 3", "B365": "Gen 3", "B360": "Gen 3", "H370": "Gen 3", "H310": "Gen 3",
    "B450": "Gen 3", "X470": "Gen 3", "X370": "Gen 3", "B350": "Gen 3", "A320": "Gen 3", "A520": "Gen 3"
}

# Override for specific models if needed (Empty for now)
MANUAL_OVERRIDES = {
}

def analyze():
    # Load ALL motherboard data files to be safe
    files = [
        'src/data/mytek_motherboards.json',
        'src/data/tunisianet_motherboards.json',
        'src/data/spacenet_motherboards.json',
        'src/data/wiki_motherboards.json',
        'src/data/sbs_motherboards.json'
    ]
    
    products = []
    for fpath in files:
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                products.extend(json.load(f))
        except FileNotFoundError:
            pass # Skip if local env doesn't have all files

    print(f"Loaded {len(products)} motherboards.")
    
    counts = {"Gen 5": 0, "Gen 4": 0, "Gen 3": 0, "Unknown": 0}
    unknown_chipsets = {}

    for p in products:
        title = p.get('title', '').upper()
        
        gen = "Unknown"
        
        # 1. Check Map
        for chipset, g_val in CHIPSET_GEN_MAP.items():
            if chipset in title:
                # Priority Check: Ensure B650E doesn't get matched as B650
                # If we matched B650, check if it's actually B650E
                if chipset == "B650" and "B650E" in title:
                    gen = "Gen 5" 
                else:
                    gen = g_val
                break
        
        counts[gen] += 1
        
        if gen == "Unknown":
            print(f"[UNKNOWN] {p.get('title', 'NO TITLE')}")
            # Try to identify potential chipset for logging
            # Look for typical chipset patterns like [A-Z]\d{3}
            match = re.search(r'\b([A-Z]\d{3}[MA]?)\b', title)
            if match:
                c = match.group(1)
                unknown_chipsets[c] = unknown_chipsets.get(c, 0) + 1
            # else:
            #     print(f"Unknown No-Chipset: {title}")

    print("\n--- Distribution ---")
    for k, v in counts.items():
        print(f"{k}: {v}")

    print("\n--- Unknown Chipsets Found (To Add to Map) ---")
    for k, v in sorted(unknown_chipsets.items(), key=lambda x: -x[1]):
        print(f"{k}: {v}")

if __name__ == "__main__":
    analyze()
