import json

target_titles = [
    "Vivo Y19s",
    "Oppo A5",
    "Honor X7C",
    "Honor 90 Lite",
    "Oppo Reno 14F",
    "Z Flip 3"
]

path = r"c:\Users\USER\Documents\programmation\frontend\src\data\wiki_mobiles.json"

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    for target in target_titles:
        if target.lower() in item['title'].lower():
            print(f"Title: {item['title']}")
            print(f"Image: {item['image'][:100]}...") # Print first 100 chars
            print(f"Link: {item['link']}")
            print("-" * 20)
