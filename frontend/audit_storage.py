import json

FILE = 'src/data/mytek_motherboards.json'

def audit():
    try:
        with open(FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    print("--- Current Storage Values in JSON ---")
    counts = {}
    details = []
    missing_storage = []

    for item in data:
        title = item.get('title', 'Unknown')
        specs = item.get('specs', {})
        storage = specs.get('mb_storage', 'Unknown')
        
        # Track counts
        counts[storage] = counts.get(storage, 0) + 1
        
        if storage == 'Unknown':
             missing_storage.append(title)
        
        details.append(f"[{storage}] {title}")

    print(f"Value Counts: {counts}")
    print(f"\nMissing Storage: {len(missing_storage)}")
    
    print("\n--- Detailed List ---")
    for d in sorted(details):
        print(d)

if __name__ == "__main__":
    audit()
