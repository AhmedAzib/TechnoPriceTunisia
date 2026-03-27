import json
import os
import sys
# Add current dir to path to import utils
sys.path.append(os.getcwd())
try:
    from frontend.scrapers.utils import clean_price
except ImportError:
    # prompt path fallback
    sys.path.append(os.path.join(os.getcwd(), 'frontend', 'scrapers'))
    from utils import clean_price

files = [
    "frontend/src/data/megapc_new.json",
    "frontend/src/data/skymil_new.json",
    "frontend/src/data/techtunisia_products.json"
]

for path in files:
    if not os.path.exists(path):
        print(f"Skipping {path}")
        continue
        
    print(f"Fixing {path}...")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        fixed_count = 0
        for p in data:
            old_price = p.get('price')
            
            # Convert string to float if needed using clean_price logic implicitly 
            # (passed as str or float)
            
            # If it's already a float, likely "clean_price" won't string process it
            # so we force string reconversion if it looks huge
            
            val = old_price
            if isinstance(val, (int, float)):
                if val > 50000:
                    val = val / 1000
                    p['price'] = val
                    fixed_count += 1
                # Also handle 200000 cases manually if needed ?? 
                # clean_price > 50000 handles it.
            
            # If it's a string, re-clean
            if isinstance(old_price, str):
                new_val = clean_price(old_price)
                if new_val != old_price: # type change likely
                    p['price'] = new_val
                    fixed_count += 1
                    
        print(f"  Fixed {fixed_count} items")
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error {path}: {e}")

print("Done.")
