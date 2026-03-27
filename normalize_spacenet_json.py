import json
import re
import os

file_path = r'c:\Users\USER\Documents\programmation\frontend\src\data\spacenet_products.json'

if not os.path.exists(file_path):
    print(f"Error: File not found at {file_path}")
    exit(1)

with open(file_path, 'r', encoding='utf-8') as f:
    products = json.load(f)

def clean_brand(title, current_brand):
    # Priority: Existing Brand > Title First Word
    # Convert to uppercase
    if current_brand and current_brand != "Unknown":
        b = current_brand.strip().upper()
        if "HEWLETT" in b: return "HP"
        return b
    
    # Fallback to title
    parts = title.split()
    if parts:
        b = parts[0].upper()
        if "HEWLETT" in b: return "HP"
        return b
    return "UNKNOWN"

def extract_ram(title):
    # Look for common RAM sizes: 4, 8, 12, 16, 20, 24, 32, 64 followed by Go or GB
    # Exclude if followed by SSD to avoid confusion (though rare for small sizes)
    match = re.search(r'\b(4|8|12|16|20|24|32|64)\s*(?:Go|GB|G)\b', title, re.IGNORECASE)
    if match:
        return f"{match.group(1)}GB"
    return "Unknown"

def extract_storage(title):
    # Regex for storage: 128, 256, 500, 512, 1000 (1TB)
    # 256Go SSD, 512 Go, 1 To, 1TB
    
    # Check for TB first
    match_tb = re.search(r'\b(1|2)\s*(?:To|TB)\b', title, re.IGNORECASE)
    if match_tb:
        return f"{match_tb.group(1)}TB SSD" # Assume SSD for modern laptops if TB
    
    # Check for GB sizes
    match_gb = re.search(r'\b(128|250|256|500|512)\s*(?:Go|GB)\b', title, re.IGNORECASE)
    if match_gb:
        return f"{match_gb.group(1)}GB SSD"
        
    return "Unknown"
    
def extract_cpu(title):
    title_upper = title.upper()
    if 'N100' in title_upper: return 'Intel N100' # Specific popular one
    if 'CELERON' in title_upper: return 'Celeron'
    if 'I9' in title_upper: return 'Core i9'
    if 'I7' in title_upper: return 'Core i7'
    if 'I5' in title_upper: return 'Core i5'
    if 'I3' in title_upper: return 'Core i3'
    if 'RYZEN 9' in title_upper: return 'Ryzen 9'
    if 'RYZEN 7' in title_upper: return 'Ryzen 7'
    if 'RYZEN 5' in title_upper: return 'Ryzen 5'
    if 'RYZEN 3' in title_upper: return 'Ryzen 3'
    if 'ATHLON' in title_upper: return 'Athlon'
    return "Unknown"

def normalize_price(price_val):
    if isinstance(price_val, (int, float)):
        return float(price_val)
    if isinstance(price_val, str):
        # Remove non-numeric except dot/comma
        # e.g. "1 250,500 DT" -> 1250.5
        clean = re.sub(r'[^\d.,]', '', price_val)
        clean = clean.replace(',', '.')
        try:
            return float(clean)
        except:
            return 0.0
    return 0.0

normalized_count = 0
for p in products:
    title = p.get('title', '')
    if not title: continue
    
    # Initialize specs if missing
    if 'specs' not in p or not isinstance(p['specs'], dict):
        p['specs'] = {}
        
    specs = p['specs']
    
    # 1. Brand
    final_brand = clean_brand(title, p.get('brand'))
    p['brand'] = final_brand
    specs['brand'] = final_brand
    
    # 2. RAM
    # Only overwrite if Unknown or we want to force standardization? 
    # Let's force standardization because extracted data is cleaner (e.g. "8Go" -> "8GB")
    specs['ram'] = extract_ram(title)
        
    # 3. Storage
    specs['storage'] = extract_storage(title)
    
    # 4. CPU
    # Same, force standardization
    specs['cpu'] = extract_cpu(title)
    
    # 5. Price
    p['price'] = normalize_price(p.get('price'))
    
    # 6. Screen (Keep existing or infer?)
    # If "Unknown" try to infer
    if specs.get('screen') == 'Unknown' or not specs.get('screen'):
        if '15.6' in title: specs['screen'] = '15.6"'
        elif '17.3' in title: specs['screen'] = '17.3"'
        elif '14' in title: specs['screen'] = '14.0"'
        elif '13.3' in title: specs['screen'] = '13.3"'
        else: specs['screen'] = 'Unknown'

    normalized_count += 1

# Save back
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=2, ensure_ascii=False)

print(f"Successfully normalized {normalized_count} products in {file_path}")
print("Sample product:")
print(json.dumps(products[0], indent=2, ensure_ascii=False))
