import json
import os
import glob

data_dir = r"c:\Users\USER\Documents\programmation\frontend\src\data"
files = glob.glob(os.path.join(data_dir, "*_mobiles.json")) + glob.glob(os.path.join(data_dir, "samsung_tunisie.json"))

print(f"Scanning {len(files)} files for duplicates...")

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        original_count = len(data)
        seen_ids = set()
        unique_data = []
        
        for item in data:
            item_id = item.get('id')
            if item_id not in seen_ids:
                seen_ids.add(item_id)
                unique_data.append(item)
        
        unique_count = len(unique_data)
        
        if unique_count < original_count:
            print(f"File: {os.path.basename(file_path)} - Removing {original_count - unique_count} duplicates.")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(unique_data, f, indent=4, ensure_ascii=False)
        else:
            print(f"File: {os.path.basename(file_path)} - No duplicates.")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
