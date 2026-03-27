import json
import os
import glob
import re

data_dir = r"c:\Users\USER\Documents\programmation\frontend\src\data"
files = glob.glob(os.path.join(data_dir, "*_mobiles.json")) + glob.glob(os.path.join(data_dir, "samsung_tunisie.json")) + glob.glob(os.path.join(data_dir, "*_phones.json"))

unknown_count = 0
examples = []

print("Scanning for Unknown CPUs...")

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for item in data:
            specs = item.get('specs', {})
            cpu = specs.get('cpu', 'Unknown')
            title = item.get('title', '').strip()
            
            if not cpu or cpu == 'Unknown':
                unknown_count += 1
                if len(examples) < 100:
                    examples.append(title)

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

print(f"Total Unknown CPUs: {unknown_count}")
print("\nFirst 100 examples of titles with Unknown CPU:")
for t in examples:
    print(f"- {t}")
