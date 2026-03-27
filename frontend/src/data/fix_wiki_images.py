import json
import re
import os

path = r"c:\Users\USER\Documents\programmation\frontend\src\data\wiki_mobiles.json"
backup_path = r"c:\Users\USER\Documents\programmation\frontend\src\data\wiki_mobiles.json.bak"

# 1. Create Backup
if not os.path.exists(backup_path):
    import shutil
    shutil.copy2(path, backup_path)

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Targets based on user report
targets = [
    "Vivo Y19s",
    "Oppo A5",
    "Honor X7C",
    "Honor 90 Lite",
    "Oppo Reno 14F",
    "Galaxy Z Flip 3"
]

count = 0
for item in data:
    title = item['title']
    old_img = item['image']
    
    # Check if this is one of the broken items OR just generally try to fix generic suffix logic
    # But let's prioritize the targets to avoid breaking others
    is_target = any(t.lower() in title.lower() for t in targets)
    
    if is_target:
        # Regex to remove -300x300 pattern at end
        # Example: image.jpg -> image.jpg
        # Example: image-300x300.jpg -> image.jpg
        new_img = re.sub(r'-\d+x\d+(\.\w+)$', r'\1', old_img)
        
        if new_img != old_img:
            print(f"Fixing: {title}")
            print(f"  Old: {old_img}")
            print(f"  New: {new_img}")
            item['image'] = new_img
            count += 1

print(f"Total images fixed: {count}")

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
