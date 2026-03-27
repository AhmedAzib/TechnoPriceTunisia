import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time

BASE_URL = "https://spacenet.tn/25-barrette-memoire"
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\spacenet_rams.json"

def parse_price(price_str):
    try:
        clean_str = price_str.replace(' DT', '').replace(' ', '').replace(',', '.')
        # Some prices might have '' due to encoding issues with ' DT'
        clean_str = re.sub(r'[^\d.]', '', clean_str)
        return float(clean_str)
    except:
        return 0.0

def extract_specs(title):
    specs = {
        "capacity": "Unknown",
        "type": "Unknown",
        "frequency": "Unknown"
    }
    
    # Extract Type
    type_match = re.search(r'(DDR\d)', title, re.IGNORECASE)
    if type_match:
        specs["type"] = type_match.group(1).upper()
        
    # Extract Capacity
    cap_match = re.search(r'(\d+)\s*(Go|GB)', title, re.IGNORECASE)
    if cap_match:
        specs["capacity"] = f"{cap_match.group(1)}GB"
        
    # Extract Frequency
    freq_match = re.search(r'(\d+)\s*MHz', title, re.IGNORECASE)
    if freq_match:
         specs["frequency"] = f"{freq_match.group(1)}MHz"
         
    # Apply Hardcoded Manufacturer / SpaceNet Title overrides
    hardcoded_freqs = {
        "Barrette Mémoire 4Go DDR4 Pour PC De Bureau": "3200MHz",
        "Barrette Mémoire 8Go DDR4 3200Mz SO-DIMM": "3200MHz",
        "Barrette Mémoire 8Go DDR5 5600Mz SO-DIMM": "5600MHz",
        "Barrette Mémoire Samsung  8 Go DDR5 SODIMM": "4800MHz",
        "Barrette Mémoire Kingston 4Go DDR4 SO-DIMM": "2400MHz",
        "Barrette Mémoire Samsung 4 Go DDR4 3200 AA": "3200MHz",
        "Barrette Mémoire Samsung 8 Go DDR4 3200AA": "3200MHz"
    }
    
    for override_title, override_freq in hardcoded_freqs.items():
        if override_title.replace("  ", " ").strip() == title.replace("  ", " ").strip():
            specs["frequency"] = override_freq
            break
         
    return specs

def scrape_spacenet_rams():
    all_rams = []
    seen_links = set()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    # As requested by the user, we scrape exactly 6 pages
    for page in range(1, 7):
        url = f"{BASE_URL}?page={page}"
        print(f"Scraping page {page}...")
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"Failed to fetch page {page}. Status Code: {response.status_code}")
                break
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            products = soup.select('.item-product') or soup.select('.product-miniature')
            if not products:
                print(f"No products found on page {page}. Ending pagination early.")
                break
                
            items_found_on_page = 0
                
            for product in products:
                title_elem = product.select_one('h2.product_name a')
                if not title_elem:
                    continue
                    
                link = title_elem['href']
                if link in seen_links:
                    continue
                seen_links.add(link)
                
                # Check stock
                stock_elem = product.select_one('.product-quantities label')
                stock_text = stock_elem.text.strip().lower() if stock_elem else ''
                
                # SpaceNet might also have Add to Cart button to check stock
                cart_btn = product.select_one('form.btn-add-to-cart')
                
                # Default "out-of-stock" condition, checking 'en stock' or cart button
                if 'en stock' not in stock_text and not cart_btn:
                    continue  # Out of stock
                    
                title = title_elem.text.strip()
                
                price_elem = product.select_one('.product-price-and-shipping .price')
                price = parse_price(price_elem.text.strip()) if price_elem else 0.0
                
                img_elem = product.select_one('.thumbnail img')
                image = img_elem['src'] if img_elem else ''
                
                brand_elem = product.select_one('.manufacturer-logo')
                brand = "Unknown"
                if brand_elem and brand_elem.has_attr('alt'):
                    brand = brand_elem['alt'].strip()
                    if brand.lower() == 'sans marque' or brand == '':
                        brand = "Unknown"
                
                specs = extract_specs(title)
                
                ram = {
                    "id": f"spacenet-ram-{len(all_rams)}",
                    "title": title,
                    "price": price,
                    "image": image,
                    "brand": brand,
                    "category": "ram", 
                    "source": "SpaceNet",
                    "availability": "in-stock",
                    "link": link,
                    "specs": specs
                }
                
                all_rams.append(ram)
                items_found_on_page += 1
                
            print(f"  -> Found {items_found_on_page} in-stock RAMs on page {page}.")
            time.sleep(1)
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    print(f"\nTotal in-stock RAMs scraped: {len(all_rams)}")
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_rams, f, indent=2, ensure_ascii=False)
        
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_spacenet_rams()
