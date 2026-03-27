import json
import os

files = [
    "frontend/src/data/megapc_new.json",
    "frontend/src/data/skymil_new.json"
]

for path in files:
    if not os.path.exists(path): continue
    print(f"--- {os.path.basename(path)} ---")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    suspicious = []
    for p in data:
        price = p.get('price', 0)
        try:
            val = float(price)
            # Check if exactly 1000, 2000, 3000... or generally too round
            if val > 0 and val % 1000 == 0:
                suspicious.append(p)
        except:
            pass
            
    print(f"Total: {len(data)}")
    print(f"Suspicious (Exact 1000s): {len(suspicious)}")
    if suspicious:
        print("Examples:")
        for x in suspicious[:3]:
            print(f"  {x['price']} - {x['title']}")
