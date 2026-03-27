import json
import os
import requests
import re
import time
from urllib.parse import urlparse

# Constants
JSON_PATH = 'frontend/src/data/tdiscount_products.json'
OUTPUT_DIR = 'frontend/public/images/tdiscount'
WEB_PATH_PREFIX = '/images/tdiscount'

def setup_directories():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

def download_images():
    setup_directories()
    
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    updated = False
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://tdiscount.tn/'
    }

    for product in products:
        original_url = product.get('image', '')
        if not original_url or 'http' not in original_url:
            continue
            
        # Extension
        path = urlparse(original_url).path
        ext = os.path.splitext(path)[1]
        if not ext:
            ext = '.jpg'
        
        # Filename
        title_slug = slugify(product['title'])[:50] # Limit length
        filename = f"{title_slug}{ext}"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Download
        if not os.path.exists(filepath):
            try:
                print(f"Downloading: {filename} from {original_url}")
                response = requests.get(original_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    print("  -> Success")
                else:
                    print(f"  -> Failed: {response.status_code}")
                    continue
            except Exception as e:
                print(f"  -> Error: {e}")
                continue
        else:
            print(f"Skipping existing: {filename}")
        
        # Update JSON
        new_path = f"{WEB_PATH_PREFIX}/{filename}"
        if product['image'] != new_path:
            product['image'] = new_path
            updated = True
            
    if updated:
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        print("Updated JSON with local image paths.")
    else:
        print("No changes to JSON.")

if __name__ == "__main__":
    download_images()
