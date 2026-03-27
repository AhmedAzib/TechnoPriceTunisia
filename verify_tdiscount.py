import json

def verify():
    path = 'frontend/src/data/tdiscount_products.json'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Total items: {len(data)}")
        
        images_ok = 0
        prices_ok = 0
        titles_ok = 0
        
        for p in data:
            if p.get('image') and p['image'].startswith('/images/'):
                images_ok += 1
            if p.get('price') and p['price'] > 0:
                prices_ok += 1
            if p.get('title'):
                titles_ok += 1
                
        print(f"Images Valid: {images_ok}")
        print(f"Prices Valid: {prices_ok}")
        print(f"Titles Valid: {titles_ok}")
        
    except Exception as e:
        print(f"JSON Error: {e}")

if __name__ == "__main__":
    verify()
