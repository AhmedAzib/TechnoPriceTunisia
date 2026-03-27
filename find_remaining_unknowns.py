import json
import re

JSON_PATH = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"

def infer_screen(product):
    title = product.get("title", "").lower()
    specs = product.get("specs", {})
    screen = specs.get("screen", "Unknown")
    
    # Simulate the "Existing Data" check (if data was there, we rely on it)
    if screen != "Unknown":
        return screen

    # Simulate MobilesPage.jsx logic (Updated)
    if 'iphone 16 pro max' in title or 'iphone 15 pro max' in title or 'iphone 14 pro max' in title: return '6.7"'
    if 'iphone 16 plus' in title or 'iphone 15 plus' in title or 'iphone 14 plus' in title: return '6.7"'
    if 'iphone 16' in title or 'iphone 15' in title or 'iphone 14' in title or 'iphone 13' in title: return '6.1"'
    if 'galaxy s24 ultra' in title or 'galaxy s23 ultra' in title: return '6.8"'
    if 'galaxy s24+' in title or 'galaxy s23+' in title: return '6.7"'
    if 'galaxy s24' in title or 'galaxy s23' in title: return '6.1"'
    if 'galaxy a06' in title or 'galaxy a05' in title or 'galaxy a16' in title or 'galaxy a15' in title or 'galaxy a25' in title: return '6.7"'
    if 'galaxy a55' in title or 'galaxy a35' in title or 'galaxy a54' in title or 'galaxy a34' in title: return '6.6"'
    if 'galaxy a' in title: return '6.5"'
    if 'redmi note 13' in title or 'redmi note 12' in title: return '6.67"'
    if 'redmi a3' in title or 'redmi a2' in title: return '6.7"'
    if 'redmi 13' in title or 'redmi 12' in title: return '6.79"'
    if 'infinix note' in title or 'infinix hot' in title: return '6.78"'
    if 'infinix smart' in title: return '6.6"'
    if 'tecno spark' in title or 'tecno pop' in title: return '6.6"'
    if 'itel' in title: return '6.5"'
    if 'lesia' in title: return '6.5"'
    if 'oppo reno' in title: return '6.7"'
    if 'oppo a' in title: return '6.56"'
    if 'realme c' in title: return '6.74"'
    if 'realme 11' in title or 'realme 12' in title: return '6.7"'
    # New additions
    if 'honor play' in title: return '6.5"'
    if 'honor x5' in title or 'honor x6' in title or 'honor x7' in title or 'honor x8' in title or 'honor x9' in title: return '6.56"'
    if 'vivo y0' in title or 'vivo y1' in title or 'vivo y2' in title: return '6.56"'
    if 'vivo y3' in title or 'vivo y5' in title: return '6.6"'
    if 'redmi a' in title: return '6.52"'
    if 'redmi 15' in title or 'redmi 14' in title: return '6.7"'
    if 'oscal' in title: return '6.5"'
    # if 'tecno spark' in title: return '6.6"' # Duplicate
    if 'blackview' in title: return '6.5"'

    # Regex Fallback - Checking what fails
    title_upper = title.upper()
    # Current Regex in Frontend: /(\d+\.\d+|\d+)\s*(?:PO|INCH|''|")|ECRAN\s*(\d+\.\d+)/
    match = re.search(r'(\d+\.\d+|\d+)\s*(?:PO|INCH|\'\'|")|ECRAN\s*(\d+\.\d+)', title_upper)
    if match:
        return "Regex Match" # We don't care about value, just that it matches
        
    return "Unknown"

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    unknowns = []
    for p in data:
        s = infer_screen(p)
        if s == "Unknown":
            unknowns.append(p["title"])
            
    print(f"Found {len(unknowns)} Remaining Unknowns.")
    print("------------------------------------------------")
    for u in unknowns[:50]:
        print(u)

if __name__ == "__main__":
    main()
