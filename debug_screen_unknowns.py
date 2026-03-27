import json
import re
import os

DATA_DIR = 'c:/Users/USER/Documents/programmation/frontend/src/data/'

FILES = [
    'tunisianet_new.json',
    'megapc_gamer.json',
    'megapc_pro.json',
    'skymil_new.json',
    'techspace_new.json',
    'mytek_new.json',
    'mytek_laptops.json',
    'wiki_products.json',
    'techtunisia_products.json',
    'spacenet_products.json',
    'tdiscount_products.json'
    # Exclude mytek_mobiles.json as they are phones
]

def parse_screen(t, specs_screen):
    t = t.upper()
    s_val = 0.0
    
    # 1. Title Override (Priority)
    if "15.6" in t or "15,6" in t: s_val = 15.6
    elif "17.3" in t or "17,3" in t: s_val = 17.3
    elif re.search(r'16(\.0|["\']| \w)?', t) and not re.search(r'16\s?GB', t): 
         # Rough approximation of JS regex
         # t.includes("16.0") || t.match(/16["']/) || t.match(/(Ecran|Screen|Display).*?16/i)
         if "16.0" in t or "16\"" in t or re.search(r'(ECRAN|SCREEN|DISPLAY).*?16', t):
             s_val = 16.0
             
    elif "14.0" in t or "14\"" in t or "14.5" in t: s_val = 14.0
    elif "13.3" in t or "13.4" in t or "13.6" in t or "13\"" in t: s_val = 13.3
    
    # 2. Specs Inference
    if s_val == 0 and specs_screen:
        s_str = str(specs_screen).replace(',', '.')
        
        # Contextual Scan
        kw_match = re.search(r'(?:Écran|Ecran|Screen|Display|Diagonale?|Taille)[\s:|-]*(\d{2}(?:\.\d+)?)', s_str, re.IGNORECASE)
        unit_match = re.search(r'(\d{2}(?:\.\d+)?)\s?("|inch|po|pouce|dq)', s_str, re.IGNORECASE)
        
        if kw_match:
            s_val = float(kw_match.group(1))
        elif unit_match:
            s_val = float(unit_match.group(1))
        elif len(s_str) < 15: # Naive fallback
             try:
                 clean = re.sub(r'[^\d.]', '', s_str)
                 if clean: s_val = float(clean)
             except: pass

        # Sanity Guard
        if (s_val == 13 or s_val == 14) and not re.search(r'("|inch|ecran|dia|oled|fhd|qhd)', s_str, re.IGNORECASE):
            s_val = 0
            
        # Strict 16-18 Guard
        if 16 <= s_val < 18:
            has_context = kw_match or unit_match or re.search(r'("|inch|ecran|dia|oled|fhd|qhd|wuxga|wsxga|4k|16:10)', s_str, re.IGNORECASE)
            if not has_context:
                s_val = 0

    # 3. Model Inference
    if s_val == 0:
        if "HP 15" in t or "DELL 15" in t or "VICTUS 15" in t or "V15" in t or "IDEAPAD 3 15" in t or "VIVOBOOK 15" in t: s_val = 15.6
        elif "VOSTRO 35" in t or "LATITUDE 35" in t or "LATITUDE 55" in t or "LATITUDE 75" in t or "INSPIRON 15" in t or "INSPIRON 35" in t: s_val = 15.6
        elif re.search(r'\b(G15|NITRO 5|KATANA|CYBORG|THIN|GF63|TUF.*15|F15|A15|ROG.*15|STRIX G15|ZEPHYRUS G15|OMEN 15|LOQ 15)\b', t): s_val = 15.6
        
        elif "HP 17" in t or "VICTUS 16" in t or "LEGION 5" in t or "LEGION 7" in t or "ROG STRIX G16" in t or re.search(r'16-(R|A|B)', t): s_val = 16.0
        elif re.search(r'\b(G16|TUF\s?F16|TUF\s?A16|ROG\s?STRIX\s?G16|ROG\s?SCAR\s?16|ZEPHYRUS\s?G16|ZEPHYRUS\s?M16|OMEN\s?16|LOQ\s?16|PULSE\s?16|VECTOR\s?16|CROSSHAIR\s?16|LEGION\s?PRO\s?16|LEGION\s?SLIM\s?16)\b', t): s_val = 16.0
        
        elif "HP 14" in t or "V14" in t or "ZENBOOK 14" in t: s_val = 14.0
        elif "MACBOOK AIR" in t or "MACBOOK PRO 13" in t or "XPS 13" in t: s_val = 13.3
        elif "MACBOOK PRO 14" in t: s_val = 14.2
        elif "MACBOOK PRO 16" in t: s_val = 16.2

    return s_val

all_data = []
for fname in FILES:
    path = os.path.join(DATA_DIR, fname)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                js = json.load(f)
                all_data.extend(js)
            except:
                print(f"Failed to load {fname}")

print(f"Loaded {len(all_data)} products total.")

unknowns = []
for p in all_data:
    title = p.get('title', '')
    specs = p.get('specs', {})
    screen_spec = specs.get('screen', '')
    
    # Filter out obvious non-computers if possible (simple heuristic)
    if "IMPRIMANTE" in title.upper() or "ECRAN" in title.upper() and not "PC" in title.upper(): continue

    val = parse_screen(title, screen_spec)
    
    if val == 0:
        unknowns.append((title, screen_spec))

print(f"Found {len(unknowns)} items with Unknown screen.")
print("--- Top 50 Unknowns ---")
for t, s in unknowns[:50]:
    print(f"Title: {t[:60]}... | Spec: {s}")
