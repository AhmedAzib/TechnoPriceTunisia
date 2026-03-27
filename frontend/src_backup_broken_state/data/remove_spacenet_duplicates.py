import json
import os

file_path = r"c:\Users\USER\Documents\programmation\frontend\src\data\spacenet_mobiles.json"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Original count: {len(data)}")
    
    seen_ids = set()
    unique_data = []
    
    for item in data:
        item_id = item.get('id')
        if item_id not in seen_ids:
            seen_ids.add(item_id)
            unique_data.append(item)
            
    print(f"Unique count: {len(unique_data)}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(unique_data, f, indent=4, ensure_ascii=False)
        
    print("Duplicates removed.")

except Exception as e:
    print(f"Error: {e}")
