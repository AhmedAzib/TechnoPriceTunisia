import requests
from bs4 import BeautifulSoup
import re
import json
import os
import time

def parse_price(price_str):
    if not price_str: return 0
    # Clean all non-numeric characters except comma and dot
    clean_str = re.sub(r'[^\d.,]', '', price_str).replace(',', '.')
    try:
        return float(clean_str)
    except:
        return 0

def parse_specs_from_title_and_desc(title, desc):
    specs = {
        'memory_type': 'Unknown',
        'ram_capacity': 'Unknown',
        'frequency': 'Unknown',
        'format': 'Unknown'
    }
    
    combined = (title + " " + desc).upper()
    
    # Capacity
    cap_match = re.search(r'(\d{1,3})\s?(GO|GB)', combined)
    if cap_match:
        specs['ram_capacity'] = f"{cap_match.group(1)} GB"
        
    # Type
    if 'DDR5' in combined: specs['memory_type'] = 'DDR5'
    elif 'DDR4' in combined: specs['memory_type'] = 'DDR4'
    elif 'DDR3' in combined: specs['memory_type'] = 'DDR3'
    elif re.search(r'\bD5\b', combined): specs['memory_type'] = 'DDR5'
    elif re.search(r'\bD4\b', combined): specs['memory_type'] = 'DDR4'
        
    # Frequency
    freq_match = re.search(r'(\d{4})\s*(MHZ|MT/S)', combined)
    if freq_match:
        specs['frequency'] = f"{freq_match.group(1)} MHz"
        
    # Format
    if 'SO-DIMM' in combined or 'SODIMM' in combined or 'PORTABLE' in combined:
        specs['format'] = 'SO-DIMM'
    elif 'UDIMM' in combined or 'DIMM' in combined or 'PC' in combined or 'BUREAU' in combined:
        specs['format'] = 'DIMM'
        
    return specs

def scrape_skymil_rams():
    base_url = "https://skymil-informatique.com/30-memoire-ram-tunisie?page="
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    all_rams = []
    
    for page in range(1, 3):
        print(f"Scraping page {page}...")
        url = base_url + str(page)
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            products = soup.select('article.product-miniature')
            if not products:
                print(f"No products found on page {page}.")
                break
                
            for p in products:
                # Title & Link
                title_elem = p.select_one('.product-title a')
                title = title_elem.text.strip() if title_elem else "Unknown"
                link = title_elem['href'] if title_elem else ""
                
                # Image
                img_elem = p.select_one('.product-thumbnail img')
                image = img_elem['data-full-size-image-url'] if img_elem and 'data-full-size-image-url' in img_elem.attrs else ""
                if not image and img_elem:
                    image = img_elem['src']
                    
                # Price
                price_elem = p.select_one('.price')
                price = parse_price(price_elem.text if price_elem else "")
                
                # description (has specs)
                desc_elem = p.select_one('.product-description-short')
                desc = desc_elem.text.strip() if desc_elem else ""
                
                # Extract Specs
                specs = parse_specs_from_title_and_desc(title, desc)
                specs['category'] = 'ram'
                
                # Form ID from link
                product_id = "skymil-ram-" + link.split('/')[-1].replace('.html', '')
                
                # Stock (SkyMil generally shows all items on this page, but if add-to-cart exists, it's in stock)
                # Let's assume in-stock if add-to-cart exists, else out-of-stock
                in_stock_btn = p.select_one('.add-to-cart')
                status = "En Stock" if in_stock_btn else "Hors Stock"
                
                # Only save In Stock
                if status == "En Stock":
                    all_rams.append({
                        "id": product_id,
                        "title": title,
                        "price": price,
                        "link": link,
                        "image": image,
                        "status": status,
                        "brand": "Unknown", # Let master normalizer figure it out from title
                        "specs": specs
                    })
            
            time.sleep(1) # Be polite
            
        except requests.exceptions.RequestException as e:
            print(f"Error scraping page {page}: {e}")
            
    print(f"Scraped {len(all_rams)} total in-stock RAMs from SkyMil.")
    
    out_dir = r"c:\Users\USER\Documents\programmation\frontend\src\data"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "skymil_rams.json")
    
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(all_rams, f, ensure_ascii=False, indent=4)
        
    print(f"Saved to {out_file}")

if __name__ == "__main__":
    scrape_skymil_rams()
