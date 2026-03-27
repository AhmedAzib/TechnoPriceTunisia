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
    # Pattern: number followed by GO/TO, optionally followed by SSD/HDD
    # We find ALL matches and assign based on values/suffix
    
    # Regex to capture: (Value, Unit, Suffix)
    # suffix is optional.
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
                # Explicit storage
                specs['storage'] = formatted
            else:
                # Ambiguous - guess based on value
                if unit == 'TO':
                    specs['storage'] = formatted
                elif v_int in [4, 6, 8, 12, 16, 20, 24, 32, 40, 48, 64]:
                    # Likely RAM (unless it's a very old 32GB SSD)
                    if specs['ram'] == 'Unknown':
                        specs['ram'] = formatted
                elif v_int >= 120:
                    # Likely Storage
                    # Only overwrite if not already found via explicit suffix
                    if specs['storage'] == 'Unknown':
                         specs['storage'] = formatted
        except:
             pass

    # CPU Heuristics
    if "ULTRA" in t: specs['cpu'] = "Intel Core Ultra" # Broad catch
    elif "I9" in t: specs['cpu'] = "Intel Core i9"
    elif "I7" in t: specs['cpu'] = "Intel Core i7"
    elif "I5" in t: specs['cpu'] = "Intel Core i5"
    elif "I3" in t: specs['cpu'] = "Intel Core i3"
    elif "N100" in t: specs['cpu'] = "Intel N100"
    elif "N200" in t: specs['cpu'] = "Intel N200"
    elif "N4500" in t: specs['cpu'] = "Intel Celeron N4500"
    elif "N4020" in t: specs['cpu'] = "Intel Celeron N4020"
    elif "CELERON" in t: specs['cpu'] = "Intel Celeron"
    elif "RYZEN 9" in t: specs['cpu'] = "AMD Ryzen 9"
    elif "RYZEN 7" in t: specs['cpu'] = "AMD Ryzen 7"
    elif "RYZEN 5" in t: specs['cpu'] = "AMD Ryzen 5"
    elif "RYZEN 3" in t: specs['cpu'] = "AMD Ryzen 3"
    elif "ATHLON" in t: specs['cpu'] = "AMD Athlon"
    elif "M1" in t: specs['cpu'] = "Apple M1"
    elif "M2" in t: specs['cpu'] = "Apple M2"
    elif "M3" in t: specs['cpu'] = "Apple M3"
    
    # Screen
    screen_match = re.search(r'(\d{2}\.?\d?)\s*\"', t) # Matches 15.6"
    if screen_match:
        specs['screen'] = f"{screen_match.group(1)}\""
        
    return specs

def clean_price(price_str):
    if not price_str: return 0.0
    # Remove 'DT', spaces, non-breaking spaces
    clean = re.sub(r'[^\d,]', '', price_str)
    # Replace comma with dot
    clean = clean.replace(',', '.')
    try:
        return float(clean)
    except:
        return 0.0

def scrape():
    print("VERSION: 2.0 - New Spec Parsing")
    print("Launching MyTek Laptop Scraper...")
    
    # Setup Driver
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-popup-blocking')
    
    driver = uc.Chrome(options=options, use_subprocess=True)
    
    products = []
    seen_links = set()
    
    base_url = "https://www.mytek.tn/informatique/ordinateurs-portables/pc-portable.html"
    
    try:
        # Loop pages 1 to 50
        for page in range(1, 51):
            url = f"{base_url}?p={page}"
            print(f"Scraping Page {page}: {url}")
            
            driver.get(url)
            time.sleep(random.uniform(3, 6)) # Random wait to be safe
            
            # Simple Scroll to trigger lazy loading if any
            driver.execute_script("window.scrollBy(0, 500)")
            time.sleep(0.5)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            
            # Extract Data (Updated Selectors)
            items = driver.execute_script("""
                var params = [];
                // Correct selector based on debug HTML
                var boxes = document.querySelectorAll('div.product-container');
                
                boxes.forEach(box => {
                    try {
                        var nameEl = box.querySelector('.product-item-name a');
                        if (!nameEl) return;
                        
                        var imgEl = box.querySelector('.product-item-photo img');
                        var img = imgEl ? (imgEl.src || imgEl.getAttribute('data-src')) : "";
                        
                        // Price logic
                        var priceEl = box.querySelector('.price-box .final-price');
                        var price = priceEl ? priceEl.innerText : "0";
                        
                        // Stock Logic
                        var stockEl = box.querySelector('.stock.availables span');
                        var stock = stockEl ? stockEl.innerText.trim() : "Unknown";
                        // Check for out of stock indicator if stockEl is missing or generic
                        if (!stockEl && box.querySelector('.stock.unavailable')) {
                             stock = "Epuisé";
                        }

                        params.push({
                            title: nameEl.innerText.trim(),
                            link: nameEl.href,
                            image: img,
                            price: price,
                            stock: stock
                        });
                    } catch(e) {}
                });
                return params;
            """)
            
            if not items:
                print(f"No items found on page {page}. Stopping.")
                # Save debug HTML only if it's the first page failure
                if page == 1:
                    with open("debug_laptops_page1_v2.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    print("Saved debug_laptops_page1_v2.html")
                break

            new_count = 0
            for item in items:
                if item['link'] in seen_links: 
                    continue
                    
                seen_links.add(item['link'])
                new_count += 1
                
                specs = parse_specs(item['title'])
                price_val = clean_price(item['price'])
                
                products.append({
                    "id": f"mk-lap-{len(products)+1000}", # Unique ID
                    "title": item['title'],
                    "price": price_val,
                    "image": item['image'],
                    "link": item['link'],
                    "stock": item['stock'],
                    "category": "Laptop",
                    "specs": specs,
                    "source": "MyTek"
                })
                
            print(f"  Found {len(items)} items. {new_count} new. Total: {len(products)}")
            
            # Save incrementally
            if len(products) % 20 == 0:
                with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()
        
    # Final Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"Finished. Saved {len(products)} laptops to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape()
