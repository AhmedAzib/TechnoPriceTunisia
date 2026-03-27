import json
import os

INPUT_FILE = r"frontend\src\data\tunisianet_new.json"
OUTPUT_COMPUTERS = r"frontend\src\data\tunisianet_clean.json" # Safest to create a new one first
OUTPUT_PHONES = r"frontend\src\data\tunisianet_phones.json"

# Strict Phone Filter
PHONE_KEYWORDS = [
    "smartphone", "téléphone", "gsm", "mobile",
    "infinix", "oppo", "vivo", "redmi", "realme",
    "iphone", "tecno", "itel", "nokia", "huawei",
    "honor", "zte", "oscal", "tcl", "lesia", "logicom",
    "galaxy a", "galaxy m", "galaxy s", "galaxy z", "galaxy fold", "galaxy flip"
]

# Safe List (If these are in title, might be okay even if keyword present? No, "Smartphone" is definitive)
# But "Huawei" might be a laptop ("MateBook").
# "Samsung" might be a laptop ("Galaxy Book").
# So for Brand keywords, we check if "Laptop" or "Pc Portable" or "MateBook" or "Book" is absent.

def is_phone(title):
    t = title.lower()
    
    # 1. Definitive Keywords
    definitive = ["smartphone", "téléphone", "gsm"]
    for kw in definitive:
        if kw in t:
            return True
            
    # 2. Brand Logic
    # Infinix: InBook is laptop.
    if "infinix" in t:
        if "inbook" in t: return False
        return True # Default to phone
        
    # Tecno: Megabook is laptop.
    if "tecno" in t:
        if "megabook" in t: return False
        return True
        
    # Samsung: Galaxy Book is laptop.
    if "samsung" in t:
        if "galaxy book" in t or "pc portable" in t: return False
        # Galaxy A/M/S/Z -> Phone
        if any(x in t for x in ["galaxy a", "galaxy m", "galaxy s", "galaxy z", "note"]):
            return True
        # If just "Samsung", be careful. But usually phones have model names.
        
    # Huawei: MateBook is laptop.
    if "huawei" in t:
        if "matebook" in t or "pc portable" in t: return False
        return True
        
    # Xiaomi/Redmi
    if "redmi" in t:
        if "book" in t: return False
        return True
    
    # Other Brands known for ONLY phones in this context
    # Lesia, Itel, Logicom, Oscal, ZTE, TCL, Vivo, Oppo, Realme, Honor
    strict_brands = ["lesia", "itel", "logicom", "oscal", "zte", "tcl", "vivo", "oppo", "realme", "honor", "iphone"]
    for brand in strict_brands:
        if brand in t:
            return True

    return False

def split_data():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    computers = []
    phones = []
    
    print(f"Total Items: {len(data)}")
    
    for item in data:
        if is_phone(item['title']):
            phones.append(item)
        else:
            computers.append(item)
            
    print(f"Computers: {len(computers)}")
    print(f"Phones: {len(phones)}")
    
    with open(OUTPUT_COMPUTERS, 'w', encoding='utf-8') as f:
        json.dump(computers, f, indent=4, ensure_ascii=False)
        
    with open(OUTPUT_PHONES, 'w', encoding='utf-8') as f:
        json.dump(phones, f, indent=4, ensure_ascii=False)
        
    print(f"Saved to {OUTPUT_COMPUTERS} and {OUTPUT_PHONES}")
    
    # Overwrite the 'new' file if successful?
    # User said "delete them... or transform them". 
    # I will just save to 'new' as well to be sure the app picks it up if it uses 'new'.
    with open(INPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(computers, f, indent=4, ensure_ascii=False)
    print(f"Overwritten {INPUT_FILE} with clean data.")

if __name__ == "__main__":
    split_data()
