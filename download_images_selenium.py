import json
import os
import time
import re
import base64
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def get_base64_image(driver, url):
    script = """
    var uri = arguments[0];
    var callback = arguments[1];
    var xhr = new XMLHttpRequest();
    xhr.responseType = 'blob';
    xhr.onload = function() {
      var reader = new FileReader();
      reader.onloadend = function() {
        callback(reader.result);
      }
      reader.readAsDataURL(xhr.response);
    };
    xhr.onerror = function() {
      callback(null);
    };
    xhr.open('GET', uri);
    xhr.send();
    """
    return driver.execute_async_script(script, url)

def download_images():
    setup_directories()
    
    # Setup Driver
    options = Options()
    # options.add_argument("--headless=new") # Try non-headless if needed, but start headless
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    # Fake user agent just in case
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Load Main Site to pass Cloudflare/Get Cookies
        print("Connecting to Tdiscount home...")
        driver.get("https://tdiscount.tn/")
        time.sleep(5) # Wait for cloudflare
        
        # Load JSON
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        updated = False
        
        for product in products:
            original_url = product.get('image', '')
            if not original_url or 'http' not in original_url:
                continue
                
            # Filename
            path = urlparse(original_url).path
            ext = os.path.splitext(path)[1]
            if not ext:
                ext = '.jpg'
            
            title_slug = slugify(product['title'])[:50]
            filename = f"{title_slug}{ext}"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            # Download if missing
            if not os.path.exists(filepath):
                print(f"Downloading: {filename}...")
                base64_data = get_base64_image(driver, original_url)
                
                if base64_data:
                    # Remove header "data:image/jpeg;base64,"
                    if ',' in base64_data:
                        header, encoded = base64_data.split(',', 1)
                        data = base64.b64decode(encoded)
                        with open(filepath, 'wb') as f:
                            f.write(data)
                        print("  -> Success")
                    else:
                        print("  -> Invalid Base64 format")
                else:
                    print("  -> Failed to fetch (JS error or timeout)")
            else:
                print(f"Skipping existing: {filename}")
            
            # Update path
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
            
    finally:
        driver.quit()

if __name__ == "__main__":
    download_images()
