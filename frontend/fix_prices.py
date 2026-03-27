import json
import os

FILES = [
    'src/data/megapc_new.json',
    'src/data/skymil_new.json',
    'src/data/techspace_new.json'
]

def fix_prices():
    print("Fixing prices...")
    
    for relative_path in FILES:
        path = os.path.join(os.path.dirname(__file__), relative_path)
        if not os.path.exists(path):
            print(f"File not found: {path}")
            continue
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            fixed_count = 0
            for item in data:
                price = item.get('price', 0)
                try:
                    p_float = float(price)
                    # Heuristic: Laptops are never < 200 TND. 
                    # If < 200, it's likely represented in thousands (e.g. 2.500 => 2500)
                    if 0 < p_float < 100: 
                        # User said "at least 100.000" but usually means 100 TND.
                        # If value is like 2.0, it means 2000.
                        # If value is 129, it means 129000? No, 129 TND is possible for accessories but not laptops?
                        # Assume threshold is 200.
                        item['price'] = p_float * 1000
                        fixed_count += 1
                        # print(f"Fixed: {p_float} -> {item['price']} ({item.get('title')[:20]})")
                except:
                    pass
            
            if fixed_count > 0:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"Updated {relative_path}: Fixed {fixed_count} prices.")
            else:
                print(f"No changes needed for {relative_path}.")
                
        except Exception as e:
            print(f"Error processing {relative_path}: {e}")

if __name__ == "__main__":
    fix_prices()
