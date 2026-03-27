import json
import os
import glob

def clean_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        initial_count = len(data)
        cleaned_data = []
        
        for p in data:
            # Check brand, title, source
            brand = str(p.get('brand', '')).lower()
            title = str(p.get('title', '')).lower()
            
            if "sans marque" in brand or "sans marque" in title:
                continue
            
            cleaned_data.append(p)
            
        removed = initial_count - len(cleaned_data)
        
        if removed > 0:
            print(f"[{os.path.basename(path)}] Removed {removed} items.")
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        else:
            print(f"[{os.path.basename(path)}] Clean.")
            
    except Exception as e:
        print(f"Error {path}: {e}")

files = glob.glob("frontend/src/data/*.json")
for file_path in files:
    clean_file(file_path)
