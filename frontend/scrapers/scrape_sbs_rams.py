import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time

BASE_URL = "https://www.sbsinformatique.com/barrettes-pc-de-bureau-tunisie"
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\sbs_rams.json"

def parse_price(price_str):
    try:
        clean_str = price_str.replace(' TND', '').replace(' ', '').replace(',', '.')
        clean_str = re.sub(r'[^\d.]', '', clean_str)
        return float(clean_str)
    except:
        return 0.0

def scrape_sbs_rams():
    all_rams = []
    seen_links = set()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    # Based on the pagination analysis, there are 25 articles (approx 3 pages of 12 items)
    for page in range(1, 4):
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
                print(f"No products found on page {page}.")
                break
                
            items_found_on_page = 0
                
            for product in products:
                # The Add-to-cart form
                # If the 'disable' class is present on the button, or it has the disabled attribute
                # cart_btn = product.select_one('button.tvproduct-add-to-cart')
                # if cart_btn and ('disable' in cart_btn.get('class', []) or 'disabled' in cart_btn.get('class', []) or cart_btn.has_attr('disabled')):
                #    continue # Skip out of stock items
                    
                title_elem = product.select_one('.tvproduct-name h6') or product.select_one('.product-title h6')
                if not title_elem:
                    continue
                    
                title = title_elem.text.strip()
                linkWrapper = product.select_one('.tvproduct-name a') or product.select_one('a.product-thumbnail')
                link = linkWrapper['href'] if linkWrapper else ''
                
                if link in seen_links:
                    continue
                seen_links.add(link)
                
                price_elem = product.select_one('.price')
                price = parse_price(price_elem.text.strip()) if price_elem else 0.0
                
                img_elem = product.select_one('img.tvproduct-defult-img')
                image = img_elem['src'] if img_elem else ''
                
                desc_elem = product.select_one('.tv-product-desc')
                desc = desc_elem.text.strip() if desc_elem else ''
                # Parse specs using the same extract_specs logic from SpaceNet
                specs = {
                    "capacity": "Unknown",
                    "type": "Unknown",
                    "frequency": "Unknown"
                }
                
                # Combine title and desc to find specs
                full_text = f"{title} {desc}"
                
                type_match = re.search(r'(DDR\d)', full_text, re.IGNORECASE)
                if type_match:
                    specs["type"] = type_match.group(1).upper()
                    
                cap_match = re.search(r'(\d+)\s*(Go|GB)', full_text, re.IGNORECASE)
                if cap_match:
                    specs["capacity"] = f"{cap_match.group(1)}GB"
                    
                freq_match = re.search(r'(\d+)\s*(?:MHz|MT/s)', full_text, re.IGNORECASE)
                if freq_match:
                     specs["frequency"] = f"{freq_match.group(1)}MHz"
                     
                
                ram = {
                    "id": f"sbs-ram-{len(all_rams)}",
                    "title": title,
                    "price": price,
                    "image": image,
                    "brand": "Unknown", # Default, normalized in frontend
                    "category": "ram", 
                    "source": "SBS Informatique",
                    "availability": "in-stock",
                    "link": link,
                    "specs": specs,
                    "raw_description": desc
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
    scrape_sbs_rams()
