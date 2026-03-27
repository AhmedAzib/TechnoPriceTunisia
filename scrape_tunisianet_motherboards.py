import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os
import random

# Configuration
BASE_URL = "https://www.tunisianet.com.tn/420-carte-mere?order=product.price.asc"
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\tunisianet_motherboards.json"

def clean_price(price_str):
    if not price_str:
        return 0.0
    # Handle "259,000 DT"
    clean = price_str.upper().replace('DT', '').replace('TND', '').replace('\u00a0', '').strip()
    clean = clean.replace(',', '.') 
    clean = re.sub(r'[^\d.]', '', clean)
    try:
        return float(clean)
    except ValueError:
        return 0.0

def extract_motherboard_details(title, full_text=""):
    spec_data = {
        "category": "motherboard",
        "brand": "Unknown",
        "socket": "Unknown",
        "chipset": "Unknown",
        "form_factor": "Unknown",
        "memory_type": "Unknown",
        "max_memory": "Unknown",
        "slots_ram": "Unknown",
        "slots_m2": "Unknown",
        "usb_c": "No",
        "wifi": "No",
        "bluetooth": "No",
        "pcie_gen": "Unknown"
    }
    
    t_upper = title.upper()
    text_upper = full_text.upper()
    
    # 1. Detect Brand
    if "MSI" in t_upper: spec_data["brand"] = "MSI"
    elif "ASUS" in t_upper: spec_data["brand"] = "Asus"
    elif "GIGABYTE" in t_upper: spec_data["brand"] = "Gigabyte"
    elif "ASROCK" in t_upper: spec_data["brand"] = "ASRock"
    elif "BIOSTAR" in t_upper: spec_data["brand"] = "Biostar"
    elif "NZXT" in t_upper: spec_data["brand"] = "NZXT"
    
    # 2. Socket Extraction (Critical)
    if "LGA 1851" in text_upper or "LGA1851" in text_upper: spec_data["socket"] = "LGA 1851" # New Intel
    elif "LGA 1700" in text_upper or "LGA1700" in text_upper or "1700" in t_upper: spec_data["socket"] = "LGA 1700"
    elif "LGA 1200" in text_upper or "LGA1200" in text_upper or "1200" in t_upper: spec_data["socket"] = "LGA 1200"
    elif "LGA 1151" in text_upper or "LGA1151" in text_upper: spec_data["socket"] = "LGA 1151"
    elif "AM5" in text_upper or "AM5" in t_upper: spec_data["socket"] = "AM5"
    elif "AM4" in text_upper or "AM4" in t_upper: spec_data["socket"] = "AM4"
    elif "TRX40" in text_upper: spec_data["socket"] = "sTRX4"
    elif "J4025" in t_upper or "J5040" in t_upper: spec_data["socket"] = "Integrated CPU"
    
    # 3. Chipset Extraction
    # Intel
    if "Z890" in t_upper or "Z890" in text_upper: spec_data["chipset"] = "Intel Z890"
    elif "B860" in t_upper or "B860" in text_upper: spec_data["chipset"] = "Intel B860"
    elif "H810" in t_upper or "H810" in text_upper: spec_data["chipset"] = "Intel H810"
    elif "Z790" in t_upper or "Z790" in text_upper: spec_data["chipset"] = "Intel Z790"
    elif "B760" in t_upper or "B760" in text_upper: spec_data["chipset"] = "Intel B760"
    elif "H610" in t_upper or "H610" in text_upper: spec_data["chipset"] = "Intel H610"
    elif "Z690" in t_upper or "Z690" in text_upper: spec_data["chipset"] = "Intel Z690"
    elif "B660" in t_upper or "B660" in text_upper: spec_data["chipset"] = "Intel B660"
    elif "H510" in t_upper or "H510" in text_upper: spec_data["chipset"] = "Intel H510"
    elif "B560" in t_upper or "B560" in text_upper: spec_data["chipset"] = "Intel B560"
    elif "Z590" in t_upper or "Z590" in text_upper: spec_data["chipset"] = "Intel Z590"
    # AMD
    elif "X870" in t_upper or "X870" in text_upper: spec_data["chipset"] = "AMD X870"
    elif "B850" in t_upper or "B850" in text_upper: spec_data["chipset"] = "AMD B850"
    elif "B840" in t_upper or "B840" in text_upper: spec_data["chipset"] = "AMD B840"
    elif "X670" in t_upper or "X670" in text_upper: spec_data["chipset"] = "AMD X670" # Covers X670E
    elif "B650" in t_upper or "B650" in text_upper: spec_data["chipset"] = "AMD B650" # Covers B650E
    elif "A620" in t_upper or "A620" in text_upper: spec_data["chipset"] = "AMD A620"
    elif "X570" in t_upper or "X570" in text_upper: spec_data["chipset"] = "AMD X570"
    elif "B550" in t_upper or "B550" in text_upper: spec_data["chipset"] = "AMD B550"
    elif "A520" in t_upper or "A520" in text_upper: spec_data["chipset"] = "AMD A520"
    elif "B450" in t_upper or "B450" in text_upper: spec_data["chipset"] = "AMD B450"
    elif "A320" in t_upper or "A320" in text_upper: spec_data["chipset"] = "AMD A320"

    # 4. Form Factor
    if "E-ATX" in text_upper or "EATX" in text_upper: spec_data["form_factor"] = "E-ATX"
    elif "MICRO-ATX" in text_upper or "MATX" in text_upper or "MICRO ATX" in text_upper or "M-ATX" in text_upper: spec_data["form_factor"] = "Micro-ATX"
    elif "MINI-ITX" in text_upper or "MITX" in text_upper or "MINI ITX" in text_upper: spec_data["form_factor"] = "Mini-ITX"
    elif "ATX" in text_upper: spec_data["form_factor"] = "ATX" # Check ATX last
    
    # Form Factor Fallback using Dimensions
    if spec_data["form_factor"] == "Unknown":
        if "244 X 244" in text_upper or "24.4 X 24.4" in text_upper or "244X244" in text_upper:
            spec_data["form_factor"] = "Micro-ATX"
        elif "305 X 244" in text_upper or "30.5 X 24.4" in text_upper or "305X244" in text_upper:
            spec_data["form_factor"] = "ATX"
        elif "170 X 170" in text_upper or "17 X 17" in text_upper:
            spec_data["form_factor"] = "Mini-ITX"

    # 5. Memory Type
    if "DDR5" in t_upper or "DDR5" in text_upper: spec_data["memory_type"] = "DDR5"
    elif "DDR4" in t_upper or "DDR4" in text_upper: spec_data["memory_type"] = "DDR4"
    elif "DDR3" in t_upper or "DDR3" in text_upper: spec_data["memory_type"] = "DDR3"

    # 6. Wifi & Bluetooth
    if "WIFI" in t_upper or "WI-FI" in text_upper: spec_data["wifi"] = "Yes"
    if "BLUETOOTH" in text_upper: spec_data["bluetooth"] = "Yes"

    return spec_data

def scrape_tunisianet_motherboards():
    print("Launching Full Scraper for Tunisianet Motherboards...", flush=True)
    all_products = []
    
    try:
        page = 1
        max_pages = 20 # Safety limit
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        while page <= max_pages:
            url = f"{BASE_URL}&page={page}"
            print(f"Fetching Page {page}: {url}", flush=True)
            
            try:
                r = requests.get(url, headers=headers, timeout=15)
                if r.status_code != 200:
                    print(f"Error: Status {r.status_code}")
                    break
            except Exception as e:
                print(f"Request Error: {e}")
                break
                
            soup = BeautifulSoup(r.content, 'html.parser')
            items = soup.select("article.product-miniature")
            
            if not items:
                print(f"No items found on page {page}. Stopping.", flush=True)
                break
                
            found_on_page = 0
            for item in items:
                # 1. Check Stock (Strict "En stock")
                in_stock = False
                stock_elem = item.select_one(".in-stock")
                if stock_elem and "EN STOCK" in stock_elem.get_text(strip=True).upper():
                    in_stock = True
                
                # Double check textual content if class method fails
                if not in_stock:
                     full_text_check = item.get_text().upper()
                     if "EN STOCK" in full_text_check and "NON DISPONIBLE" not in full_text_check and "ÉPUISÉ" not in full_text_check:
                         in_stock = True
                
                if not in_stock:
                    continue 

                # 2. Extract Data
                try:
                    p_id = item['data-id-product']
                except:
                    p_id = f"tunisianet-mb-{random.randint(1000,9999)}"
                
                # Title
                title_elem = item.select_one(".product-title a")
                if not title_elem: continue
                title = title_elem.get_text(strip=True)
                link = title_elem['href']
                
                # Image
                img_elem = item.select_one(".thumbnail-container img")
                image = img_elem['src'] if img_elem else ""
                
                # Price
                price_elem = item.select_one(".price")
                price = clean_price(price_elem.get_text(strip=True)) if price_elem else 0.0
                
                # Description (for specs)
                desc_elem = item.select_one(".product-description-short") or item.select_one(".listds")
                desc_text = desc_elem.get_text(separator=" ", strip=True) if desc_elem else ""
                
                specs = extract_motherboard_details(title, desc_text)
                
                product = {
                    "id": f"tunisianet-mb-{p_id}",
                    "title": title,
                    "price": price,
                    "image": image,
                    "brand": specs["brand"],
                    "category": "motherboard",
                    "source": "Tunisianet",
                    "availability": "in-stock",
                    "link": link,
                    "description": desc_text,
                    "specs": specs
                }
                
                all_products.append(product)
                found_on_page += 1
                
            print(f"Scraped {found_on_page} items from page {page}")
            if found_on_page == 0 and page > 1:
                print("No stock items found on this page. Stopping.")
                
            # Check for next page
            next_btn = soup.select_one("a.next.js-search-link")
            if not next_btn or "disabled" in next_btn.get("class", []):
                print("No next page button found. Stopping.")
                break
                
            page += 1
            time.sleep(1) 
            
    except Exception as e:
        print(f"Error during scraping: {e}")
        
    print(f"Total extracted: {len(all_products)}")
    
    # Save
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_tunisianet_motherboards()
