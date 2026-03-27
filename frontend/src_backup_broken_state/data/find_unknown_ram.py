import json
import re
import glob

def load_data():
    files = glob.glob(r'c:\Users\USER\Documents\programmation\frontend\src\data\*_mobiles.json') + \
            glob.glob(r'c:\Users\USER\Documents\programmation\frontend\src\data\*_phones.json')
    all_phones = []
    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                for p in data:
                    p['source_file'] = f
                all_phones.extend(data)
        except Exception as e:
            print(f"Error loading {f}: {e}")
    return all_phones

def parse_ram(phone):
    specs = phone.get('specs', {})
    raw_ram = specs.get('ram', 'Unknown')
    
    # 1. Existing valid RAM? (Simple check: if it has digits and ends in GB/Go and <= 24)
    # This mimics the frontend trying to use existing data first, but generic parsing might be weak in JSON.
    # Let's assume if JSON says "Unknown", we need regex.
    
    if raw_ram != 'Unknown' and raw_ram is not None:
        # Check if it looks valid
        match = re.search(r'(\d+)', str(raw_ram))
        if match:
             val = int(match.group(1))
             if val <= 24 and val != 5: # 5G exclusions
                 return f"{val}GB"

    title = phone.get('title', '').lower()
    
    # Regexes from MobilesPage.jsx
    
    # 1. Slash: 3/64
    m_slash = re.search(r'(\d+)\s*/\s*(\d+)', title)
    if m_slash:
        r = int(m_slash.group(1))
        s = int(m_slash.group(2))
        if r <= 24 and r != 5 and s > r:
            return f"{r}GB (Slash)"

    # 2. Plus: 4+128
    m_plus = re.search(r'(\d+)\s*\+\s*(\d+)', title)
    if m_plus:
        r = int(m_plus.group(1))
        s = int(m_plus.group(2))
        if r <= 24 and r != 5 and s > r:
             return f"{r}GB (Plus)"

    # 3. Hyphen: 6-128
    m_hyphen = re.search(r'(\d+)\s*-\s*(\d+)', title)
    if m_hyphen:
        r = int(m_hyphen.group(1))
        s = int(m_hyphen.group(2))
        if r <= 24 and r != 5 and s > r:
             return f"{r}GB (Hyphen)"
             
    # 4. Concatenated: 4Go128Go
    m_concat = re.search(r'(\d+)go(\d+)go', title)
    if m_concat:
        r = int(m_concat.group(1))
        s = int(m_concat.group(2))
        return f"{r}GB (Concat)"

    # 5. Short G: 6G 128G
    m_short = re.search(r'(\d+)g\s*[\/\s]*\s*(\d+)', title)
    if m_short:
        r = int(m_short.group(1))
        # s = int(m_short.group(2))
        if r <= 24 and r != 5:
             return f"{r}GB (Short G)"

    return "Unknown"

phones = load_data()
unknowns = []

for p in phones:
    res = parse_ram(p)
    if res == "Unknown":
        # Check exclusion context
        t_lower = p.get('title', '').lower()
        if 'bicyclette' in t_lower or 'pc portable' in t_lower:
            continue
            
        unknowns.append({
            'title': p['title'],
            'price': p.get('price', 0),
            'brand': p.get('brand', 'Unknown')
        })

# Sort by Price Descending to see the "3999" ones
unknowns.sort(key=lambda x: x['price'], reverse=True)

print(f"Total Unknown RAM (Filtered): {len(unknowns)}")
print("-" * 60)
print(f"{'Price':<10} | {'Brand':<15} | {'Title'}")
print("-" * 60)
for u in unknowns[:40]: # Top 40 pricey ones
    print(f"{str(u['price']):<10} | {u['brand']:<15} | {u['title']}")
