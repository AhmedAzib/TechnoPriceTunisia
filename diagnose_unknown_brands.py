import json
import re
import os

# Paths to data files
BASE_DIR = r"c:\Users\USER\Documents\programmation\frontend\src\data"
FILES = [
    "tunisianet_clean.json",
    "spacenet_products.json",
    "mytek_test.json",
    "wiki_clean.json"
]

def load_data(filename):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return []

def normalize_brand_mock(brand, title):
    b = str(brand or "").lower().strip()
    t = str(title or "").lower().strip()
    
    def has(keyword):
        return keyword in b or keyword in t

    if has('hp') or has('hewlett') or has('elitebook') or has('pavilion') or has('probook') or has('omen') or has('victus'): return 'HP'
    if has('dell') or has('vostro') or has('latitude') or has('inspiron') or has('xps') or has('alienware') or has('g15'): return 'Dell'
    if has('lenovo') or has('thinkpad') or has('thinkbook') or has('ideapad') or has('yoga') or has('legion') or has('loq'): return 'Lenovo'
    if has('asus') or has('zenbook') or has('vivobook') or has('rog') or has('tuf') or has('expertbook'): return 'Asus'
    if has('msi') or has('katana') or has('cyborg') or has('stealth') or has('raider') or has('thin'): return 'MSI'
    if has('apple') or has('macbook') or has('mac ') or has('imac'): return 'Apple'
    if has('acer') or has('nitro') or has('predator') or has('aspire') or has('swift') or has('extensa'): return 'Acer'
    if has('gigabyte') or has('aorus') or has('aero'): return 'Gigabyte'
    if has('samsung') or has('galaxy book'): return 'Samsung'
    if has('huawei') or has('matebook'): return 'Huawei'
    if has('microsoft') or has('surface'): return 'Microsoft'
    if has('bmax'): return 'BMAX'
    if has('infinix'): return 'Infinix'
    if has('razer') or has('blade'): return 'Razer'
    if has('chuwi'): return 'Chuwi'
    if has('mytek'): return 'MyTek'

    if brand and b not in ['unknown', 'generic', 'autre']:
         return brand.capitalize()
    
    return 'Unknown'

def main():
    unknowns = []
    total = 0
    
    for filename in FILES:
        data = load_data(filename)
        for p in data:
            total += 1
            brand = p.get('brand', 'Unknown')
            title = p.get('name', p.get('title', ''))
            
            # Use the MOCK function
            normalized = normalize_brand_mock(brand, title)
            
            if normalized == "Unknown" or normalized == "Generic":
                unknowns.append(title)

    print(f"Total Products: {total}")
    print(f"Total Unknown Brands: {len(unknowns)}")
    print("-" * 30)
    print("Top 50 Unknown Brand Titles:")
    
    word_freq = {}
    
    for i, t in enumerate(unknowns):
        if i < 50:
             try:
                print(t[:100])
             except:
                print(t[:100].encode('utf-8'))
        
        words = t.upper().split()
        for w in words:
            word_freq[w] = word_freq.get(w, 0) + 1
            
    print("-" * 30)
    print("Most Frequent Words in Unknown Brand Titles:")
    sorted_freq = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    for w, count in sorted_freq[:30]:
        print(f"{w}: {count}")

if __name__ == "__main__":
    main()
