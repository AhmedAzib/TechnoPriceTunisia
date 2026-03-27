import json
import re
import os

def clean_data():
    input_path = 'src/data/spacenet_products.json'
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned_data = []

    # Whitelists and Regex
    brands = ["HP", "Dell", "Lenovo", "Asus", "Acer", "MSI", "Apple", "Samsung", "Huawei", "Microsoft", "Gigabyte"]
    
    for item in data:
        title = item.get('name', '')
        title_upper = title.upper()
        
        # 1. Price Normalization
        # "1 250,000 DT" -> 1250.0
        price_str = item.get('price', '0')
        # Remove non-numeric chars except comma (for decimal)
        # Assuming format like "1 250,000" where space is thousands and comma is decimal
        # Remove all spaces
        price_clean = re.sub(r'\s+|DT|TND', '', price_str) # "1250,000"
        price_clean = price_clean.replace(',', '.') # "1250.000"
        try:
            price = float(price_clean)
        except ValueError:
            price = 0.0

        # 2. Brand Extraction
        brand = "Unknown"
        for b in brands:
            if b.upper() in title_upper:
                brand = b.capitalize() # Normalize casing (HP vs Hp -> let's map carefully if needed)
                if brand == "Hp": brand = "HP"
                if brand == "Msi": brand = "MSI"
                break
        
        # 3. Specs Extraction
        
        # RAM
        ram = "Unknown"
        ram_match = re.search(r'(\d+)\s?(Go|GB)', title, re.IGNORECASE)
        if ram_match:
            ram = f"{ram_match.group(1)}GB"

        # Storage
        storage = "Unknown"
        # Look for SSD pattern first
        ssd_match = re.search(r'(\d+)\s?(Go|GB|To|TB)\s?SSD', title, re.IGNORECASE)
        if ssd_match:
            unit = ssd_match.group(2).upper().replace("GO", "GB").replace("TO", "TB")
            storage = f"{ssd_match.group(1)}{unit} SSD"
        else:
            # Generic storage match if SSD not explicitly mentioned but size is large (likely storage)
            # Avoiding confusion with RAM (usually storage is > 64GB)
            # Actually risky, stick to explicit patterns first or known keywords
            pass
            
        # Screen Size
        screen = "Unknown"
        screen_match = re.search(r'(\d{1,2}[\.,]\d)["\']?', title)
        if screen_match:
            screen = screen_match.group(1).replace(',', '.')
            
        # CPU
        cpu = "Unknown"
        if "I3" in title_upper: cpu = "Core i3"
        elif "I5" in title_upper: cpu = "Core i5"
        elif "I7" in title_upper: cpu = "Core i7"
        elif "I9" in title_upper: cpu = "Core i9"
        elif "RYZEN 3" in title_upper: cpu = "Ryzen 3"
        elif "RYZEN 5" in title_upper: cpu = "Ryzen 5"
        elif "RYZEN 7" in title_upper: cpu = "Ryzen 7"
        elif "CELERON" in title_upper: cpu = "Celeron"
        elif "PENTIUM" in title_upper: cpu = "Pentium"
        elif "N100" in title_upper: cpu = "N100"
        elif "M1" in title_upper: cpu = "Apple M1"
        elif "M2" in title_upper: cpu = "Apple M2"
        elif "M3" in title_upper: cpu = "Apple M3"

        # Category mapping
        category = "Etudiant" # Default fallback
        if "GAMER" in title_upper or "GAMING" in title_upper or "RTX" in title_upper or "GTX" in title_upper or brand == "MSI":
            category = "Gamer"
        elif "PROBOOK" in title_upper or "ELITEBOOK" in title_upper or "THINKPAD" in title_upper or "VOSTRO" in title_upper or "LATITUDE" in title_upper:
            category = "Business"
        elif price > 2500: # Expensive non-gamer/non-business usually premium/business
            category = "Business"

        # Create new structure
        new_item = {
            "id": f"sn-{item.get('link', '').split('/')[-1].replace('.html', '')}", # Generate stable ID from link if possible
            "title": title,
            "price": price,
            "image": item.get('image', ''),
            "link": item.get('link', ''),
            "brand": brand, # Top level brand
            "specs": {
                "brand": brand,
                "cpu": cpu,
                "gpu": "Integrated", # Default
                "ram": ram,
                "storage": storage,
                "hz": "60Hz", # Default
                "screen": screen,
                "res": "FHD", # Default
                "panel": "IPS", # Default
                "os": "FreeDOS", # Default
                "category": category
            },
            "source": "Spacenet"
        }
        cleaned_data.append(new_item)

    # Save Cleaned Data
    output_path = 'src/data/spacenet_products_clean.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    
    # Also overwrite the frontend file directly to save a step
    frontend_path = 'frontend/src/data/spacenet_products.json'
    if os.path.exists('frontend/src/data'):
        with open(frontend_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    print(f"Cleaning complete. Processed {len(cleaned_data)} items.")
    print(f"Saved to {output_path} and {frontend_path}")

if __name__ == "__main__":
    clean_data()
