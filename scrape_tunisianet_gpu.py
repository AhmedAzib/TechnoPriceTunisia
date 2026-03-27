import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os
import random

# Configuration
BASE_URL = "https://www.tunisianet.com.tn/410-carte-graphique-tunisie?order=product.price.asc"
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\tunisianet_gpu.json"

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

def extract_gpu_details(title, full_text=""):
    spec_data = {
        "category": "gpu",
        "gpu": "Unknown",
        "brand": "Unknown",
        "vram": "Unknown",
        "memory_type": "Unknown",
        "bus_memoire": "Unknown",
        "gpu_series": "Unknown",
        "target_res": "Unknown",
        "cuda_cores": "Unknown",
        "boost_clock": "Unknown",
        "psu": "Unknown",
        "extreme_performance": "Unknown"
    }
    
    t_upper = title.upper()
    text_upper = full_text.upper()
    
    # 1. Detect Brand
    if "MSI" in t_upper: spec_data["brand"] = "MSI"
    elif "ASUS" in t_upper: spec_data["brand"] = "Asus"
    elif "GIGABYTE" in t_upper: spec_data["brand"] = "Gigabyte"
    elif "PNY" in t_upper: spec_data["brand"] = "PNY"
    elif "ZOTAC" in t_upper: spec_data["brand"] = "Zotac"
    elif "PALIT" in t_upper: spec_data["brand"] = "Palit"
    elif "SAPPHIRE" in t_upper: spec_data["brand"] = "Sapphire"
    elif "XFX" in t_upper: spec_data["brand"] = "XFX"
    elif "GAINWARD" in t_upper: spec_data["brand"] = "Gainward"
    elif "INNO3D" in t_upper: spec_data["brand"] = "Inno3D"
    elif "MANLI" in t_upper: spec_data["brand"] = "Manli"
    elif "XSTORM" in t_upper: spec_data["brand"] = "XStorm"
    elif "BI-STAR" in t_upper: spec_data["brand"] = "Bi-Star"

    # 2. Extract GPU Chipset (1000% Safe)
    gpu_val = "Unknown"
    # NVIDIA 50 Series
    if "RTX 5090" in t_upper: gpu_val = "RTX 5090"
    elif "RTX 5080" in t_upper: gpu_val = "RTX 5080"
    elif "RTX 5070" in t_upper: 
        if "TI" in t_upper: gpu_val = "RTX 5070 Ti"
        else: gpu_val = "RTX 5070"
    elif "RTX 5060" in t_upper: 
        if "TI" in t_upper: gpu_val = "RTX 5060 Ti"
        else: gpu_val = "RTX 5060"
    elif "RTX 5050" in t_upper: gpu_val = "RTX 5050"
    
    # NVIDIA 40 Series
    elif "RTX 4090" in t_upper: gpu_val = "RTX 4090"
    elif "RTX 4080" in t_upper: gpu_val = "RTX 4080"
    elif "RTX 4070" in t_upper: 
        if "TI SUPER" in t_upper: gpu_val = "RTX 4070 Ti Super"
        elif "TI" in t_upper: gpu_val = "RTX 4070 Ti"
        elif "SUPER" in t_upper: gpu_val = "RTX 4070 Super"
        else: gpu_val = "RTX 4070"
    elif "RTX 4060" in t_upper:
        if "TI" in t_upper: gpu_val = "RTX 4060 Ti"
        else: gpu_val = "RTX 4060"
    elif "RTX 4050" in t_upper: gpu_val = "RTX 4050"

    # NVIDIA 30 Series
    elif "RTX 3090" in t_upper: gpu_val = "RTX 3090"
    elif "RTX 3080" in t_upper: gpu_val = "RTX 3080"
    elif "RTX 3070" in t_upper: gpu_val = "RTX 3070"
    elif "RTX 3060" in t_upper:
        if "TI" in t_upper: gpu_val = "RTX 3060 Ti"
        else: gpu_val = "RTX 3060"
    elif "RTX 3050" in t_upper: gpu_val = "RTX 3050"
    
    # NVIDIA 20/16/10 Series
    elif "RTX 2060" in t_upper: gpu_val = "RTX 2060"
    elif "GTX 1660" in t_upper: gpu_val = "GTX 1660"
    elif "GTX 1650" in t_upper: gpu_val = "GTX 1650"
    elif "GTX 1630" in t_upper: gpu_val = "GTX 1630"
    elif "GTX 1050" in t_upper: gpu_val = "GTX 1050" # Ti check?
    elif "GT 1030" in t_upper: gpu_val = "GT 1030"
    elif "GT 730" in t_upper: gpu_val = "GT 730"
    elif "GT 710" in t_upper or "GT710" in t_upper: gpu_val = "GT 710"
    elif "GT 610" in t_upper or "GT610" in t_upper: gpu_val = "GT 610"
    elif "GT 210" in t_upper or "GT210" in t_upper: gpu_val = "GT 210"
    
    # AMD Radeon
    elif "RX 9" in t_upper: 
        match = re.search(r'(RX\s?9\d{3}\s?XT|RX\s?9\d{3})', t_upper)
        gpu_val = match.group(0).replace(' ', ' ') if match else "AMD Radeon RX 9000 Series"
    elif "RX 8" in t_upper:
        match = re.search(r'(RX\s?8\d{3}\s?XT|RX\s?8\d{3})', t_upper)
        gpu_val = match.group(0).replace(' ', ' ') if match else "AMD Radeon RX 8000 Series"
    elif "RX 7900" in t_upper: gpu_val = "RX 7900"
    elif "RX 7800" in t_upper: gpu_val = "RX 7800"
    elif "RX 7700" in t_upper: gpu_val = "RX 7700"
    elif "RX 7600" in t_upper: gpu_val = "RX 7600"
    elif "RX 6900" in t_upper: gpu_val = "RX 6900"
    elif "RX 6800" in t_upper: gpu_val = "RX 6800"
    elif "RX 6700" in t_upper: gpu_val = "RX 6700"
    elif "RX 6600" in t_upper: gpu_val = "RX 6600"
    elif "RX 6500" in t_upper: gpu_val = "RX 6500"
    elif "RX 6400" in t_upper: gpu_val = "RX 6400"
    elif "RX 580" in t_upper: gpu_val = "RX 580"
    elif "RX 570" in t_upper: gpu_val = "RX 570"
    elif "RX 550" in t_upper: gpu_val = "RX 550"
    
    # Intel Arc
    elif "A770" in t_upper: gpu_val = "Intel Arc A770"
    elif "A750" in t_upper: gpu_val = "Intel Arc A750"
    elif "A380" in t_upper: gpu_val = "Intel Arc A380"
    
    spec_data["gpu"] = gpu_val

    # 3. Extract VRAM (Critical)
    vram = "Unknown"
    # Negative lookbehind to ensure we don't catch "5060 GB" or "5080 GB" from titles like "RTX 5060"
    # We look for 1-2 digits, maybe a space, then GB.
    # Updated regex to be safer: match 1-2 digits (or 24), but not 4 digits.
    mem_match = re.search(r'\b(\d{1,2})\s?(G|GO|GB)\b', t_upper)
    if mem_match:
         vram = f"{mem_match.group(1)} GB"
    
    # Fallback for RTX 5050/5060 override
    if vram == "Unknown":
        if "RTX 5050" in t_upper or "RTX 5060" in t_upper:
            vram = "8 GB" # 1000% safe fallback per user request
            
    spec_data["vram"] = vram

    # 4. Memory Type
    if "GDDR6X" in t_upper or "GDDR6X" in text_upper: spec_data["memory_type"] = "GDDR6X"
    elif "GDDR6" in t_upper or "GDDR6" in text_upper: spec_data["memory_type"] = "GDDR6"
    elif "GDDR5" in t_upper or "GDDR5" in text_upper: spec_data["memory_type"] = "GDDR5"
    elif "DDR5" in t_upper: spec_data["memory_type"] = "DDR5"
    elif "DDR4" in t_upper: spec_data["memory_type"] = "DDR4"
    elif "DDR3" in t_upper: spec_data["memory_type"] = "DDR3"

    # 6. PSU Extraction (Recommended Power)
    psu = "Unknown"
    # Patterns: "Alimentation 650W", "PSU 650W", "650 Watt" + context
    # Look for 3-4 digits followed by W/Watt
    psu_match = re.search(r'(ALIMENTATION|PSU|PUISSANCE).{0,30}?(\d{3,4})\s?(W|WATT)', text_upper)
    if psu_match:
         psu = f"{psu_match.group(2)} W"
    else:
         # Fallback: Just look for "650W" or "650 W" surrounded by boundaries, hoping it's PSU
         # Less safe, but common in spec lists.
         # Only accept typical PSU values to avoid "2500W" PMPO or something.
         watt_match = re.search(r'\b(300|350|400|450|500|550|600|650|700|750|800|850|1000|1200|1600)\s?(W|WATT)\b', text_upper)
         if watt_match:
             psu = f"{watt_match.group(1)} W"

    spec_data["psu"] = psu

    # 7. Boost Clock Extraction (MHz)
    boost_clock = "Unknown"
    # Patterns: "Boost Clock 2640 MHz", "Vitesse 2640 MHz", "Frequence 2640 MHz", "2640 MHz"
    boost_match = re.search(r'(BOOST|VITESSE|FREQUENCE|CLOCK|HORLOGE).{0,30}?(\d{3,4})\s?(MHZ)', text_upper)
    if boost_match:
         boost_clock = f"{boost_match.group(2)} MHz"
    else:
         # Fallback: Just look for "XXXX MHz"
         mhz_match = re.search(r'\b(\d{3,4})\s?(MHZ)\b', text_upper)
         if mhz_match:
             # Sanity check: GPU clocks are usually 900-3000 MHz. Memory clocks might be higher (14000+). 
             val = int(mhz_match.group(1))
             if 500 <= val <= 3500: # Core clock range
                 boost_clock = f"{val} MHz"

    spec_data["boost_clock"] = boost_clock

    return spec_data

def scrape_tunisianet_gpu():
    print("Launching Full Scraper for Tunisianet GPUs...", flush=True)
    all_products = []
    
    try:
        page = 1
        max_pages = 10 # Safety limit
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
                # 1. Check Stock
                in_stock = False
                stock_elem = item.select_one(".in-stock")
                if stock_elem and "EN STOCK" in stock_elem.get_text(strip=True).upper():
                    in_stock = True
                
                # Double check
                if not in_stock:
                     full_text_check = item.get_text().upper()
                     if "EN STOCK" in full_text_check and "NON DISPONIBLE" not in full_text_check:
                         in_stock = True
                
                if not in_stock:
                    continue 

                # 2. Extract Data
                try:
                    p_id = item['data-id-product']
                except:
                    p_id = f"tunisianet-gpu-{random.randint(1000,9999)}"
                
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
                
                specs = extract_gpu_details(title, desc_text)
                
                product = {
                    "id": f"tunisianet-gpu-{p_id}",
                    "title": title,
                    "price": price,
                    "image": image,
                    "brand": specs["brand"],
                    "category": "gpu",
                    "source": "Tunisianet",
                    "availability": "in-stock",
                    "link": link,
                    "description": desc_text, # Added Description Field
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
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_tunisianet_gpu()
