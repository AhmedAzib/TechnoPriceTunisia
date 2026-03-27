import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os
import random

# Configuration
BASE_URL = "https://www.tunisianet.com.tn/421-processeur?order=product.price.asc"
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\tunisianet_processors.json"

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

def extract_cpu_details(title, full_text=""):
    spec_data = {
        "category": "cpu",
        "cpu": "Unknown",
        "brand": "Unknown"
    }
    
    t_upper = title.upper()
    text_upper = full_text.upper()
    
    # 1. Detect Brand
    if "INTEL" in t_upper or "CORE" in t_upper:
        spec_data["brand"] = "Intel"
    elif "AMD" in t_upper or "RYZEN" in t_upper or "ATHLON" in t_upper:
        spec_data["brand"] = "AMD"
    elif "ASROCK" in t_upper:
        spec_data["brand"] = "ASRock"
        
    # 2. Extract CPU Model
    # Specific edge case requested by user
    if "ASROCK J4025M" in t_upper:
        spec_data["cpu"] = "ASRock J4025M"
    elif spec_data["brand"] == "Intel":
        ultra_match = re.search(r'(CORE\s?ULTRA\s?\d\s?(?:PROCESSOR\s?)?\d{3}[A-Z]*)', t_upper)
        if ultra_match:
             raw = ultra_match.group(1).title()
             spec_data["cpu"] = f"Intel {raw.replace('Processor ', '')}"
        else:
            match = re.search(r'(CORE\s?I\d[-\s]?\d{3,5}[A-Z]?)', t_upper)
            if match:
                 spec_data["cpu"] = f"Intel {match.group(1).title()}"
            else:
                 if "CELERON" in t_upper: spec_data["cpu"] = "Intel Celeron"
                 elif "PENTIUM" in t_upper: spec_data["cpu"] = "Intel Pentium"
                 elif "G3930" in t_upper: spec_data["cpu"] = "Intel Celeron"
                 elif "I9" in t_upper: spec_data["cpu"] = "Intel Core i9" 
                 elif "I7" in t_upper: spec_data["cpu"] = "Intel Core i7"
                 elif "I5" in t_upper: spec_data["cpu"] = "Intel Core i5"
                 elif "I3" in t_upper: spec_data["cpu"] = "Intel Core i3"
             
    elif spec_data["brand"] == "AMD":
        match = re.search(r'(RYZEN\s?\d\s?\d{4}[A-Z]*)', t_upper)
        if match:
             spec_data["cpu"] = match.group(1).title()
        else:
             if "ATHLON" in t_upper: spec_data["cpu"] = "AMD Athlon"
             elif "THREADRIPPER" in t_upper: spec_data["cpu"] = "AMD Threadripper"
             elif "RYZEN 9" in t_upper: spec_data["cpu"] = "Ryzen 9"
             elif "RYZEN 7" in t_upper: spec_data["cpu"] = "Ryzen 7"
             elif "RYZEN 5" in t_upper: spec_data["cpu"] = "Ryzen 5"
             elif "RYZEN 3" in t_upper: spec_data["cpu"] = "Ryzen 3"

             elif "RYZEN 3" in t_upper: spec_data["cpu"] = "Ryzen 3"

    # 2.5 Extract Generation / Series
    generation = "Unknown"
    
    # Intel Generations
    if spec_data["brand"] == "Intel":
        if "CORE ULTRA" in t_upper: 
            if "200" in t_upper or "285K" in t_upper or "265K" in t_upper or "245K" in t_upper: 
                generation = "Core Ultra (Series 2)"
            else:
                generation = "Core Ultra (Series 1)"
        elif "14" in t_upper and ("GEN" in t_upper or re.search(r'14\d{2}', t_upper)): generation = "14th Gen"
        elif "13" in t_upper and ("GEN" in t_upper or re.search(r'13\d{2}', t_upper)): generation = "13th Gen"
        elif "12" in t_upper and ("GEN" in t_upper or re.search(r'12\d{2}', t_upper)): generation = "12th Gen"
        elif "11" in t_upper and ("GEN" in t_upper or re.search(r'11\d{2}', t_upper)): generation = "11th Gen"
        elif "10" in t_upper and ("GEN" in t_upper or re.search(r'10\d{2}', t_upper)): generation = "10th Gen"
        elif "9" in t_upper and ("GEN" in t_upper or re.search(r'9\d{2}', t_upper)): generation = "9th Gen"
        
        # Legacy/Budget
        if generation == "Unknown":
            if "CELERON" in t_upper or "PENTIUM" in t_upper or "DUAL CORE" in t_upper:
                generation = "Intel Legacy"

    # AMD Series
    elif spec_data["brand"] == "AMD":
        if "9000" in t_upper or re.search(r'9\d{3}', t_upper): generation = "Ryzen 9000 Series"
        elif "8000" in t_upper or re.search(r'8\d{3}', t_upper): generation = "Ryzen 8000 Series"
        elif "7000" in t_upper or re.search(r'7\d{3}', t_upper): generation = "Ryzen 7000 Series"
        elif "5000" in t_upper or re.search(r'5\d{3}', t_upper): generation = "Ryzen 5000 Series"
        elif "4000" in t_upper or re.search(r'4\d{3}', t_upper): generation = "Ryzen 4000 Series"
        elif "3000" in t_upper or re.search(r'3\d{3}', t_upper): generation = "Ryzen 3000 Series"

    spec_data["generation"] = generation
    
    # 3. Extract Core Count (Enhanced)
    cores = "Unknown"
    clean_text = text_upper.replace('\n', ' ').replace('\r', ' ')
    patterns = [
        r'NOMBRE DE C[OŒ]URS(?:\sDU\s(?:PROCESSEUR|CPU))?\s?:\s?([A-Z0-9-]+)',
        r'NOMBRE DE C[OŒ]URS\s?:\s?(\d+)',
        r'CORES\s?:\s?(\d+)',
        r'NB DE C[OŒ]URS\s?:\s?(\d+)',
        r'(\d+)\s*C[OŒ]URS' # e.g. "6 Coeurs"
    ]
    
    found_val = None
    for p in patterns:
        m = re.search(p, clean_text)
        if m:
            found_val = m.group(1).strip()
            break
            
    if found_val:
        if "DUAL" in found_val: cores = "2 Cores"
        elif "QUAD" in found_val: cores = "4 Cores"
        elif "HEXA" in found_val: cores = "6 Cores"
        elif "OCTA" in found_val: cores = "8 Cores"
        else:
            num_m = re.match(r'^(\d+)', found_val)
            if num_m: cores = f"{num_m.group(1)} Cores"

    # Fallback Map
    if cores == "Unknown":
        core_map = {
            "DUAL-CORE": "2 Cores", "DUAL CORE": "2 Cores",
            "QUAD-CORE": "4 Cores", "QUAD CORE": "4 Cores",
            "HEXA-CORE": "6 Cores", "HEXA CORE": "6 Cores",
            "OCTA-CORE": "8 Cores", "OCTA CORE": "8 Cores",
            "DECA-CORE": "10 Cores", "DECA CORE": "10 Cores",
            " 2 COEURS": "2 Cores", " 4 COEURS": "4 Cores",
            " 6 COEURS": "6 Cores", " 8 COEURS": "8 Cores"
        }
        for key, val in core_map.items():
            if key in text_upper or key in t_upper:
                cores = val
                break
    
    # Model Lookup
    if cores == "Unknown":
        known_models = {
            "D 450": "1 Core", "CELERON D": "1 Core",
            "12100": "4 Cores", "12100F": "4 Cores",
            "10100": "4 Cores", "10100F": "4 Cores",
            "10105F": "4 Cores", "14100F": "4 Cores", # User fix
            "12400": "6 Cores", "12400F": "6 Cores",
            "13400": "10 Cores", "13400F": "10 Cores",
            "14400": "10 Cores", "14400F": "10 Cores",
            "12600K": "10 Cores", "12600KF": "10 Cores",
            "13600K": "14 Cores", "13600KF": "14 Cores",
            "14600K": "14 Cores", "14600KF": "14 Cores",
            "12700": "12 Cores", "12700K": "12 Cores", "12700F": "12 Cores", # User fix
            "13700K": "16 Cores", "14700K": "20 Cores",
            "12900K": "16 Cores", "13900K": "24 Cores", 
            "14900K": "24 Cores", "14900KF": "24 Cores", # User fix
            
            "4500": "6 Cores", # User fix Ryzen 5 4500
            "5600": "6 Cores", "5600G": "6 Cores", "5600X": "6 Cores", "5500": "6 Cores",
            "5650G": "6 Cores", "7500F": "6 Cores", "8600G": "6 Cores", "9600X": "6 Cores", # User fixes
            "7600": "6 Cores", "7600X": "6 Cores",
            "5700X": "8 Cores", "5800X": "8 Cores", "5700G": "8 Cores",
            "7700": "8 Cores", "7700X": "8 Cores", "7800X3D": "8 Cores",
            "9700X": "8 Cores", # User fix
            "5900X": "12 Cores", "5950X": "16 Cores", "7950X": "16 Cores"
        }
        for model, count in known_models.items():
            if re.search(r'\b' + model + r'\b', t_upper):
                cores = count
                break

    # 4. Clock Speed
    clock_speed = "Unknown"
    # Logic:
    # 1. Search for explicit "Fréquence : X GHz" pattern.
    # 2. If not found, search for any "X GHz" pattern in text.
    
    # Specific patterns first (capture the value after colon)
    explicit_patterns = [
        r'FRÉQUENCE(?: DE)?(?: DU)?(?: PROCESSEUR| CPU)?\s?:\s?([^<\n\r]+)',
        r'VITESSE(?: DE)?(?: DU)?(?: PROCESSEUR| CPU)?\s?:\s?([^<\n\r]+)'
    ]
    
    found_speed = False
    for p in explicit_patterns:
        m = re.search(p, clean_text)
        if m:
            val = m.group(1).strip()
            # Now extract the first frequency number + unit from this substring
            hz_match = re.search(r'(\d+(?:[.,]\d+)?)\s?GHz', val, re.IGNORECASE)
            if hz_match:
                speed_val = hz_match.group(1).replace(',', '.')
                clock_speed = f"{speed_val} GHz"
                found_speed = True
                break
    
    # Fallback: Direct search in full text if no explicit label found
    if not found_speed:
        # Regex to find "3.6 GHz" or "3,6 GHz"
        # We use strict matching to avoid matching random numbers
        direct_match = re.search(r'(\d+(?:[.,]\d+)?)\s?GHZ', clean_text)
        if direct_match:
             speed_val = direct_match.group(1).replace(',', '.')
             clock_speed = f"{speed_val} GHz"
    
    spec_data["clock_speed"] = clock_speed
    
    # 5. Integrated Graphics
    graphics = "Unknown"
    
    # User requested specific full names:
    # 600 -> Intel UHD Graphics 600
    # 610 -> Intel HD Graphics 610
    # 7 -> AMD Radeon Vega 7 Graphics
    # 730 -> Intel UHD Graphics 730
    # 770 -> Intel UHD Graphics 770
    # 11 -> AMD Radeon Vega 11 (inferred)

    # First, try to catch the full pattern directly
    gpu_full_patterns = [
        r'(INTEL\s+UHD\s+GRAPHICS\s+\d+)',
        r'(INTEL\s+HD\s+GRAPHICS\s+\d+)',
        r'(AMD\s+RADEON\s+VEGA\s+\d+)',
        r'(RADEON\s+VEGA\s+\d+)',
        r'CARTE GRAPHIQUE\s*:\s*([^<\n\r]+)',
        r'MODÈLE DE PROCESSEUR GRAPHIQUE\s*:\s*([^<\n\r]+)'
    ]
    
    for p in gpu_full_patterns:
        m = re.search(p, clean_text, re.IGNORECASE)
        if m:
            # Prefer group 1 if it exists (specific match), else group 0 or whatever captured
            if m.lastindex:
                 val = m.group(m.lastindex).strip()
            else:
                 val = m.group(0).strip()
            
            # Clean up
            if len(val) < 40 and "GRAPHIC" in val.upper() or "RADEON" in val.upper():
                graphics = val.title() # e.g. "Intel Uhd Graphics 600"
                break
            
            # If we caught a generic text line, try to extract specific code
            if "CARTE" in p or "MODÈLE" in p:
                if "600" in val: graphics = "Intel UHD Graphics 600"
                elif "610" in val: graphics = "Intel HD Graphics 610"
                elif "730" in val: graphics = "Intel UHD Graphics 730"
                elif "770" in val: graphics = "Intel UHD Graphics 770"
                elif "VEGA 7" in val.upper(): graphics = "AMD Radeon Vega 7 Graphics"
                elif "VEGA 11" in val.upper(): graphics = "AMD Radeon Vega 11 Graphics"
                elif "RADEON" in val.upper(): graphics = val.split('-')[0].strip() # Fallback
                break

    # If still unknown or just a number was found previously (legacy logic), enforce specific mapping based on text
    if graphics == "Unknown" or len(graphics) < 4: 
        if "UHD GRAPHICS 600" in clean_text or "UHD 600" in clean_text: graphics = "Intel UHD Graphics 600"
        elif "HD GRAPHICS 610" in clean_text or "HD 610" in clean_text: graphics = "Intel HD Graphics 610"
        elif "UHD GRAPHICS 730" in clean_text or "UHD 730" in clean_text: graphics = "Intel UHD Graphics 730"
        elif "UHD GRAPHICS 770" in clean_text or "UHD 770" in clean_text: graphics = "Intel UHD Graphics 770"
        elif "VEGA 7" in clean_text: graphics = "AMD Radeon Vega 7 Graphics"
        elif "VEGA 11" in clean_text: graphics = "AMD Radeon Vega 11 Graphics"
        elif "600" in clean_text and ("J4" in t_upper or "CELERON" in t_upper): graphics = "Intel UHD Graphics 600" # Heuristic for Celeron J4xxx
      
    # Normalized Title Case
    if graphics != "Unknown":
        # Ensure consistent naming
        upper_g = graphics.upper()
        if "610" in upper_g: graphics = "Intel HD Graphics 610"
        elif "600" in upper_g: graphics = "Intel UHD Graphics 600"
        elif "VEGA 7" in upper_g: graphics = "AMD Radeon Vega 7 Graphics"
        elif "VEGA 11" in upper_g: graphics = "AMD Radeon Vega 11 Graphics"
        elif "730" in upper_g: graphics = "Intel UHD Graphics 730"
        elif "770" in upper_g: graphics = "Intel UHD Graphics 770"

    spec_data["graphics"] = graphics
    
    # 6. Memory Type
    memory_type = "Unknown"
    if "DDR5" in clean_text: memory_type = "DDR5"
    elif "DDR4" in clean_text: memory_type = "DDR4"
    elif "DDR3" in clean_text: memory_type = "DDR3"
    spec_data["memory_type"] = memory_type
    
    # 7. Thread Count
    threads = "Unknown"
    th_patterns = [
        r'NOMBRE\s+(?:DE)?\s*THREADS?\s*:\s*(\d+)',
        r'THREADS?\s*:\s*(\d+)',
        r'(\d+)\s*THREADS'
    ]
    for p in th_patterns:
        m = re.search(p, clean_text, re.IGNORECASE)
        if m:
             t_count = m.group(1).strip()
             threads = f"{t_count} Threads"
             break
    spec_data["threads"] = threads

    # 8. Memory Cache
    cache = "Unknown"
    cache_patterns = [
        r'MÉMOIRE\s+CACHE\s*:\s*([^<\n\r]+)',
        r'CACHE\s*:\s*([^<\n\r]+)',
        r'(\d+\s?MO)\s+DE\s+MÉMOIRE\s+CACHE'
    ]
    for p in cache_patterns:
        m = re.search(p, clean_text, re.IGNORECASE)
        if m:
             raw_cache = m.group(1).strip()
             # Cleanup known suffix
             split_chars = ["-", "  ", "FRÉQUENCE", "VITESSE", ")"]
             for char in split_chars:
                 if char in raw_cache.upper():
                     raw_cache = raw_cache.split(char)[0].strip()
             if len(raw_cache) < 20: 
                 cache = raw_cache
                 break
    spec_data["cache"] = cache

    spec_data["cores"] = cores
    return spec_data

def scrape_tunisianet_requests():
    print("Launching Requests Scraper for Tunisianet Processors...", flush=True)
    all_products = []
    
    try:
        page = 1
        max_pages = 5 
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
                     full_text = item.get_text().upper()
                     if "EN STOCK" in full_text and "NON DISPONIBLE" not in full_text:
                         in_stock = True
                
                if not in_stock:
                    continue 

                # 2. Extract Data
                # ID
                try:
                    p_id = item['data-id-product']
                except:
                    p_id = f"tunisianet-cpu-{random.randint(1000,9999)}"
                
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
                
                # Description
                desc_elem = item.select_one(".product-description-short") or item.select_one(".listds")
                desc_text = desc_elem.get_text(separator=" ", strip=True) if desc_elem else ""
                
                specs = extract_cpu_details(title, desc_text)
                
                product = {
                    "id": f"tunisianet-cpu-{p_id}",
                    "title": title,
                    "price": price,
                    "image": image,
                    "brand": specs["brand"],
                    "category": "cpu",
                    "source": "Tunisianet",
                    "availability": "in-stock",
                    "link": link,
                    "specs": specs
                }
                
                all_products.append(product)
                found_on_page += 1
                print(f"[{len(all_products)}] scraped: {title}")
            
            if found_on_page == 0 and page > 1:
                print("No stock items found on this page. Stopping traversal.")
                # But allow checking all pages if page 1 was empty? Unlikely.
            
            # Check for next page
            next_btn = soup.select_one("a.next.js-search-link")
            if not next_btn or "disabled" in next_btn.get("class", []):
                print("No next page button found or disabled. Stopping.")
                break
                
            page += 1
            time.sleep(1) # Be polite
            
    except Exception as e:
        print(f"Error during scraping: {e}")
        
    print(f"Total extracted: {len(all_products)}")
    
    # Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_tunisianet_requests()
