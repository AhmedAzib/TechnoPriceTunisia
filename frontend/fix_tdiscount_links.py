import json
import re

# Shortened Base Pattern (Let Wordpress handle the redirect)
BASE_URL = "https://tdiscount.tn/produit"

def fix_links():
    path = "src/data/tdiscount_mobiles.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    count = 0
    for p in data:
        old_link = p.get("link", "")
        clean_link = old_link.rstrip("/")
        slug = clean_link.split("/")[-1]
        
        if slug and "tdiscount.tn" not in slug:
             new_link = f"{BASE_URL}/{slug}/"
             if new_link != old_link:
                 p["link"] = new_link
                 count += 1
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print(f"Shortened {count} Tdiscount links.")

if __name__ == "__main__":
    fix_links()
