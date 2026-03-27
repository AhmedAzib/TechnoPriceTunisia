import json

file_path = 'frontend/src/data/spacenet_products.json'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    seen_ids = set()
    cleaned_data = []
    duplicates_count = 0

    for item in data:
        if item['id'] not in seen_ids:
            seen_ids.add(item['id'])
            cleaned_data.append(item)
        else:
            duplicates_count += 1
            # print(f"Removing duplicate: {item['id']}")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    print(f"Finished. Removed {duplicates_count} duplicates. Remaining items: {len(cleaned_data)}")

except FileNotFoundError:
    print(f"File not found: {file_path}")
except Exception as e:
    print(f"Error: {e}")
