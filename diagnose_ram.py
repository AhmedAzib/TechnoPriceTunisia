import json
import re
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

def normalize_ram_mock(title, specs):
    # Mocking similar logic to current JS to see what we get
    # Note: The JS logic pulls from specs.ram OR title if missing.
    
    ram = specs.get('ram', 'Unknown')
    t = title.upper()
    
    # 1. Extraction if missing
    if not ram or ram == 'Unknown':
        # Simple extract attempt
        match = re.search(r'(\d{1,3})\s?(GO|GB|G)\b', t)
        if match:
            ram = f"{match.group(1)}GB"
            
    # 2. Standardization Logic
    if ram and ram != 'Unknown':
        # Remove whitespace and standardize GO->GB
        ram = str(ram).replace(' ', '').upper().replace('GO', 'GB')
        
        # If just numeric, append GB
        if ram.isdigit():
             ram += "GB"
        
    return ram

def main():
    ram_counts = {}
    
    for filename in FILES:
        data = load_data(filename)
        for p in data:
            title = p.get('name', p.get('title', ''))
            specs = p.get('specs', {})
            
            ram = normalize_ram_mock(title, specs)
            ram_counts[ram] = ram_counts.get(ram, 0) + 1

    print("-" * 30)
    print("RAM Value Distribution:")
    
    # Numeric sort helper
    def sort_key(k):
        try:
            val = str(k[0])
            num = int(re.sub(r'\D', '', val)) if re.search(r'\d', val) else 99999
            return (0, num)
        except:
            return (1, str(k[0]))

    sorted_ram = sorted(ram_counts.items(), key=sort_key)

    for r, count in sorted_ram:
        print(f"'{r}': {count}")

if __name__ == "__main__":
    main()
