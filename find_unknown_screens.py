import json
import re

JSON_PATH = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"

def infer_screen(product):
    title = product.get("title", "").lower()
    specs = product.get("specs", {})
    screen = specs.get("screen", "Unknown")
    
    if screen != "Unknown":
        return screen
        
    # Replicating MobilesPage.jsx logic
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

    # Regex Fallback
    title_upper = title.upper()
    match = re.search(r'(\d+\.\d+|\d+)\s*(?:PO|INCH|\'\'|")|ECRAN\s*(\d+\.\d+)', title_upper)
    if match:
        size = match.group(1) or match.group(2)
        return f"{size}\""
        
    return "Unknown"

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    unknowns = []
    for p in data:
        s = infer_screen(p)
        if s == "Unknown":
            unknowns.append(p["title"])
            
    print(f"Found {len(unknowns)} Unknowns.")
    print("------------------------------------------------")
    for u in unknowns[:50]:
        print(u)

if __name__ == "__main__":
    main()
