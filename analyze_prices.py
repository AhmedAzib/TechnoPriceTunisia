import json
import os

files = [
    "frontend/src/data/megapc_new.json",
    "frontend/src/data/skymil_new.json",
    "frontend/src/data/techtunisia_products.json"
]

for file_path in files:
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        continue
        
    print(f"--- Analyzing {os.path.basename(file_path)} ---")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        prices = []
        for p in data:
            val = p.get('price', 0)
            if isinstance(val, (int, float)):
                prices.append(val)
            elif isinstance(val, str):
                # Try to clean
                try:
                    clean = float(val.replace(' ', '').replace(',', '').replace('TND', '').replace('DT', ''))
                    prices.append(clean)
                    print(f"Found string price: {val} -> {clean}")
                except:
                    pass
        
        if not prices:
            print("No valid prices found.")
            continue
            
        max_p = max(prices)
        min_p = min(prices)
        avg_p = sum(prices) / len(prices)
        
        print(f"Count: {len(prices)}")
        print(f"Max: {max_p}")
        print(f"Min: {min_p}")
        print(f"Avg: {avg_p:.2f}")
        
        # specific check for user claim
        high_vals = [p for p in prices if p > 10000]
        print(f"Prices > 10,000: {len(high_vals)}")
        if high_vals:
            print(f"Examples: {high_vals[:5]}")
            
    except Exception as e:
        print(f"Error: {e}")
    print("\n")
