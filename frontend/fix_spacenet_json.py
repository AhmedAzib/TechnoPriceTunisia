
import json
import hashlib

def fix_json():
    input_file = "src/data/spacenet_products.json"
    
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        fixed_data = []
        for item in data:
            # Fix Title
            if 'name' in item:
                item['title'] = item['name']
                del item['name']
            
            # Add ID
            if 'id' not in item:
                # Generate unique ID from link
                item['id'] = hashlib.md5(item['link'].encode('utf-8')).hexdigest()[:12]
                
            # Add specs if missing
            if 'specs' not in item:
                item['specs'] = {
                    "brand": item.get('brand', 'Unknown'),
                    # We can try to guess other specs here but for now just empty object to prevent crashes
                    # The frontend normalizeSpecs handles missing values gracefully mostly
                }
                
            fixed_data.append(item)
            
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(fixed_data, f, indent=4, ensure_ascii=False)
            
        print(f"Fixed {len(fixed_data)} items.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_json()
