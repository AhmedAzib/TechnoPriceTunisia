import json

file_path = "c:/Users/USER/Documents/programmation/frontend/src/data/spacenet_rams.json"

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

overrides = {
    "Barrette Mémoire 4Go DDR4 Pour PC De Bureau": "3200MHz",
    "Barrette Mémoire 8Go DDR4 3200Mz SO-DIMM": "3200MHz",
    "Barrette Mémoire 8Go DDR5 5600Mz SO-DIMM": "5600MHz",
    "Barrette Mémoire Samsung  8 Go DDR5 SODIMM": "4800MHz",
    "Barrette Mémoire Kingston 4Go DDR4 SO-DIMM": "2400MHz",
    "Barrette Mémoire Samsung 4 Go DDR4 3200 AA": "3200MHz",
    "Barrette Mémoire Samsung 8 Go DDR4 3200AA": "3200MHz"
}

fixed_count = 0

for item in data:
    title = item.get("title", "")
    
    # Try exact match first
    freq = overrides.get(title)
    
    # Fallback to loose match just in case
    if not freq:
        for override_title, override_freq in overrides.items():
            if override_title.replace("  ", " ") == title.replace("  ", " "):
                freq = override_freq
                break

    if freq:
        if item["specs"]["frequency"] != freq:
            print(f"Fixing {title} -> {freq}")
            item["specs"]["frequency"] = freq
            fixed_count += 1

print(f"Fixed {fixed_count} items in spacenet_rams.json")

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
