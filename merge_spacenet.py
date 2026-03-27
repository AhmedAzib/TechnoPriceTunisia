import json
import os

# Paths
OLD_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\spacenet_processors.json"
NEW_FILE = r"C:\Users\USER\Documents\programmation\spacenet_full_dump.json"
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\spacenet_processors.json"

def normalize_key(title):
    return title.strip().lower()

def main():
    # 1. Load Manual Fixes (Old File)
    manual_fixes = {}
    fix_keys = [
        "PROCESSEUR AMD RYZEN™ 3 3100 3.9 GHZ SOCKET AM4 TRAY",
        "PROCESSEUR INTEL CORE I5-650 3.4GHZ SOCKET FCLGA 1156 VERSION TRAY SANS VENTILATEUR",
        "PROCESSEUR INTEL® CORE™ I9-11900F 5.20 GHZ TRAY",
        "PROCESSEUR INTEL CORE I7 14700 5.4 GHZ FCLGA 1700 TRAY",
        "PROCESSEUR INTEL CORE I7-13700K 5.4GHZ SOCKET FCLGA 1700 TRAY",
        "PROCESSEUR INTEL CORE I7-14700K 5.6 GHZ LGA 1700 BOX"
    ]
    
    try:
        with open(OLD_FILE, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
            for item in old_data:
                k = normalize_key(item['title'])
                if k in [normalize_key(x) for x in fix_keys]:
                    manual_fixes[k] = item
                    print(f"Captured Fix: {item['title']} -> {item['price']} DT")
    except Exception as e:
        print(f"Error loading old file: {e}")

    # 2. Load Full Scrape
    all_items = []
    seen_links = set()
    
    try:
        with open(NEW_FILE, 'r', encoding='utf-8') as f:
            new_data = json.load(f)
            print(f"Loaded {len(new_data)} items from dump.")
            
            for item in new_data:
                link = item['link']
                if link in seen_links: continue
                seen_links.add(link)
                
                # Check for fix
                k = normalize_key(item['title'])
                if k in manual_fixes:
                    # Use the fixed version (price & logic) but maybe update details?
                    # The fixed version has the correct PRICE. The new version might have better SPECS/DESC.
                    # User said "clean them and make sure there details are 100% clean".
                    # But user also gave EXACT prices.
                    # I will use the NEW item structure (better specs?) but OVERWRITE the Price/Status with the FIX.
                    fixed_item = manual_fixes[k]
                    item['price'] = fixed_item['price']
                    item['status'] = fixed_item['status'] # Keep "En Stock" if fixed
                    # Also keep specs if they differ? 
                    # The scraper was "enhanced". Let's trust scraper specs but FORCE PRICE.
                    print(f"Applying Fix to: {item['title']}")
                
                all_items.append(item)
    except Exception as e:
        print(f"Error loading dump: {e}")

    print(f"Total Unique Items: {len(all_items)}")
    
    # 3. Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)
    print("Done.")

if __name__ == "__main__":
    main()
