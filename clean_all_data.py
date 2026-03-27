import json
import os

def clean_all_data():
    base_dir = 'frontend/src/data'
    tunisianet_path = os.path.join(base_dir, 'products.json')
    spacenet_path = os.path.join(base_dir, 'spacenet_products.json')

    brand_map = {
        "HP": "HP", "HEWLETT PACKARD": "HP",
        "MSI": "MSI",
        "LG": "LG",
    }
    
    # Helper to normalize brand
    def normalize_brand(b):
        if not b: return "Unknown"
        b = b.strip()
        upper = b.upper()
        if upper in brand_map:
            return brand_map[upper]
        return b.title() # Default to Title Case: "Lenovo", "Asus"

    # 1. Clean Tunisianet
    if os.path.exists(tunisianet_path):
        print(f"Cleaning {tunisianet_path}...")
        with open(tunisianet_path, 'r', encoding='utf-8') as f:
            t_data = json.load(f)
        
        for item in t_data:
            # Normalize Brand
            raw_brand = item.get('brand', '')
            if not raw_brand:
                # Try infer from specs
                raw_brand = item.get('specs', {}).get('brand', '')
            
            clean_brand = normalize_brand(raw_brand)
            item['brand'] = clean_brand
            if 'specs' in item:
                item['specs']['brand'] = clean_brand
            
            # Ensure price is number
            if isinstance(item.get('price'), str):
                try:
                    item['price'] = float(item['price'].replace(',', '.').replace('DT', '').replace(' ', ''))
                except:
                    item['price'] = 0.0

        with open(tunisianet_path, 'w', encoding='utf-8') as f:
            json.dump(t_data, f, ensure_ascii=False, indent=2)
        print(f"Tunisianet cleaned: {len(t_data)} items.")

    # 2. Clean Spacenet
    if os.path.exists(spacenet_path):
        print(f"Cleaning {spacenet_path}...")
        with open(spacenet_path, 'r', encoding='utf-8') as f:
            s_data = json.load(f)
        
        for item in s_data:
            # Normalize Brand
            clean_brand = normalize_brand(item.get('brand', ''))
            item['brand'] = clean_brand
            if 'specs' in item and isinstance(item['specs'], dict):
                item['specs']['brand'] = clean_brand
            
            # Ensure source is consistent (though code adds it, doing it here doesn't hurt)
            item['source'] = 'Spacenet'

        with open(spacenet_path, 'w', encoding='utf-8') as f:
            json.dump(s_data, f, ensure_ascii=False, indent=2)
        print(f"Spacenet cleaned: {len(s_data)} items.")

    print("Data cleaning complete. Filters should now simply merge 'HP' and 'Hp'.")

if __name__ == "__main__":
    clean_all_data()
