
import os
import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Setup JSON path
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'src', 'data', 'mytek_mobiles.json')
# URLs to scrape
START_URLS = [
    {"url": "https://www.mytek.tn/telephonie-tunisie/smartphone-mobile-tunisie/smartphone.html", "cat": "Smartphone"},
    {"url": "https://www.mytek.tn/telephonie-tunisie/smartphone-mobile-tunisie/iphone.html", "cat": "Smartphone"},
    {"url": "https://www.mytek.tn/smartphone.html", "cat": "Smartphone"},
    {"url": "https://www.mytek.tn/telephonie-tunisie/smartphone-mobile-tunisie/telephone-portable.html", "cat": "Feature Phone"},
    {"url": "https://www.mytek.tn/informatique/tablettes-tactiles/tablettes-android.html", "cat": "Tablet"},
    {"url": "https://www.mytek.tn/informatique/tablettes-tactiles/ipad.html", "cat": "Tablet"},
    {"url": "https://www.mytek.tn/telephonie-tunisie/smartwatch/montre-connectee.html", "cat": "Smartwatch"},
    {"url": "https://www.mytek.tn/telephonie-tunisie/smartwatch/bracelet-connectee.html", "cat": "Smartwatch"}
]

def extract_specs(text):
    # derived from get_specs in scraper.py
    clean_text = text.upper().replace("-", " ").replace("\\n", " ").replace("  ", " ")
    specs = { "brand": "Other", "ram": "Unknown", "storage": "Unknown", "screen": "Unknown", "color": "Unknown" }

    # --- BRAND ---
    brands = ["SAMSUNG", "APPLE", "INFINIX", "XIAOMI", "OPPO", "REALME", "VIVO", "HUAWEI", "NOKIA", "ITEL", "TECHO", "EVERTEK", "IPRO", "HUAWEI", "HONOR", "TCL", "BLACKVIEW"]
    for b in brands:
        if b in clean_text: specs["brand"] = b.capitalize(); break
    
    # --- RAM ---
    ram = re.search(r'(\d+)\s*(?:GO|GB)', clean_text)
    if ram: specs["ram"] = f"{ram.group(1)}GB"

    # --- STORAGE ---
    storage = re.search(r'(\d+)\s*(?:GO|GB|TO|TB)', clean_text)
    if storage:
        val = int(storage.group(1))
        unit = "GB"
        if "TO" in clean_text or "TB" in clean_text:
             unit = "TB"
             val = val 
        pass
    
    # Simple regex for typical storage sizes
    if "1 TO" in clean_text or "1TB" in clean_text: specs["storage"] = "1TB"
    elif "512" in clean_text: specs["storage"] = "512GB"
    elif "256" in clean_text: specs["storage"] = "256GB"
    elif "128" in clean_text: specs["storage"] = "128GB"
    elif "64" in clean_text: specs["storage"] = "64GB"
    elif "32" in clean_text: specs["storage"] = "32GB"
    elif "16" in clean_text: specs["storage"] = "16GB"
    
    # --- SCREEN ---
    screen = re.search(r'(\d+\.?\d*)\s*(?:\")', clean_text)
    if screen: specs["screen"] = f"{screen.group(1)}\""
    
    return specs


def scrape():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Load existing data first
    products = []
    seen_links = set()
    
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                products = json.load(f)
                for p in products:
                    seen_links.add(p['link'])
            print(f"Loaded {len(products)} existing products.")
        except Exception as e:
            print(f"Error loading existing data: {e}")
            
    current_max_id = 0
    if products:
        for p in products:
            try:
                # Expecting format 'mytek-mob-123'
                pid = int(p['id'].split('-')[-1])
                if pid > current_max_id:
                    current_max_id = pid
            except:
                pass
    
    driver = webdriver.Chrome(options=options)
    
    try:
        print("Starting MyTek Mobile Scraper (Robust Mode with Categories)...")
        
        for entry in START_URLS:
            base_url = entry['url']
            category_name = entry['cat']
            print(f"\n--- Scraping Category: {category_name} ({base_url}) ---")
            
            consecutive_empty_pages = 0
            
            # Iterate Pages 1 to 200
            for page in range(1, 201):
                url = f"{base_url}?p={page}"
                print(f"Scraping Page {page}: {url}")
                
                try:
                    driver.get(url)
                    time.sleep(4) # Wait for load
                    
                    # Scroll
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                    time.sleep(1)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    
                    # JS Extraction Strategy
                    items = driver.execute_script("""
                        var results = [];
                        var boxes = document.querySelectorAll('li.product-item, div.product-item, li.item.product');
                        
                        if (boxes.length === 0) {
                             boxes = document.querySelectorAll('div.product-container');
                        }

                        boxes.forEach(box => {
                            try {
                                var nameEl = box.querySelector('a.product-item-link') || box.querySelector('.product-item-name a');
                                var imgEl = box.querySelector('.product-item-photo img') || box.querySelector('.product-image-photo');
                                var img = imgEl ? (imgEl.src || imgEl.getAttribute('data-src')) : "";
                                
                                var priceEl = box.querySelector('[data-price-amount]');
                                var priceText = priceEl ? priceEl.getAttribute('data-price-amount') : "";
                                
                                if (!priceText) {
                                    var p = box.querySelector('.price');
                                    if (p) priceText = p.innerText;
                                }
                                
                                var stockEl = box.querySelector('.stock span') || box.querySelector('.stock');
                                var stock = stockEl ? stockEl.innerText.trim() : "Unknown";
                                if (box.querySelector('.unavailable')) stock += " Epuisé";

                                if (nameEl) {
                                     results.push({
                                        title: nameEl.innerText.trim(),
                                        link: nameEl.href,
                                        image: img,
                                        raw_price: priceText,
                                        availability: stock
                                    });
                                }
                            } catch(e) {}
                        });
                        return results;
                    """)
                    
                    if not items:
                        print("No items found on this page.")
                        consecutive_empty_pages += 1
                        if consecutive_empty_pages >= 2:
                            print("End of category reached.")
                            break
                        continue
                    else:
                        consecutive_empty_pages = 0
                        
                    new_items_count = 0
                    for item in items:
                        if item['link'] in seen_links:
                            continue
                        seen_links.add(item['link'])
                        new_items_count += 1
                        current_max_id += 1
                        
                        # Clean Price
                        price = 0
                        try:
                            # Handle "1 299,000 TND" or raw numbers
                            p_clean = str(item['raw_price']).replace('TND', '').replace(' ', '').replace(',', '.').strip()
                            # regex to find number
                            match = re.search(r'(\d+(\.\d+)?)', p_clean)
                            if match:
                                price = float(match.group(1))
                        except:
                            pass
                        
                        # Clean Availability
                        avail = "in-stock"
                        if "epuisé" in item['availability'].lower() or "out" in item['availability'].lower():
                            avail = "out-of-stock"
                        
                        # Brand (Simple guess)
                        brand = "Unknown"
                        
                        # Specs
                        specs = extract_specs(item['title'])
                        if specs.get("brand") and specs["brand"] != "Other":
                            brand = specs["brand"]
                        else:
                             brand = item['title'].split()[0]

                        products.append({
                            "id": f"mytek-mob-{current_max_id}",
                            "title": item['title'],
                            "price": price,
                            "image": item['image'],
                            "brand": brand,
                            "category": category_name, # Added Category
                            "source": "MyTek",
                            "availability": avail,
                            "link": item['link'],
                            "specs": specs
                        })
                        
                    print(f"  Found {len(items)} items. {new_items_count} new. Total: {len(products)}")
                    
                    # Save periodically
                    if len(products) % 50 == 0:
                         with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                            json.dump(products, f, ensure_ascii=False, indent=4)
                            
                    if len(products) >= 5000:
                        print("Target reached (5000).")
                        break
                        
                except Exception as e:
                    print(f"Page Error: {e}")
                    # Continue to next page anyway instead of breaking whole category
                    continue
            
            if len(products) >= 5000:
                break
                
    except Exception as e:
        print(f"Critical Scraper Error: {e}")
    finally:
        driver.quit()
        
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
        print(f"Final Save: {len(products)} to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape()
