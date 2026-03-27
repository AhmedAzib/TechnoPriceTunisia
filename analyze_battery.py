import json
import re

JSON_PATH = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"

def get_battery(product):
    specs = product.get("specs", {})
    if specs.get("battery") and specs.get("battery") != "Unknown":
        return specs.get("battery")
        
    title = product.get("title", "").lower()
    match = re.search(r'(\d{4})\s*mah', title)
    if match:
        return f"{match.group(1)} mAh"
        
    return "Unknown"

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    counts = {}
    unknowns = []
    
    for p in data:
        bat = get_battery(p)
        counts[bat] = counts.get(bat, 0) + 1
        if bat == "Unknown":
            unknowns.append(p["title"])
            
    print("Battery Counts:")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")
        
    print(f"\nUnknowns ({len(unknowns)}):")
    for u in unknowns[:50]:
        print(f"  {u}")

if __name__ == "__main__":
    main()
