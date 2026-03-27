import json

JSON_PATH = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"

def main():
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        all_keys = set()
        for p in data:
            specs = p.get('specs', {})
            for k in specs.keys():
                all_keys.add(k)
                
        print("Available Spec Keys:", sorted(list(all_keys)))
        
        # Print a sample specs object
        if data:
             print("\nSample Specs:", data[0].get('specs'))
             
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
