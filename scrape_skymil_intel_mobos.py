import requests
from bs4 import BeautifulSoup
import json
import re
import os

BASE_URL = "https://skymil-informatique.com/28-intel-tunisie"
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\skymil_intel_mobos.json"

def clean_price(price_str):
    if not price_str:
        return 0.0
    clean = price_str.upper().replace('TND', '').replace('DT', '').replace('\u00a0', '').strip()
    clean = clean.replace(',', '.') 
    clean = re.sub(r'[^\d.]', '', clean)
    try:
        return float(clean)
    except ValueError:
        return 0.0

def extract_motherboard_details(title, desc_text):
    spec_data = {
        "socket": "Unknown",
        "form_factor": "Unknown",
        "memory_type": "Unknown",
        "memory_max": "Unknown",
        "chipset": "Unknown"
    }
    
    t_upper = title.upper()
    d_upper = desc_text.upper()
    full_text = t_upper + " " + d_upper

    # 1. Socket
    socket_match = re.search(r'(LGA\s?\d{4})', full_text)
    if socket_match:
        spec_data["socket"] = socket_match.group(1).replace(" ", "")
    elif "1851" in full_text:
        spec_data["socket"] = "LGA1851"
    elif "1700" in full_text:
        spec_data["socket"] = "LGA1700"
    elif "1200" in full_text:
        spec_data["socket"] = "LGA1200"
    elif "1151" in full_text:
        spec_data["socket"] = "LGA1151"
    
    # 2. Memory Type
    if "DDR5" in full_text:
        spec_data["memory_type"] = "DDR5"
    elif "DDR4" in full_text:
        spec_data["memory_type"] = "DDR4"
    elif "DDR3" in full_text:
        spec_data["memory_type"] = "DDR3"

    # 3. Form Factor
    if "E-ATX" in full_text or "EXTENDED ATX" in full_text:
        spec_data["form_factor"] = "E-ATX"
    elif "MICRO-ATX" in full_text or "M-ATX" in full_text or "MATX" in full_text:
        spec_data["form_factor"] = "Micro-ATX"
    elif "MINI-ITX" in full_text or "ITX" in full_text:
        spec_data["form_factor"] = "Mini-ITX"
    elif re.search(r'\bATX\b', full_text):
        spec_data["form_factor"] = "ATX"

    # 4. Memory Max
    mem_match = re.search(r'(?:JUSQU.À|MAX|JUSQU\'A|JUSQUA)\s?(\d{2,3})\s?(?:GO|GB)', full_text)
    if not mem_match:
        # Check standard capacities mentioned independently
        mem_match = re.search(r'\b(?:128|64|192|256|32)\s?(?:GO|GB)\b', full_text)
    
    if mem_match:
        val = int(mem_match.group(1) if mem_match.lastindex else mem_match.group(0).replace(' ', '').replace('GO','').replace('GB',''))
        spec_data["memory_max"] = f"{val}GB"

    # 5. Chipset
    # Simple search for intel chipsets: Z890, B860, H810, Z790, H770, B760, Z690, H670, B660, H610, Z590, B560, H510...
    chipset_match = re.search(r'\b(Z890|B860|H810|Z790|H770|B760|Z690|H670|B660|H610|Z590|B560|H510|Z490|B460|H410)\b', full_text)
    if chipset_match:
        spec_data["chipset"] = f"Intel {chipset_match.group(1)}"

    return spec_data

def scrape_skymil():
    print("Launching Skymil Motherboard Scraper...", flush=True)
    all_products = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    page = 1
    max_pages = 5
    
    while page <= max_pages:
        url = f"{BASE_URL}?page={page}"
        print(f"Fetching Page {page}: {url}...", flush=True)
        
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 404:
                break
                
            soup = BeautifulSoup(r.content, 'html.parser')
            items = soup.select("div.product-miniature.js-product-miniature")
            if not items:
                items = soup.select("article.product-miniature")
                
            if not items:
                print(f"No items found on page {page}. Stopping.")
                break

            found_new = False
            for item in items:
                title_elem = item.select_one(".product-title a")
                if not title_elem: continue
                title = title_elem.get_text(strip=True)
                
                # Cleanup Skymil bloated titles
                title = re.sub(r'(?i)Tunisie\s?Skymil\s?Carte\s?m[èe]re\s?Intel\s?', '', title).strip()
                link = title_elem['href']

                # Stock Status
                # Sometimes skymil hides addToCart if out of stock, sometimes it says "En stock" in description or label
                stock_label = item.select_one(".product-flags .out_of_stock, .product-availability")
                stock_text = stock_label.get_text(strip=True).lower() if stock_label else ""
                
                add_to_cart = item.select_one(".add-to-cart")
                disabled = add_to_cart and "disabled" in add_to_cart.get("class", [])
                
                # En stock logic
                availability = "in-stock"
                if disabled or "rupture" in stock_text or "epuisé" in stock_text or "hors" in stock_text:
                    availability = "out-of-stock"
                    
                # User asked to download ONLY EN STOCK
                if availability != "in-stock":
                    continue
                    
                # Deduplicate by link
                if any(p['link'] == link for p in all_products):
                    continue

                price_elem = item.select_one(".price")
                price = clean_price(price_elem.get_text(strip=True)) if price_elem else 0.0

                img_elem = item.select_one(".thumbnail-container img")
                image = img_elem['src'] if img_elem else ""

                desc_elem = item.select_one(".product-description-short")
                desc_text = desc_elem.get_text(separator=' ', strip=True) if desc_elem else ""
                
                specs = extract_motherboard_details(title, desc_text)
                
                product = {
                    "id": f"sm-mobo-{len(all_products)+1}",
                    "title": title,
                    "price": price,
                    "image": image,
                    "brand": "Unknown", # will be resolved in normalizeBrand later
                    "category": "motherboards",
                    "source": "Skymil",
                    "availability": availability,
                    "link": link,
                    "specs": specs
                }
                
                all_products.append(product)
                print(f"[{availability.upper()}] {title} - {price} DT")
                found_new = True

            if not found_new:
                break
                
            page += 1
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    print(f"\n--- SCRAPED {len(all_products)} IN-STOCK MOTHERBOARDS ---")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_skymil()
