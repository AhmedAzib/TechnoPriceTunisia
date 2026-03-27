import json
import collections

FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\spacenet_motherboards.json"

try:
    with open(FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Total Products: {len(data)}")

    sockets = collections.Counter()
    chipsets = collections.Counter()
    form_factors = collections.Counter()
    brands = collections.Counter()
    statuses = collections.Counter()

    unknown_socket_titles = []

    for p in data:
        specs = p.get('specs', {})
        sockets[specs.get('socket', 'Unknown')] += 1
        chipsets[specs.get('chipset', 'Unknown')] += 1
        form_factors[specs.get('form_factor', 'Unknown')] += 1
        brands[specs.get('brand', 'Unknown')] += 1
        statuses[p.get('status', 'Unknown')] += 1
        
        if specs.get('socket') == 'Unknown':
            unknown_socket_titles.append(p['title'])

    print("\n--- Stock Status ---")
    for k, v in statuses.items():
        print(f"{k}: {v}")

    print("\n--- Sockets ---")
    for k, v in sockets.most_common():
        print(f"{k}: {v}")

    print("\n--- Chipsets ---")
    for k, v in chipsets.most_common():
        print(f"{k}: {v}")
        
    print("\n--- Form Factors ---")
    for k, v in form_factors.most_common():
        print(f"{k}: {v}")

    print("\n--- Brands ---")
    for k, v in brands.most_common():
        print(f"{k}: {v}")

    if unknown_socket_titles:
        print("\n--- Models with Unknown Socket ---")
        for t in unknown_socket_titles:
            print(f"- {t}")

    unknown_brand_titles = [p['title'] for p in data if p['specs'].get('brand') == 'Unknown']
    if unknown_brand_titles:
        print("\n--- Models with Unknown Brand ---")
        for t in unknown_brand_titles:
            print(f"- {t}")

    unknown_ff_titles = [p['title'] for p in data if p['specs'].get('form_factor') == 'Unknown']
    if unknown_ff_titles:
        print("\n--- Models with Unknown Form Factor ---")
        for t in unknown_ff_titles:
            print(f"- {t}")

except Exception as e:
    print(f"Error reading file/verifying: {e}")
