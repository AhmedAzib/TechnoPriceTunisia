import json

with open("sbs_motherboards.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total Scraped: {len(data)}")
for p in data:
    print(p["title"])
