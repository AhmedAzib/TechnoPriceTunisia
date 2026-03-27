import json
import os

FILES = [
    'src/data/megapc_new.json',
    'src/data/skymil_new.json',
    'src/data/techspace_new.json',
    # 'src/data/mytek_laptops.json' # User mentioned the others specifically
]

def audit():
    print("Auditing Round and High Prices...")
    
    for relative_path in FILES:
        path = os.path.join(os.path.dirname(__file__), relative_path)
        if not os.path.exists(path):
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        suspicious = []
        high = []
        for item in data:
            p = float(item.get('price', 0))
            
            # Check for exactly 1000, 2000, 3000, 4000
            # User said "1.000.000 exactly or 2.000.000"
            # Maybe they mean values that are clean thousands?
            if p > 0 and p % 100 == 0:
                suspicious.append((p, item['title'], item['link']))
            
            # Check for millions
            if p > 50000:
                high.append((p, item['title']))

        if suspicious or high:
            print(f"\n--- {relative_path} ---")
            if high:
                print(f"FOUND {len(high)} HIGH PRICES (> 50k):")
                for h in high[:5]: print(f"  {h[0]} - {h[1]}")
            
            if suspicious:
                print(f"FOUND {len(suspicious)} ROUND PRICES (Multiple of 100):")
                for s in suspicious[:10]: 
                    print(f"  {s[0]} - {s[1]}")
                    print(f"  Link: {s[2]}")

if __name__ == "__main__":
    audit()
