import json
import re

JSON_PATH = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"

def infer_hz(product):
    title = product.get("title", "").lower().replace("  ", " ")
    specs = product.get("specs", {})
    hz = specs.get("hz", "Unknown")
    
    if hz != "Unknown":
        return hz

    # Snapshot of MobilesPage.jsx Logic
    t = title
    
    # 120Hz +
    if 'iphone' in t and ('pro' in t or 'promax' in t): return "120Hz"
    if 'galaxy s' in t or 'galaxy z' in t: return "120Hz"
    if 'redmi note' in t: return "120Hz"
    if 'infinix note' in t or 'infinix zero' in t or 'infinix gt' in t: return "120Hz"
    if 'tecno camon' in t or 'tecno pova' in t: return "120Hz"
    if 'galaxy a3' in t or 'galaxy a5' in t: return "120Hz"
    if 'honor 90' in t or 'honor 200' in t or 'honor 400' in t or 'honor x9' in t: return "120Hz"
    if 'xiaomi 14' in t or 'xiaomi 13' in t: return "144Hz"
    if 'realme 11' in t or 'realme 12' in t: return "120Hz"
    
    # 90Hz
    if 'tecno spark' in t or 'tecno pop 9' in t or 'tecno go' in t: return "90Hz"
    if 'infinix hot' in t or 'infinix smart' in t: return "90Hz"
    if 'redmi 1' in t or 'redmi 12' in t or 'redmi 13' in t or 'redmi a' in t: return "90Hz"
    if 'galaxy a1' in t or 'galaxy a2' in t: return "90Hz"
    if 'honor x5' in t or 'honor x6' in t or 'honor x7' in t or 'honor x8' in t: return "90Hz"
    if 'vivo y0' in t or 'vivo y1' in t or 'vivo y2' in t or 'vivo y3' in t: return "90Hz"
    if 'oscal' in t or 'blackview' in t: return "90Hz"
    if 'itel p55' in t or 'itel a70' in t or 'itel s23' in t: return "90Hz"
    
    # 60Hz
    if 'iphone' in t: return "60Hz"
    if 'galaxy a0' in t: return "60Hz"
    if 'lesia' in t or 'itel' in t or 'nokia' in t: return "60Hz"
    if 'honor play' in t: return "60Hz"
    
    # Check explicit Hz in title validation (Regex Fallback in logic?)
    # MobilesPage.jsx doesn't have regex fallback for Hz yet in the snapshot I used.
    # But let's see what's left.
    
    return "Unknown"

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    unknowns = []
    for p in data:
        h = infer_hz(p)
        if h == "Unknown":
            unknowns.append(p["title"])
            
    print(f"Found {len(unknowns)} Remaining Unknowns.")
    print("------------------------------------------------")
    for u in unknowns:
        print(u)

if __name__ == "__main__":
    main()
