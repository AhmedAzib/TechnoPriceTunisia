import json
import os
from collections import Counter

DATA_DIR = r"c:\Users\USER\Documents\programmation\frontend\src\data"

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"Warning: {filename} not found.")
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []

# Simulate MASTER_DATA construction
master_data = []

# tunisianetData
master_data.extend(load_json('tunisianet_new.json'))

# megapcData (gamer + pro)
master_data.extend(load_json('megapc_gamer.json'))
master_data.extend(load_json('megapc_pro.json'))

# skymilData
master_data.extend(load_json('skymil_new.json'))

# techspaceData
master_data.extend(load_json('techspace_new.json'))

# mytekData
master_data.extend(load_json('mytek_new.json'))
master_data.extend(load_json('mytek_laptops.json'))
master_data.extend(load_json('mytek_mobiles.json'))

# wikiData
master_data.extend(load_json('wiki_products.json'))

# techTunisiaData
master_data.extend(load_json('techtunisia_products.json'))

# spacenetData
master_data.extend(load_json('spacenet_products.json'))

# tdiscountData
master_data.extend(load_json('tdiscount_products.json'))

print(f"Total products in MASTER_DATA: {len(master_data)}")

# Check for duplicates by ID (or Link)
ids = []
links = []
titles = []

for p in master_data:
    # Logic from normalizeProductData: id = p.id || p.link
    uid = p.get('id') or p.get('link')
    ids.append(uid)
    
    if p.get('link'):
        links.append(p.get('link'))
    
    if p.get('name') or p.get('title'):
        titles.append((p.get('name') or p.get('title')).lower().strip())

id_counts = Counter(ids)
link_counts = Counter(links)
title_counts = Counter(titles)

# Top Duplicates
print("\nTop Duplicate IDs:")
for uid, count in id_counts.most_common(10):
    if count > 1:
        print(f"{uid}: {count}")

print("\nTop Duplicate Links:")
for link, count in link_counts.most_common(10):
    if count > 1:
        print(f"{link}: {count}")

print("\nTop Duplicate Titles:")
for title, count in title_counts.most_common(10):
    if count > 1:
        print(f"{title}: {count}")

# Check specific example if possible
target_snippet = "lenovo legion pro 7"
print(f"\nChecking for duplicates containing '{target_snippet}':")
count = 0
for p in master_data:
    t = (p.get('name') or p.get('title') or "").lower()
    if target_snippet in t:
        count += 1
        # print(f"- {t} ({p.get('link')})")
print(f"Total '{target_snippet}': {count}")

target_snippet_2 = "rog strix scar 18"
print(f"\nChecking for duplicates containing '{target_snippet_2}':")
count = 0
for p in master_data:
    t = (p.get('name') or p.get('title') or "").lower()
    if target_snippet_2 in t:
        count += 1
        # print(f"- {t} ({p.get('link')})")
print(f"Total '{target_snippet_2}': {count}")
