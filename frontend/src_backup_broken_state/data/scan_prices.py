import json
import os
import glob

data_dir = r"c:\Users\USER\Documents\programmation\frontend\src\data"
files = glob.glob(os.path.join(data_dir, "*_mobiles.json")) + glob.glob(os.path.join(data_dir, "samsung_tunisie.json"))

print(f"Scanning {len(files)} files...")

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for item in data:
            price = item.get('price')
            
            # Check for non-numeric or weird variants
            try:
                if price is None:
                    print(f"File: {os.path.basename(file_path)}, ID: {item.get('id')}, Price is NULL")
                    continue
                    
                if isinstance(price, (int, float)):
                    continue # Good
                    
                if isinstance(price, str):
                    # Check if it parses cleanly
                    val = float(price) # Python's float handles some things, strictly
                    continue
                    
                print(f"File: {os.path.basename(file_path)}, ID: {item.get('id')}, Price invalid type: {type(price)} Value: {price}")
                
            except Exception as e:
                print(f"File: {os.path.basename(file_path)}, ID: {item.get('id')}, Price ERROR: {price} ({e})")

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
