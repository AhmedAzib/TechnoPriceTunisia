
import json
import re

input_file = "frontend/src/data/techtunisia_products.json"

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Original count: {len(data)}")

# exclude keywords
# User specifically requested removing "3 souris and 1 sac"
# We found: 
# - Tapis De Souris ...
# - Tapis Souris ...
# - Sac à dos ...
# We'll filter based on these specific patterns to be safe.

matches_bad = ["tapis souris", "tapis de souris", "sac à dos pour pc"]

cleaned = []
for item in data:
    title_lower = item['title'].lower()
    
    # Check if title STARTS with or contains explicit accessory name
    is_bad = False
    for m in matches_bad:
        if m in title_lower:
            is_bad = True
            print(f"Removing accessory: {item['title']}")
            break
            
    # Also keep the general phone filter but less aggressive
    if not is_bad:
         general_excludes = ["smartphone", "galaxy a", "infinixhot", "redmi note", "tecno spark"]
         if any(gx in title_lower for gx in general_excludes):
             is_bad = True
             print(f"Removing phone: {item['title']}")

    if is_bad:
        continue
        
    cleaned.append(item)

print(f"Cleaned count: {len(cleaned)}")

with open(input_file, 'w', encoding='utf-8') as f:
    json.dump(cleaned, f, indent=2, ensure_ascii=False)
    
print("Saved cleaned data.")
