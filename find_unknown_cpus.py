
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import re
import os

files = [
    'frontend/src/data/techtunisia_products.json',
    'frontend/src/data/megapc_gamer.json',
    'frontend/src/data/megapc_pro.json',
    'frontend/src/data/tunisianet_new.json', 
    'frontend/src/data/mytek_products.json',
    'frontend/src/data/wiki_products.json',
    'frontend/src/data/skymil_products.json',
    'frontend/src/data/techspace_products.json',
    'frontend/src/data/spacenet_products.json',
    'frontend/src/data/tdiscount_products.json'
]

def normalize_cpu(title, existing_cpu=""):
    t = title.upper()
    specs_cpu = existing_cpu or "Unknown"
    
    if specs_cpu != "Unknown" and len(specs_cpu) > 2:
        return specs_cpu # Assumed valid if exists
        
    # Logic from productUtils.js (Simplified for detection)
    
    # Apple
    if re.search(r'\bM[1-9]\s?(PRO|MAX|ULTRA)?\b', t): return "Apple M"
    if "SNAPDRAGON" in t: return "Snapdragon"
    
    # Accessories Check
    if t.startswith("FILTRE") or "FILTRE DE" in t or t.startswith("BOITE") or t.startswith("ALIMENTATION") or t.startswith("CLAVIER"): return "Accessory (Ignored)"
    
    # Intel Core New Gen
    if re.search(r'\bCORE\s?[U3579]+\b', t): return "Intel Core U/Series"
    if re.search(r'\bINTEL\s?[3579]\s?\d{3}H', t): return "Intel Series"
    if re.search(r'\bU[3579]-\d{3}', t): return "Intel U-Series"
    if re.search(r'\bULTRA\s?[579]\b', t): return "Intel Ultra"
    
    # Intel N-Series
    if re.search(r'\bN\d{3,4}\b', t) or re.search(r'\bN95\b', t): return "Intel N-Series"
    
    # Intel Core i-Series
    if re.search(r'\bI9\b', t): return "Intel Core i9"
    if re.search(r'\bI7\b', t): return "Intel Core i7"
    if re.search(r'\bI5\b', t): return "Intel Core i5"
    if re.search(r'\bI3\b', t): return "Intel Core i3"
    
    # AMD Ryzen AI
    if "RYZEN AI" in t or re.search(r'\bAI\s?9\b', t): return "Ryzen AI"
    
    # Intel Underscore Typos
    if re.search(r'I[3579]_\d{3,5}', t): return "Intel Typo Fixed"
    
    # Intel Generation Detect
    if re.search(r'\d{1,2}(È|TH|ND|RD)?\s?G(É|E)N', t) and "RYZEN" not in t and "AMD" not in t: return "Intel Core Implied"

    # AMD Ryzen Standard (and Typos/Shortcodes)
    if re.search(r'RYZEN\s?9', t) or re.search(r'RAYZEN\s?9', t) or re.search(r'\bR[-_]?9\b', t) or re.search(r'AMD\s?9', t): return "Ryzen 9"
    if re.search(r'RYZEN\s?7', t) or re.search(r'RAYZEN\s?7', t) or re.search(r'\bR[-_]?7\b', t) or re.search(r'AMD\s?7', t): return "Ryzen 7"
    if re.search(r'RYZEN\s?5', t) or re.search(r'RAYZEN\s?5', t) or re.search(r'\bR[-_]?5\b', t) or re.search(r'AMD\s?5', t): return "Ryzen 5"
    if re.search(r'RYZEN\s?3', t) or re.search(r'RAYZEN\s?3', t) or re.search(r'\bR[-_]?3\b', t) or re.search(r'AMD\s?3', t): return "Ryzen 3"
    
    # AMD Specific Models
    if "M1502YA" in t or "M1605YA" in t or "M3500" in t: return "Ryzen 7"
    
    # AMD Budget / Legacy
    if re.search(r'\b3050U\b', t) or "ATHLON" in t: return "Athlon"
    if re.search(r'A[469]-\d{4}', t): return "AMD A-Series"
    if "AMD" in t and "INTEL" not in t: return "AMD Generic"

    if "CELERON" in t: return "Celeron"
    if "PENTIUM" in t: return "Pentium"
    if "ATOM" in t: return "Atom"
    if "XEON" in t: return "Xeon"
    
    if re.search(r'QUAD[\s-]CORE', t): return "Quad Core"
    if re.search(r'DUAL[\s-]CORE', t): return "Dual Core"
    
    # --- MODEL BASED INFERENCE (Last Resort) ---
    if "VICTUS" in t and re.search(r'1[56]-FA', t): return "Intel Core i5"
    if "VICTUS" in t and re.search(r'1[56]-FB', t): return "Ryzen 5"
    if re.search(r'15-(FD|DA|DW|DY)', t): return "Intel Core"
    if re.search(r'15-(FC|EQ|GW)', t): return "Ryzen 5"
    if "D415DA" in t: return "Ryzen 3"
    if "X543MA" in t: return "Celeron"
    if "MATEBOOK" in t: return "Intel Core"
    
    if "MACBOOK" in t: return "Apple M-Series"
    
    return "Unknown"

unknowns = []

print("Scanning for Unknown CPUs...")
for fp in files:
    if os.path.exists(fp):
        with open(fp, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                for p in data:
                    title = p.get('name', p.get('title', ''))
                    # Some files might have specs.cpu already
                    existing = p.get('specs', {}).get('cpu', '') if p.get('specs') else ""
                    
                    # My logic:
                    cpu = normalize_cpu(title, existing)
                    if cpu == "Unknown":
                        unknowns.append(f"[{fp}] {title}")
            except:
                pass
    else:
        print(f"Skipping {fp} (Not Found)")

print(f"\nFound {len(unknowns)} items with Unknown CPU:")
for u in unknowns[:50]: # Show first 50
    print(u)
