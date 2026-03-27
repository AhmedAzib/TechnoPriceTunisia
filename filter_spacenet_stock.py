import json

FILE_PATH = r"C:\Users\USER\Documents\programmation\frontend\src\data\spacenet_processors.json"

def main():
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Total items before filter: {len(data)}")
        
        # Filter strictly for 'En Stock'
        in_stock_items = [item for item in data if item.get('status') == 'En Stock']
        
        print(f"Total items after filter ('En Stock'): {len(in_stock_items)}")
        
        # Verify if our fixed items are in there
        # Price check for one of them
        for item in in_stock_items:
            if "3100" in item['title'] and "AMD" in item['brand']:
                print(f"Verification - Ryzen 3100 Price: {item['price']} (Should be 149.0)")
            if "14700K" in item['title'] and "BOX" in item['title']:
                 print(f"Verification - i7-14700K Price: {item['price']} (Should be 1519.0)")

        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(in_stock_items, f, indent=2, ensure_ascii=False)
            
        print("Successfully saved filtered list.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
