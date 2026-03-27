import json
import re

FILE = r"frontend\src\data\tunisianet_clean.json"

def normalize(title):
    t = title.lower()
    # Remove common prefixes/suffixes
    t = t.replace("pc portable", "").replace("ordinateur portable", "")
    t = t.replace("pc de bureau", "").replace("ordinateur de bureau", "")
    t = t.replace("gamer", "").replace("tunisie", "")
    t = t.replace("  ", " ").strip()
    return t

def inspect():
    with open(FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Total Items: {len(data)}")
    
    seen_titles = {}
    duplicates = []
    
    # Check "Copy" items
    copy_items = [x for x in data if x['title'].lower().startswith("copy")]
    print(f"\nItems starting with 'Copy': {len(copy_items)}")
    for c in copy_items:
        print(f" - {c['title']}")

    # Check Duplicates
    for item in data:
        norm = normalize(item['title'])
        if norm in seen_titles:
            duplicates.append((item, seen_titles[norm]))
        else:
            seen_titles[norm] = item
            
    print(f"\nPotential Duplicates found: {len(duplicates)}")
    
    # Print sample duplicates
    print("\nSample Duplicates (First 10):")
    for i in range(min(10, len(duplicates))):
        new_item, old_item = duplicates[i]
        print(f"1. {old_item['title']} (Ref: {old_item.get('link')})")
        print(f"2. {new_item['title']} (Ref: {new_item.get('link')})")
        print("-" * 20)

if __name__ == "__main__":
    inspect()
