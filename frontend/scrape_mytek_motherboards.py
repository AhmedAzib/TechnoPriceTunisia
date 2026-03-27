import os
import time
import json
import re
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# Output Path
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'src', 'data', 'mytek_motherboards.json')

# Helper to Extract Specs from Title and Description
def parse_specs(title, description=""):
    specs = {
        "socket": "Unknown",
        "format": "Unknown", 
        "memory_type": "Unknown",
        "brand": "Unknown"
    }
    t = title.upper()
    d = description.upper()
    combined = t + " " + d
    
    # 1. Brand Extraction
    if "ASUS" in t: specs['brand'] = "ASUS"
    elif "MSI" in t: specs['brand'] = "MSI"
    elif "GIGABYTE" in t: specs['brand'] = "GIGABYTE"
    elif "ASROCK" in t: specs['brand'] = "ASROCK"
    elif "BIOSTAR" in t: specs['brand'] = "BIOSTAR"
    
    # 2. Socket Extraction (Explicit)
    if "LGA 1700" in combined or "LGA1700" in combined: specs['socket'] = "LGA 1700"
    elif "LGA 1200" in combined or "LGA1200" in combined: specs['socket'] = "LGA 1200"
    elif "LGA 1851" in combined or "LGA1851" in combined: specs['socket'] = "LGA 1851"
    elif "AM5" in combined: specs['socket'] = "AM5"
    elif "AM4" in combined: specs['socket'] = "AM4"
    
    # 2b. Socket Inference from Chipset (Heuristic)
    if specs['socket'] == "Unknown":
        if any(x in t for x in ["A520", "B450", "B550", "X570", "A320"]): specs['socket'] = "AM4"
        elif any(x in t for x in ["A620", "B650", "X670", "X870", "B850", "B840"]): specs['socket'] = "AM5"
        elif any(x in t for x in ["H610", "B660", "H770", "B760", "Z690", "Z790"]): specs['socket'] = "LGA 1700"
        elif any(x in t for x in ["H510", "B560", "Z590", "H410", "B460", "Z490"]): specs['socket'] = "LGA 1200"
        elif any(x in t for x in ["Z890", "B860"]): specs['socket'] = "LGA 1851"
    
    # 3. Format Extraction (Explicit)
    if "MICRO ATX" in combined or "MICRO-ATX" in combined or "M-ATX" in combined: specs['format'] = "Micro-ATX"
    elif "MINI ITX" in combined or "MINI-ITX" in combined: specs['format'] = "Mini-ITX"
    elif "E-ATX" in combined or "EATX" in combined: specs['format'] = "E-ATX"
    elif "ATX" in combined: specs['format'] = "ATX"
    
    # 3b. Format Inference (Heuristic)
    if specs['format'] == "Unknown":
        # Check for 'M' suffix in chipset usually indicating mATX (e.g. B550M, H610M)
        # Be careful not to match random Ms. Match Chipset+M word boundary or before hyphen.
        chipset_m_regex = r'(?:A520|B450|B550|A620|B650|H610|B660|B760|H510|B560)[M](?![A-Z])'
        if re.search(chipset_m_regex, t):
            specs['format'] = "Micro-ATX"
    
    # 4. Memory Type Extraction
    if "DDR5" in combined: specs['memory_type'] = "DDR5"
    elif "DDR4" in combined: specs['memory_type'] = "DDR4"
    elif "DDR3" in combined: specs['memory_type'] = "DDR3"
    
    # 4b. Memory Inference from Chipset
    if specs['memory_type'] == "Unknown":
        # AM5 is only DDR5
        if specs['socket'] == "AM5" or any(x in t for x in ["A620", "B650", "X670", "X870"]):
            specs['memory_type'] = "DDR5"
        # LGA 1851 is DDR5
        elif specs['socket'] == "LGA 1851" or any(x in t for x in ["Z890", "B860"]):
            specs['memory_type'] = "DDR5"

    return specs

def clean_price(price_str):
    try:
        clean = re.sub(r'[^\d,.]', '', price_str)
        clean = clean.replace(',', '.')
        return float(clean)
    except:
        return 0.0

def scrape():
    print("VERSION: Motherboard 1.0 - Appending Mode")
    print("Launching MyTek Motherboard Scraper...")
    
    # Load Existing Data
    existing_data = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                print(f"Loaded {len(existing_data)} existing items.")
        except:
            print("Could not load existing file. Starting fresh.")
    
    existing_links = {item['link'] for item in existing_data}

    # Setup Driver
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--blink-settings=imagesEnabled=false')
    
    driver = uc.Chrome(options=options)
    
    base_url = "https://www.mytek.tn/informatique/composants-informatique/carte-mere.html"
    
    new_items_count = 0
    
    try:
        for page in range(1, 100):
            url = f"{base_url}?p={page}"
            print(f"Scraping Page {page}: {url}")
            driver.get(url)
            
            time.sleep(random.uniform(3, 6))
            
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
                        const stockEl = el.querySelector('.stock.availables span') || el.querySelector('.stock.unavailable span') || el.querySelector('.stock span');
                        
                        // Extract description snippet if available for better parsing
                        const descEl = el.querySelector('.product-item-description'); 
                        const desc = descEl ? descEl.innerText : "";

                        if (nameEl && priceEl) {
                            items.push({
                                title: nameEl.innerText.trim(),
                                link: nameEl.href,
                                priceRaw: priceEl.innerText.trim(),
                                image: imgEl ? imgEl.src : '',
                                stock: stockEl ? stockEl.innerText.trim() : 'Unknown',
                                description: desc
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
                # FILTER: En stock ONLY
                if "En stock" not in p['stock']:
                    continue

                if p['link'] in existing_links:
                    continue
                
                slug = p['link'].split('/')[-1].replace('.html', '')
                pid = f"mytek-mb-{slug[:40]}" 
                
                specs = parse_specs(p['title'], p['description'])
                
                item = {
                    "id": pid,
                    "title": p['title'],
                    "price": clean_price(p['priceRaw']),
                    "image": p['image'],
                    "link": p['link'],
                    "stock": p['stock'],
                    "category": "Motherboard",
                    "specs": specs,
                    "source": "MyTek",
                    "sub_category": "Main"
                }
                
                existing_data.append(item)
                existing_links.add(p['link'])
                new_items_count += 1
                page_added += 1
            
            print(f"  Added {page_added} new in-stock items.")
            
            if page_added > 0:
                with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            # Stop if page had no valid items (likely end of list or only out of stock left?)
            # Actually, Mytek sort by pertinence might mix stock. We should continue paging until no items found at all.
                    
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()
        
    print(f"Finished. Added {new_items_count} new motherboards.")
    print(f"Total Database Size: {len(existing_data)}")

if __name__ == "__main__":
    scrape()
