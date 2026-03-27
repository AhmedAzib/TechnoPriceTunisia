import json

# Targeted Analysis for Lesia, ZTE, Honor, Oscal
files = [
    'c:/Users/USER/Documents/programmation/frontend/src/data/tunisianet_mobiles.json',
    'c:/Users/USER/Documents/programmation/frontend/src/data/mytek_mobiles.json'
]

print("Analyzing Lesia, ZTE, Honor, Oscal in 'Others'...")

target_brands = ['lesia', 'zte', 'honor', 'oscal']
candidates = {b: [] for b in target_brands}

count = 0

for path in files:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for p in data:
            t = p.get('title', '').lower()
            specs = p.get('specs', {})
            cpu = specs.get('cpu', 'Unknown').lower()
            
            # Simulating MobilesPage.jsx Overrides
            
            # Lesia Young 1 -> Quad Core
            if 'lesia young 1' in t: 
                continue # Classified as Quad Core
                
            # Lesia / ZTE / Oscal -> Unisoc
            if 'lesia' in t or 'zte' in t or 'oscal flat' in t:
                continue # Classified as Unisoc
                
            # Honor Play (Generic) -> MediaTek
            if 'honor play' in t:
                continue # Classified as MediaTek
            
            # Honor X5/X6 -> MediaTek
            if 'honor x5' in t or 'honor x6' in t or 'honor x7a' in t or 'honor x7b' in t:
                continue
                
            # Honor X7/X8/X9 -> Snapdragon (Classified)
            if 'honor x7' in t or 'honor x8' in t or 'honor x9' in t:
                continue

            # Oscal Tiger -> MediaTek
            if 'oscal tiger' in t:
                continue

            # Skip matches for target brands if they hit the above rules
            
            # Skip if classified
            if any(x in cpu for x in ['snapdragon', 'dimensity', 'helio', 'mediatek', 'unisoc', 'exynos', 'apple', 'bionic', 'kirin', 'quad core']):
                continue
            if any(x in cpu for x in ['snapdragon', 'dimensity', 'helio', 'mediatek', 'unisoc', 'exynos', 'apple', 'bionic', 'kirin', 'quad core']):
                continue
            
            # Check if it matches our target brands
            for b in target_brands:
                if b in t:
                    candidates[b].append(f"{p['title']} [{specs.get('cpu')}]")
                    count += 1
                    break
                    
    except Exception as e:
        print(f"Error reading {path}: {e}")

print(f"Total Unclassified Candidates for Targets: {count}")
for b, items in candidates.items():
    if items:
        print(f"\n--- {b.upper()} ({len(items)}) ---")
        for i in items[:10]:
            print(i)
