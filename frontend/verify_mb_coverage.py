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
    missing_format = []
    missing_speed = []
    missing_type = []
    missing_capacity = []

    for item in data:
        specs = item.get('specs', {})
        if specs.get('format', 'Unknown') == 'Unknown':
            missing_format.append(item['title'])
        if specs.get('memory_speed', 'Unknown') == 'Unknown':
            missing_speed.append(item['title'])
        if specs.get('memory_type', 'Unknown') == 'Unknown':
            missing_type.append(item['title'])
        if specs.get('memory_capacity', 'Unknown') == 'Unknown':
            missing_capacity.append(item['title'])

    print(f"Total Items: {total}")
    print(f"Missing Format: {len(missing_format)}")
    if missing_format: print(missing_format[:5])
    
    print(f"Missing Speed: {len(missing_speed)}")
    if missing_speed: print(missing_speed[:5])

    print(f"Missing Type: {len(missing_type)}")
    if missing_type: print(missing_type[:5])

    print(f"Missing Capacity: {len(missing_capacity)}")
    if missing_capacity: print(missing_capacity[:5])

if __name__ == "__main__":
    verify()
