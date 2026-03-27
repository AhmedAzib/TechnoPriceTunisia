
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

# Simulate the NEW SAFE logic
def get_parsed_ram(title, existing_ram, price):
    # 1. Explicit
    explicitMatch = re.search(r'(\d{1,3})\s?(GO|GB|G)\s?(RAM|MEM|MÉM)', title, re.IGNORECASE)
    if explicitMatch: return int(explicitMatch.group(1))
    
    # 2. Loose with Guards
    matches = list(re.finditer(r'(\d{1,3})\s?(GO|GB|G)\b', title, re.IGNORECASE))
    best_ram = 0
    
    for m in matches:
        val = int(m.group(1))
        start = m.start()
        end = m.end()
        before = title[max(0, start-10):start].upper()
        after = title[end:min(len(title), end+10)].upper()
        
        # GUARDS
        if re.search(r'(RTX|GTX|MX|RADEON|GRAPHICS|VGA)\s?$', before): continue
        if re.search(r'(RTX|GTX|MX|RADEON)\s?\d{3,4}\s?$', before): continue
        if re.search(r'^\s?(G(É|E)N|TH)', after): continue
        
        if val <= 64 and val > best_ram:
            best_ram = val
    
    # Use existing if no loose match found or combined
    ram_val = best_ram
    if ram_val == 0 and existing_ram:
         try:
             s = str(existing_ram).upper().replace('GB','').replace('GO','').strip()
             ram_val = int(re.sub(r'\D', '', s))
         except: pass

    # 3. Price Sanity Check
    if price > 1200:
        if ram_val < 8: ram_val = 8 # Force 8GB min
        if ram_val == 11 or ram_val == 13: ram_val = 16
        
    return ram_val

target_rams = [2, 4, 6, 11, 13]

print("Scanning for RAM in [2, 4, 6, 11, 13] SAFE CHECK...")
for fp in files:
    if os.path.exists(fp):
        with open(fp, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                for p in data:
                    title = p.get('name', p.get('title', ''))
                    price = p.get('price', 0)
                    try:
                        if isinstance(price, str):
                            price = float(price.replace(',', '').replace(' ', '').replace('TND', '').replace('DT', ''))
                    except: price = 0
                    
                    specs = p.get('specs', {})
                    current_ram_val = get_parsed_ram(title, specs.get('ram'), price)
                    
                    # We want to verify we DON'T find these anymore
                    if current_ram_val in target_rams:
                         print(f"[{fp}] STILL BAD: RAM {current_ram_val} | Price: {price} | Title: {title}")
            except: pass
