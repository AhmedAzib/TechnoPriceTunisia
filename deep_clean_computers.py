import json

INPUT_FILE = r"frontend\src\data\tunisianet_clean.json"
OUTPUT_FILE = r"frontend\src\data\tunisianet_clean_v2.json"

def normalize(title):
    t = title.lower()
    t = t.replace("pc portable", "").replace("ordinateur portable", "")
    t = t.replace("pc de bureau", "").replace("ordinateur de bureau", "")
    t = t.replace("gamer", "").replace("tunisie", "")
    t = t.replace("  ", " ").strip()
    return t

def clean():
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Total Input: {len(data)}")
        
        seen_titles = set()
        unique_items = []
        duplicates_removed = 0
        
        for item in data:
            title = item['title']
            
            # 1. Filter "Copy"
            if title.lower().startswith("copy"):
                print(f"Removed Copy: {title}")
                continue
                
            # 2. Strict Deduplication by Normalized Title
            norm_title = normalize(title)
            
            if norm_title in seen_titles:
                duplicates_removed += 1
                continue
                
            seen_titles.add(norm_title)
            unique_items.append(item)
            
        print(f"Duplicates Removed: {duplicates_removed}")
        print(f"Final Count: {len(unique_items)}")
        
        # Save
        with open(INPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(unique_items, f, indent=4, ensure_ascii=False)
            
        print(f"Overwritten {INPUT_FILE} with strict unique data.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clean()
