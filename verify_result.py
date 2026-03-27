import json

FILE = "tunisianet_computers.json"

try:
    with open(FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Total Items: {len(data)}")
    
    # Check for phones
    phone_keywords = ["smartphone", "téléphone", "gsm", "infinix", "oppo", "vivo", "redmi", "realme"]
    phones_found = 0
    for item in data:
        t = item['title'].lower()
        for kw in phone_keywords:
            if kw in t:
                # print(f"WARNING: Possible phone found: {item['title']}")
                phones_found += 1
                break
                
    print(f"Phones Found (False Positives?): {phones_found}")
    
    # Check sample
    print("Sample items:")
    for i in range(3):
        print(f" - {data[i]['title']} ({data[i]['price']} DT)")
        
except Exception as e:
    print(f"Error reading file: {e}")
