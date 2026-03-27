import json
import os

main_file = r"c:\Users\USER\Documents\programmation\frontend\src\data\wiki_mobiles.json"
iphone_file = r"c:\Users\USER\Documents\programmation\frontend\src\data\wiki_iphones.json"

if not os.path.exists(iphone_file):
    print("No iPhone file found.")
    exit()

with open(main_file, 'r', encoding='utf-8') as f:
    main_data = json.load(f)

with open(iphone_file, 'r', encoding='utf-8') as f:
    iphone_data = json.load(f)

# Deduplicate by ID just in case
existing_ids = set(item['id'] for item in main_data)
added_count = 0

for item in iphone_data:
    if item['id'] not in existing_ids:
        main_data.append(item)
        added_count += 1
        print(f"Added: {item['title']}")
    else:
        print(f"Skipped duplicate: {item['title']}")

print(f"Total merged: {added_count}")

with open(main_file, 'w', encoding='utf-8') as f:
    json.dump(main_data, f, indent=4, ensure_ascii=False)

# Clean up
try:
    os.remove(iphone_file)
    print("Deleted temporary iPhone file.")
except:
    pass
