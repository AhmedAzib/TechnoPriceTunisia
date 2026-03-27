import json

INPUT_FILE = "tunisianet_computers.json" # The raw scrape (1460 items)
OUTPUT_FILE = r"frontend\src\data\tunisianet_new.json"

def restore():
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Raw Input Items: {len(data)}")
        
        seen_titles = set()
        unique_items = []
        duplicates_removed = 0
        
        for item in data:
            # STRICT Logic: 100% Identical Title
            # We strip whitespace and lowercase, but we DO NOT remove words like "Gamer" or "Pc Portable"
            # This ensures "Pc Portable Lenovo" and "Pc Portable Gamer Lenovo" are seen as DIFFERENT.
            # This ensures "Lenovo 8GB" and "Lenovo 16GB" are seen as DIFFERENT.
            
            title_key = item['title'].strip().lower()
            
            if title_key in seen_titles:
                # print(f"Removing Exact Duplicate: {item['title']}")
                duplicates_removed += 1
                continue
                
            seen_titles.add(title_key)
            unique_items.append(item)
            
        print(f"Exact Duplicates Removed: {duplicates_removed}")
        print(f"Restored Count: {len(unique_items)}")
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(unique_items, f, indent=4, ensure_ascii=False)
            
        print(f"Saved to {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    restore()
