import json

FILE = 'src/data/mytek_motherboards.json'

def verify():
    try:
        with open(FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    total = len(data)
    missing_slots = []

    for item in data:
        specs = item.get('specs', {})
        if specs.get('mb_slots', 'Unknown') == 'Unknown':
            missing_slots.append(item['title'])

    print(f"Total Items: {total}")
    print(f"Missing Slots: {len(missing_slots)}")
    if missing_slots: 
        print("First 5 missing:")
        for t in missing_slots[:5]:
            print(f" - {t}")

if __name__ == "__main__":
    verify()
