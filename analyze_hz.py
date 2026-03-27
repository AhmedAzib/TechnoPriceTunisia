import json
import re

JSON_PATH = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"

def get_hz(product):
    title = product.get("title", "").lower()
    
    # 1. Explicit Hz in Title
    match = re.search(r'(\d+)\s*hz', title)
    if match:
        return f"{match.group(1)}Hz"
        
    # 2. Heuristic Inference (Draft)
    if 'iphone' in title:
        if 'pro' in title: return "120Hz"
        return "60Hz"
    
    if 'galaxy s' in title: return "120Hz"
    if 'galaxy z' in title: return "120Hz" # Fold/Flip
    
    if 'redmi note' in title:
        if '13' in title or '12' in title or '14' in title: return "120Hz"
        
    if 'infinix' in title:
        if 'note' in title or 'hot 40' in title or 'zero' in title: return "120Hz"
        if 'hot 30' in title: return "90Hz"
        if 'smart' in title: return "90Hz" # Newer ones are 90Hz often
        
    if 'tecno' in title:
        if 'spark 20' in title or 'spark 10' in title: return "90Hz"
        if 'camon' in title or 'pova' in title: return "120Hz"
        
    if 'itel' in title:
        if 'p55' in title or 'a70' in title: return "90Hz" # Often 90Hz now? Need verification
        return "60Hz"
        
    return "Unknown"

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    counts = {}
    unknowns = []
    
    for p in data:
        hz = get_hz(p)
        counts[hz] = counts.get(hz, 0) + 1
        if hz == "Unknown":
            unknowns.append(p["title"])
            
    print("Hz Counts:")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")
        
    print(f"\nUnknowns ({len(unknowns)}):")
    for u in unknowns[:50]:
        print(f"  {u}")

if __name__ == "__main__":
    main()
