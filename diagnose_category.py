import json
import os

# Paths to data files
BASE_DIR = r"c:\Users\USER\Documents\programmation\frontend\src\data"
FILES = [
    "tunisianet_clean.json",
    "spacenet_products.json",
    "mytek_test.json",
    "wiki_clean.json"
]

def load_data(filename):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return []

def main():
    cat_counts = {}
    unknown_examples = []
    total = 0

    print(f"Loading data from {len(FILES)} files...")
    
    for filename in FILES:
        data = load_data(filename)
        for p in data:
            total += 1
            # Check if category exists in root or specs
            cat = p.get('category') or p.get('specs', {}).get('category', 'Unknown')
            
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
            
            if cat == 'Unknown':
                unknown_examples.append({
                    'title': p.get('name', p.get('title', '')),
                    'specs': p.get('specs', {})
                })

    print("-" * 30)
    print(f"Total Products: {total}")
    print("Category Value Distribution:")
    sorted_cat = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)
    for c, count in sorted_cat:
        print(f"'{c}': {count}")

    print("-" * 30)
    print(f"Top 50 Unknown Category Examples:")
    for i, item in enumerate(unknown_examples[:50]):
        # Print valid specs to help us decide classification rules
        gpu = item['specs'].get('gpu', 'N/A')
        cpu = item['specs'].get('cpu', 'N/A')
        print(f"{i+1}. {item['title']} | GPU: {gpu} | CPU: {cpu}")

if __name__ == "__main__":
    main()
