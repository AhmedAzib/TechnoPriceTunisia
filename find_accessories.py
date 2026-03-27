
import json

input_file = "frontend/src/data/techtunisia_products.json"

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total items: {len(data)}")

keywords = ["souris", "sac"]

print("--- POTENTIAL ACCESSORIES ---")
for item in data:
    title = item['title'].lower()
    if any(k in title for k in keywords):
        print(f"[{item['price']}] {item['title']}")
