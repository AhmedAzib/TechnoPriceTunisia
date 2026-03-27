
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import os
import re

files = [
    'frontend/src/data/techtunisia_products.json',
    'frontend/src/data/megapc_gamer.json',
    'frontend/src/data/megapc_pro.json',
    'frontend/src/data/tunisianet_new.json', 
    'frontend/src/data/mytek_new.json', 
    'frontend/src/data/mytek_laptops.json',
    'frontend/src/data/wiki_products.json',
    'frontend/src/data/skymil_new.json', 
    'frontend/src/data/techspace_new.json', 
    'frontend/src/data/spacenet_products.json',
    'frontend/src/data/tdiscount_products.json'
]

found_count = 0

# Simulate the JS cleaning logic
def get_bad_ram(title, existing_ram):
    if existing_ram and existing_ram != 'Unknown': return 0
    
    # Loose regex that might pick up "14"
    match = re.search(r'(\d{1,3})\s?(GO|GB|G)\b', title, re.IGNORECASE)
    if match:
        val = int(match.group(1))
        # Logic allows anything <= 64 now. 
        # If title is "Asus Vivobook 14 Go", it might catch "14 Go" -> 14GB
        return val
    return 0

found_count = 0

print("Scanning for IMPLICIT 14GB RAM...")
for fp in files:
    if os.path.exists(fp):
        with open(fp, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                for p in data:
                    specs = p.get('specs', {})
                    existing_ram = specs.get('ram')
                    title = p.get('name', p.get('title', ''))
                    
                    val = get_bad_ram(title, existing_ram)
            
            # Check specifically for 14
                    if val == 14:
                        print(f"[{fp}] MATCH: {title} -> Parsed: 14GB")
                        found_count += 1
            except Exception as e:
                pass

print(f"\nTotal items with 14GB RAM: {found_count}")
