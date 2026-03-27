import os
import time
import json
import re
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# Output Path
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'src', 'data', 'mytek_laptops.json')

# Helper to Extract Specs from Title
def parse_specs(title):
    specs = {
        "cpu": "Unknown",
        "ram": "Unknown", 
        "storage": "Unknown",
        "gpu": "Unknown",
        "screen": "Unknown"
    }
    t = title.upper()
    
    # HEURISTIC PARSING for RAM & Storage
    matches = re.findall(r'(\d+)\s*(GO|TO)\s*(SSD|HDD)?', t)
    
    for val, unit, suffix in matches:
        try:
            v_int = int(val)
            formatted = ""
            
            # Normalize to GB
            if unit == 'TO': 
                if v_int == 1: v_int = 1024
                elif v_int == 2: v_int = 2048
                formatted = f"{v_int}GB"
            else:
                formatted = f"{v_int}GB"
            
            # Logic
            if suffix in ['SSD', 'HDD']:
                specs['storage'] = formatted
            else:
                if unit == 'TO':
                    specs['storage'] = formatted
                elif v_int in [4, 6, 8, 12, 16, 20, 24, 32, 40, 48, 64]:
                    if specs['ram'] == 'Unknown':
                        specs['ram'] = formatted
                elif v_int >= 120:
                    if specs['storage'] == 'Unknown':
                         specs['storage'] = formatted
        except:
             pass

    # CPU Heuristics
    if "ULTRA 9" in t: specs['cpu'] = "Intel Core Ultra 9"
    elif "ULTRA 7" in t: specs['cpu'] = "Intel Core Ultra 7"
    elif "ULTRA 5" in t: specs['cpu'] = "Intel Core Ultra 5"
    elif "ULTRA" in t: specs['cpu'] = "Intel Core Ultra"
    elif "I9" in t: specs['cpu'] = "Intel Core i9"
    elif "I7" in t: specs['cpu'] = "Intel Core i7"
    elif "I5" in t: specs['cpu'] = "Intel Core i5"
    elif "I3" in t: specs['cpu'] = "Intel Core i3"
    elif "RYZEN 9" in t: specs['cpu'] = "AMD Ryzen 9"
    elif "RYZEN 7" in t: specs['cpu'] = "AMD Ryzen 7"
    elif "RYZEN 5" in t: specs['cpu'] = "AMD Ryzen 5"
    
    return specs

def clean_price(price_str):
    try:
        clean = re.sub(r'[^\d,.]', '', price_str)
        clean = clean.replace(',', '.')
        return float(clean)
    except:
        return 0.0

def scrape():
    print("VERSION: Ultrabook 1.0 - Upsert Mode")
    print("Launching MyTek Ultrabook Scraper...")
    
    # Load Existing Data
    existing_data = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                print(f"Loaded {len(existing_data)} existing items.")
        except:
            print("Could not load existing file. Starting fresh.")
    
    existing_ids = {item['id'] for item in existing_data}

    # Setup Driver
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--blink-settings=imagesEnabled=false')
    
    driver = uc.Chrome(options=options)
    
    base_url = "https://www.mytek.tn/informatique/ordinateurs-portables/ultrabook.html"
    
    new_items_count = 0
    
    try:
        for page in range(1, 5): # Small category
            url = f"{base_url}?p={page}"
            print(f"Scraping Page {page}: {url}")
            driver.get(url)
            
            time.sleep(random.uniform(3, 5))
            
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            products = driver.execute_script("""
                const items = [];
                document.querySelectorAll('div.product-container').forEach((el, index) => {
                    try {
                        const nameEl = el.querySelector('.product-item-name a');
                        const priceEl = el.querySelector('.price-box .final-price');
                        const imgEl = el.querySelector('.product-item-photo img');
                        const stockEl = el.querySelector('.stock.availables span') || el.querySelector('.stock.unavailable');
                        
                        if (nameEl && priceEl) {
                            items.push({
                                title: nameEl.innerText.trim(),
                                link: nameEl.href,
                                priceRaw: priceEl.innerText.trim(),
                                image: imgEl ? imgEl.src : '',
                                stock: stockEl ? stockEl.innerText.trim() : 'Unknown'
                            });
                        }
                    } catch (e) {
                    }
                });
                return items;
            """)
            
            if not products or len(products) == 0:
                print(f"No items found on page {page}. Stopping.")
                break
                
            print(f"  Found {len(products)} items on page.")
            
            page_added = 0
            for p in products:
                slug = p['link'].split('/')[-1].replace('.html', '')
                pid = f"mk-ult-{slug[:30]}" # Ultrabook prefix
                
                # UPSERT
                existing_data = [x for x in existing_data if x['link'] != p['link']]
                
                specs = parse_specs(p['title'])
                
                item = {
                    "id": pid,
                    "title": p['title'],
                    "price": clean_price(p['priceRaw']),
                    "image": p['image'],
                    "link": p['link'],
                    "stock": p['stock'],
                    "category": "Laptop",
                    "specs": specs,
                    "source": "MyTek",
                    "sub_category": "Ultrabook"
                }
                
                existing_data.append(item)
                existing_ids.add(pid)
                new_items_count += 1
                page_added += 1
            
            print(f"  Processed {page_added} items (Upserted).")
            
            if page_added > 0:
                with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=2, ensure_ascii=False)
                    
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()
        
    print(f"Finished. Added/Updated {new_items_count} Ultrabooks.")
    print(f"Total Database Size: {len(existing_data)}")

if __name__ == "__main__":
    scrape()
