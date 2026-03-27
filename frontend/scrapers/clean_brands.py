
import json
import os

# Define the paths to the data files
DATA_DIR = r"c:\Users\USER\Documents\programmation\frontend\src\data"
FILES_TO_CHECK = [
    "tunisianet_new.json",
    "all_products_new.json",
    "megapc_new.json" 
]

# List of known brands to protect (case-insensitive)
KNOWN_BRANDS = [
    "Lenovo", "HP", "Dell", "Asus", "Acer", "MSI", "Apple", "MacBook", 
    "Lenovo", "HP", "Dell", "Asus", "Acer", "MSI", "Apple", "MacBook", 
    "Samsung", "Huawei", "Infinix", "BMAX", "Chuwi", "Microsoft", 
    "Razer", "Gigabyte", "Alienware", "Thomson", "Ikon", "LG", "Toshiba", "Dynabook",
    # Specific Product Lines that imply a brand
    "EliteBook", "ProBook", "IdeaPad", "ThinkPad", "Vostro", "Latitude", "Precision", "XPS",
    "ZenBook", "VivoBook", "TUF", "ROG", "Legion", "Yoga", "Aspire", "Swift", "Predator", "Nitro",
    "Cyborg", "Katana", "Sword", "Pulse", "Vector", "Crosshair", "Delta", "Alpha", "Bravo",
    "Surface", "MateBook", "MagicBook", "InBook", "MegaBook", "Victus", "Omen", "Pavilion", "Envy", "Spectre"
]

def is_sans_marque(title):
    title_lower = title.lower()
    
    # Explicit "Sans Marque" or "Generique"
    if "sans marque" in title_lower or "générique" in title_lower or "generique" in title_lower:
        return True, "Explicit 'Sans Marque'"

    # Check if it contains any known brand
    # We look for the brand as a whole word to avoid partial matches (e.g., "in" in "fin")
    # simplified check: just existence
    has_brand = any(brand.lower() in title_lower for brand in KNOWN_BRANDS)
    
    if not has_brand:
        return True, "No Known Brand Found"
    
    return False, None

def clean_file(filename, dry_run=True):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    print(f"\nScanning {filename}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return

    original_count = len(data)
    kept_products = []
    removed_products = []

    for product in data:
        title = product.get('title', 'Unknown')
        is_bad, reason = is_sans_marque(title)
        
        if is_bad:
            removed_products.append(f"{title} ({reason})")
        else:
            kept_products.append(product)

    print(f"  Original Count: {original_count}")
    print(f"  To Remove: {len(removed_products)}")
    print(f"  To Keep: {len(kept_products)}")
    
    if removed_products:
        print("  Examples of removals:")
        for p in removed_products[:5]:
            print(f"    - {p}")

    if not dry_run and len(removed_products) > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(kept_products, f, indent=4, ensure_ascii=False)
        print(f"  [SAVED] Updated {filename}")
    elif dry_run and len(removed_products) > 0:
        print(f"  [DRY RUN] Not saving changes.")

if __name__ == "__main__":
    print("Starting Cleanup of 'Sans Marque' Products...")
    for f in FILES_TO_CHECK:
        clean_file(f, dry_run=False)
