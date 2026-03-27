import requests
from bs4 import BeautifulSoup
import json
import time
import os

BASE_URL = "https://www.tunisianet.com.tn/409-barrette-memoire"
OUTPUT_FILE = os.path.join("frontend", "src", "data", "tunisianet_rams.json")

def parse_price(price_str):
    try:
        clean_str = price_str.replace(' DT', '').replace(' ', '').replace(',', '.')
        return float(clean_str)
    except:
        return 0.0

def scrape_tunisianet_rams():
    all_rams = []
    seen_links = set()
    page = 1
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    while page <= 20: # HARD LIMIT to prevent infinite loop
        url = f"{BASE_URL}?page={page}"
        print(f"Scraping page {page}...")
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"Failed to fetch page {page}.")
                break
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            products = soup.select('.item-product')
            if not products:
                print(f"No products found on page {page}. Ending pagination.")
                break
                
            items_found_on_page = 0
            new_items_this_page = 0
                
            for product in products:
                title_elem = product.select_one('.product-title a')
                if not title_elem:
                    continue
                    
                link = title_elem['href']
                if link in seen_links:
                    continue
                seen_links.add(link)
                new_items_this_page += 1
                
                stock_elem = product.select_one('.in-stock')
                if not stock_elem:
                    continue # Out of stock
                    
                title = title_elem.text.strip()
                
                price_elem = product.select_one('.price')
                price = parse_price(price_elem.text.strip()) if price_elem else 0.0
                
                img_elem = product.select_one('.thumbnail.product-thumbnail img')
                image = img_elem['src'] if img_elem else ''
                
                desc_elem = product.select_one('.list-ds')
                desc = desc_elem.text.strip() if desc_elem else ''
                
                brand = "Unknown"
                brand_elem = product.select_one('.manufacturer-logo img') # Updated selector for brand
                if brand_elem and brand_elem.has_attr('alt'):
                     brand = brand_elem['alt'].strip().capitalize()
                
                ram = {
                    "id": f"tunisianet-ram-{len(all_rams)}",
                    "title": title + " " + desc,
                    "price": price,
                    "image": image,
                    "brand": brand,
                    "category": "ram", 
                    "source": "Tunisianet",
                    "availability": "in-stock",
                    "link": link,
                    "specs": {
                        "category": "ram",
                        "description": desc
                    }
                }
                
                all_rams.append(ram)
                items_found_on_page += 1
                
            print(f"  -> Found {items_found_on_page} in-stock RAMs on page {page}.")
            
            if new_items_this_page == 0:
                print("No new unique items found on this page. Pagination ended.")
                break
                
            page += 1
            time.sleep(1)
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    print(f"\\nTotal in-stock RAMs scraped: {len(all_rams)}")
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_rams, f, indent=2, ensure_ascii=False)
        
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_tunisianet_rams()
