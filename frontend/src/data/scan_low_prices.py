import json
import os
import glob

data_dir = r"c:\Users\USER\Documents\programmation\frontend\src\data"
files = glob.glob(os.path.join(data_dir, "*_mobiles.json")) + glob.glob(os.path.join(data_dir, "samsung_tunisie.json")) + glob.glob(os.path.join(data_dir, "*_phones.json"))

print(f"Scanning {len(files)} files for low prices (< 50)...")

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for item in data:
            price = item.get('price')
            
            val = 0
            if isinstance(price, (int, float)):
                val = float(price)
            elif isinstance(price, str):
                try:
                    val = float(price)
                except:
                    continue
            
            if 0 < val < 50:
                print(f"File: {os.path.basename(file_path)}, ID: {item.get('id')}, Price: {val}, Raw: {price}")

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
