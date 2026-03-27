import json
import os

files = [
    "frontend/src/data/megapc_new.json",
    "frontend/src/data/skymil_new.json",
    "frontend/src/data/techtunisia_products.json"
]

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"--- {os.path.basename(file_path)} ---")
        for p in data:
            try:
                price = float(p.get('price', 0))
                if price >= 5000: # Threshold
                    print(f"[{price} TND] {p.get('title')}")
            except:
                pass
        print("\n")
            
    except Exception as e:
        print(f"Error {file_path}: {e}")
