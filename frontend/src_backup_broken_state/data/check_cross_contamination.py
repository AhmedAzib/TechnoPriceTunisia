import json
import os

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

base_path = r"c:\Users\USER\Documents\programmation\frontend\src\data"
wiki_path = os.path.join(base_path, "wiki_mobiles.json")
spacenet_path = os.path.join(base_path, "spacenet_mobiles.json")

wiki_data = load_json(wiki_path)
spacenet_data = load_json(spacenet_path)

print(f"Wiki items: {len(wiki_data)}")
print(f"SpaceNet items: {len(spacenet_data)}")

# Check for SpaceNet links in Wiki
spacenet_in_wiki = [item for item in wiki_data if "spacenet" in item.get('link', '').lower() or "spacenet" in item.get('title', '').lower()]
print(f"SpaceNet items found in Wiki file: {len(spacenet_in_wiki)}")
for item in spacenet_in_wiki:
    print(f" - Found: {item['title']} ({item['link']})")

# Check for Wiki links in SpaceNet
wiki_in_spacenet = [item for item in spacenet_data if "wiki" in item.get('link', '').lower() or "wiki" in item.get('title', '').lower()]
print(f"Wiki items found in SpaceNet file: {len(wiki_in_spacenet)}")

# Check for ID overlap
wiki_ids = set(item['id'] for item in wiki_data)
spacenet_ids = set(item['id'] for item in spacenet_data)
overlap = wiki_ids.intersection(spacenet_ids)
print(f"ID Overlap Count: {len(overlap)}")
if overlap:
    print(f"Overlapping IDs: {overlap}")
