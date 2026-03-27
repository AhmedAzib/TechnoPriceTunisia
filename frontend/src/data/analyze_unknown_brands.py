import json
import os
import glob

data_dir = r"c:\Users\USER\Documents\programmation\frontend\src\data"
files = glob.glob(os.path.join(data_dir, "*_mobiles.json")) + glob.glob(os.path.join(data_dir, "samsung_tunisie.json")) + glob.glob(os.path.join(data_dir, "*_phones.json"))

unknown_count = 0
examples = []

print("Scanning for Unknown brands...")

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for item in data:
            brand = item.get('brand', '').strip()
            title = item.get('title', '').strip()
            
            # Match the logic in MobilesPage somewhat (if no brand or Unknown)
            if not brand or brand.lower() == 'unknown':
                unknown_count += 1
                if len(examples) < 100:
                    examples.append(title)

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

print(f"Total Unknown Brands: {unknown_count}")
print("\nFirst 100 examples of titles with Unknown brand:")
for t in examples:
    print(f"- {t}")
