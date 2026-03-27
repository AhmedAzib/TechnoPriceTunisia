import json
import os

file_path = r"c:\Users\USER\Documents\programmation\frontend\src\data\spacenet_motherboards.json"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total items: {len(data)}")
print("-" * 65)
print(f"{'Title':<50} | {'Cap':<8} | {'Speed':<12}")
print("-" * 65)

count_with_speed = 0
# Use substrings to find targets
targets = [
    "BIOSTAR H81M-IDE", "ARKTEK G41", "B760M-P", "B760M-A WIFI", 
    "B760M-A PRO", "PRO B650M-B", "B760M-R", "B760M-A D4", 
    "PRO B650M-P", "B660M-A D4"
]

for p in data:
    specs = p.get("specs", {})
    speed = specs.get("memory_speed", "Unknown")
    cap = specs.get("memory_capacity", "Unknown")
    title = p.get("title", "No Title")
    
    # Check if this product is one of our targets
    is_target = any(t in title.upper() for t in targets)
    
    if is_target:
        print(f"{title[:48]:<50} | {cap:<8} | {speed:<12}")
        if cap != "Unknown":
            count_with_speed += 1

print("-" * 65)
print(f"Target items found: {count_with_speed}")
