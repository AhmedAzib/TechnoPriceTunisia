from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import re
import os
import random

# Configuration
BASE_URL = "https://www.mytek.tn/informatique/composants-informatique/processeur.html"
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\mytek_processors.json"

def clean_price(price_str):
    if not price_str:
        return 0.0
    # Handle "1 234,567 DT" or similar formats
    clean = price_str.upper().replace('TND', '').replace('DT', '').replace('\u00a0', '').strip()
    clean = clean.replace(',', '.') 
    # Remove all non-numeric/dot characters (allow one dot)
    clean = re.sub(r'[^\d.]', '', clean)
    try:
        return float(clean)
    except ValueError:
        return 0.0

def extract_cpu_details(title, full_text=""):
    spec_data = {
        "category": "cpu", # Normalized to 'cpu' by frontend
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
        
    # 2. Extract CPU Model
    if spec_data["brand"] == "Intel":
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

    # 2.5 Extract Generation / Series
    generation = "Unknown"
    
    # Intel Generations
    if spec_data["brand"] == "Intel":
        if "CORE ULTRA" in t_upper: 
            if "200" in t_upper or "285K" in t_upper or "265K" in t_upper or "245K" in t_upper or "225" in t_upper: 
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
    # Priority 1: Check Explicit Descriptive Patterns in full text
    cores = "Unknown"
    
    clean_text = text_upper.replace('\n', ' ').replace('\r', ' ')
    patterns = [
        r'NOMBRE DE C[OŒ]URS(?:\sDU\s(?:PROCESSEUR|CPU))?\s?:\s?([A-Z0-9-]+)',
        r'NOMBRE DE C[OŒ]URS\s?:\s?(\d+)',
        r'CORES\s?:\s?(\d+)',
        r'NB DE C[OŒ]URS\s?:\s?(\d+)'
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
        elif "DECA" in found_val: cores = "10 Cores"
        elif "DODECA" in found_val: cores = "12 Cores"
        else:
            num_m = re.match(r'^(\d+)', found_val)
            if num_m: cores = f"{num_m.group(1)} Cores"

    # Priority 2: Fallback to Title/Text Keywords
    if cores == "Unknown":
        core_map = {
            "DUAL-CORE": "2 Cores", "DUAL CORE": "2 Cores",
            "QUAD-CORE": "4 Cores", "QUAD CORE": "4 Cores",
            "HEXA-CORE": "6 Cores", "HEXA CORE": "6 Cores",
            "OCTA-CORE": "8 Cores", "OCTA CORE": "8 Cores",
            "DECA-CORE": "10 Cores", "DECA CORE": "10 Cores",
            " 2 COEURS": "2 Cores", " 4 COEURS": "4 Cores",
            " 6 COEURS": "6 Cores", " 8 COEURS": "8 Cores",
            " 10 COEURS": "10 Cores", " 12 COEURS": "12 Cores", " 14 COEURS": "14 Cores", " 16 COEURS": "16 Cores", " 24 COEURS": "24 Cores"
        }
        for key, val in core_map.items():
            if key in text_upper or key in t_upper:
                cores = val
                break
                
    # Priority 3: Model-Based Lookup (The "Safe" Fallback)
    if cores == "Unknown":
        # Extract potential model number
        # Matches: 12100F, 14900K, 5600X, 265K, 225F
        model_match = re.search(r'([A-Z]?\d{3,5}[A-Z]*)', t_upper.replace("CORE", "").replace("RYZEN", "").replace("INTEL", "").replace("AMD", ""))
        
        # Specific dictionary for known models (User provided list + common ones)
        known_models = {
            # Intel i3 (4 Cores usually)
            "12100": "4 Cores", "12100F": "4 Cores",
            "10100": "4 Cores", "10100F": "4 Cores",
            "13100": "4 Cores", "13100F": "4 Cores",
            "14100": "4 Cores", "14100F": "4 Cores",
            
            # Intel i5 (6 or 10 or 14 Cores)
            "12400": "6 Cores", "12400F": "6 Cores",
            "13400": "10 Cores", "13400F": "10 Cores",
            "14400": "10 Cores", "14400F": "10 Cores",
            "12600K": "10 Cores", "12600KF": "10 Cores",
            "13600K": "14 Cores", "13600KF": "14 Cores",
            "14600K": "14 Cores", "14600KF": "14 Cores",
            
            # Intel i7 (12 or 16 or 20 Cores)
            "12700": "12 Cores", "12700F": "12 Cores", "12700K": "12 Cores", "12700KF": "12 Cores",
            "13700": "16 Cores", "13700F": "16 Cores", "13700K": "16 Cores", "13700KF": "16 Cores",
            "14700": "20 Cores", "14700F": "20 Cores", "14700K": "20 Cores", "14700KF": "20 Cores",
            
            # Intel i9 (16 or 24 Cores)
            "12900": "16 Cores", "12900F": "16 Cores", "12900K": "16 Cores", "12900KF": "16 Cores", "12900KS": "16 Cores",
            "13900": "24 Cores", "13900F": "24 Cores", "13900K": "24 Cores", "13900KF": "24 Cores", "13900KS": "24 Cores",
            "14900": "24 Cores", "14900F": "24 Cores", "14900K": "24 Cores", "14900KF": "24 Cores", "14900KS": "24 Cores",
            
            # Intel Core Ultra (Series 2)
            "285K": "24 Cores", "265K": "20 Cores", "245K": "14 Cores", "225": "10 Cores", "225F": "10 Cores",
            
            # AMD Ryzen 5 (6 Cores)
            "5600": "6 Cores", "5600G": "6 Cores", "5600X": "6 Cores", "5500": "6 Cores", "5600GT": "6 Cores",
            "7600": "6 Cores", "7600X": "6 Cores", "7500F": "6 Cores",
            "8600G": "6 Cores", "8500G": "6 Cores",
            "9600X": "6 Cores",
            
            # AMD Ryzen 7 (8 Cores)
            "5700X": "8 Cores", "5800X": "8 Cores", "5800X3D": "8 Cores", "5700G": "8 Cores",
            "7700": "8 Cores", "7700X": "8 Cores", "7800X3D": "8 Cores",
            "8700G": "8 Cores",
            "9700X": "8 Cores",
            
            # AMD Ryzen 9 (12 or 16 Cores)
            "5900X": "12 Cores", "5950X": "16 Cores",
            "7900": "12 Cores", "7900X": "12 Cores", "7900X3D": "12 Cores",
            "7950X": "16 Cores", "7950X3D": "16 Cores",
            "9900X": "12 Cores", "9950X": "16 Cores"
        }
        
        # Check specifically for model string presence
        for model, core_count in known_models.items():
            # Word boundary check is safer: "i5-12400" should match "12400"
            if re.search(r'\b' + model + r'\b', t_upper) or re.search(r'-' + model + r'\b', t_upper):
                cores = core_count
                break

    # 4. Extract Clock Speed (Fréquence)
    # Patterns: "Fréquence de Processeur: 3,40 GHz", "Fréquence de Processeur: 3.30 GHz Up to 4.30 GHz"
    clock_speed = "Unknown"
    
    # Generic Regex for Fréquence line
    # Match "Fréquence ... : <capturing group>"
    frq_patterns = [
        r'FRÉQUENCE(?: DE)?(?: DU)?(?: PROCESSEUR| CPU)?\s?:\s?([^<\n\r]+)',
        r'VITESSE(?: DE)?(?: DU)?(?: PROCESSEUR| CPU)?\s?:\s?([^<\n\r]+)'
    ]
    
    for p in frq_patterns:
        m = re.search(p, clean_text)
        if m:
            val = m.group(1).strip()
            
            # User Change: Extract ONLY the first frequency (e.g. "3.40 GHz")
            # Look for: Number (with optional decimal) followed optionally by space and GHz
            # Regex: (\d+(?:[.,]\d+)?) ?GHz
            
            hz_match = re.search(r'(\d+(?:[.,]\d+)?)\s?GHz', val, re.IGNORECASE)
            if hz_match:
                # Normalize: Replace comma with dot
                speed_val = hz_match.group(1).replace(',', '.')
                clock_speed = f"{speed_val} GHz"
                break
            elif "UP TO" in val.upper() or "JUSQU" in val.upper():
                 pass
    
    # User Fixes (Manual Override if Unknown)
    if clock_speed == "Unknown":
        if "5500GT" in t_upper: clock_speed = "3.6 GHz"
        if "3600" in t_upper: clock_speed = "3.6 GHz" # Also fix 3600 just in case

    spec_data["clock_speed"] = clock_speed
    
    # 5. Extract Integrated Graphics
    # Patterns: "Carte graphique: Intel® UHD Graphics 610", "Modèle de processeur graphique: AMD Radeon™ 780M"
    graphics = "Unknown"
    gpu_patterns = [
        r'CARTE GRAPHIQUE\s*:\s*([^<\n\r]+)',
        r'MODÈLE DE PROCESSEUR GRAPHIQUE\s*:\s*([^<\n\r]+)',
        r'DATE DE LANCEMENT\s*:\s*([^<\n\r]+)' # Sometimes layout shifts, but let's stick to graphics text
    ]
    # We only want graphics lines.
    
    for p in [r'CARTE GRAPHIQUE\s*:\s*([^<\n\r]+)', r'MODÈLE DE PROCESSEUR GRAPHIQUE\s*:\s*([^<\n\r]+)', r'CHIPSET GRAPHIQUE\s*:\s*([^<\n\r]+)']:
        m = re.search(p, clean_text, re.IGNORECASE)
        if m:
            raw_gpu = m.group(1).strip()
            # Stop at the first " - " or "  " or "Fréquence" or meaningful delimiter
            # MyTek PDP text often looks like: "Intel UHD 610 - Fréquence..."
            split_chars = [" -", "  ", "FRÉQUENCE"] 
            for char in split_chars:
                if char in raw_gpu.upper():
                    raw_gpu = raw_gpu.split(char)[0].strip() # Take first part
                    
            clean_gpu = raw_gpu.replace('®', '').replace('™', '').strip()
            
            # Remove purely generic text if needed or keep full model
            # keeping full model is better: "Intel UHD Graphics 730"
            if clean_gpu and len(clean_gpu) > 2 and len(clean_gpu) < 50: # Sanity check length
                graphics = clean_gpu
                break

    spec_data["graphics"] = graphics
    
    spec_data["graphics"] = graphics
    
    # 6. Extract Memory Type
    # Patterns: "Types de mémoire: DDR4-2666", "Mémoire: DDR5"
    memory_type = "Unknown"
    # We look for "TYPES DE MÉMOIRE" or just "MÉMOIRE" followed by colon
    # But "Mémoire Cache" is different, so exclude that.
    
    # Pattern 1: Specific "TYPES DE MÉMOIRE"
    # Pattern 2: "MÉMOIRE" but NOT "CACHE"
    
    mem_patterns = [
        r'TYPES? DE MÉMOIRES?\s*:\s*([^<\n\r]+)',
        r'(?<!CACHE )(?<!VITESSE )MÉMOIRE\s*:\s*([^<\n\r]+)' # Negative lookbehind to avoid "Mémoire Cache" or "Vitesse Mémoire"
    ]
    
    for p in mem_patterns:
        m = re.search(p, clean_text, re.IGNORECASE)
        if m:
            raw_mem = m.group(1).strip()
            # Clean up unique MyTek separators
            split_chars = [" -", "  ", "FRÉQUENCE", "NOMBRE"] 
            for char in split_chars:
                if char in raw_mem.upper():
                    raw_mem = raw_mem.split(char)[0].strip()
            
            if len(raw_mem) > 2 and len(raw_mem) < 50:
                 # User Request: Simplify to just "DDR4" or "DDR5"
                 upper_mem = raw_mem.upper()
                 if "DDR5" in upper_mem:
                     memory_type = "DDR5"
                     # Note: Some CPUs support both, but usually MyTek lists the main one or just "DDR5" for newer ones.
                     # If it says "DDR4/DDR5" we might want to handle it, but for now let's prioritize newer tech or just simple detection.
                     # actually, if both are present, we might want to flag it. 
                     # But user asked for "2 section... DDR4 and ... DDR5".
                     # If I set it to "DDR5", it only shows in DDR5.
                     # Let's stick to simple normalization.
                 elif "DDR4" in upper_mem:
                     memory_type = "DDR4"
                 elif "DDR3" in upper_mem:
                     memory_type = "DDR3" # Just in case
                 else:
                     memory_type = raw_mem # Fallback if neither found
                 break
                 
    spec_data["memory_type"] = memory_type
    
    # 7. Extract Thread Count
    # Patterns: "Nombre de Threads: 16"
    threads = "Unknown"
    
    # Generic Regex
    th_patterns = [
        r'NOMBRE\s+(?:DE)?\s*THREADS?\s*:\s*(\d+)',
        r'THREADS?\s*:\s*(\d+)'
    ]
    
    for p in th_patterns:
        m = re.search(p, clean_text, re.IGNORECASE)
        if m:
             # Just get the number
             t_count = m.group(1).strip()
             threads = f"{t_count} Threads"
             break
             
    spec_data["threads"] = threads

    # 8. Extract Memory Cache
    # Patterns: "Mémoire Cache: 32 Mo", "Mémoire Cache: 16 Mo"
    cache = "Unknown"
    
    # Generic Regex
    # Match "Mémoire Cache : <value>"
    cache_patterns = [
        r'MÉMOIRE\s+CACHE\s*:\s*([^<\n\r]+)',
        r'CACHE\s*:\s*([^<\n\r]+)'
    ]
    
    for p in cache_patterns:
        m = re.search(p, clean_text, re.IGNORECASE)
        if m:
             raw_cache = m.group(1).strip()
             # Clean up common suffixes if any weird text follows
             # Usually "32 Mo" or "32 MB" or "32 Mo SmartCache"
             # Stop at " - " or "  "
             split_chars = ["-", "  ", "FRÉQUENCE", "VITESSE", "GARANTIE"] 
             for char in split_chars:
                if char in raw_cache.upper():
                    raw_cache = raw_cache.split(char)[0].strip()
             
             if len(raw_cache) < 20: # Sanity check
                 cache = raw_cache
                 break
                 
    spec_data["cache"] = cache

    spec_data["cores"] = cores
    return spec_data

def scrape_selenium():
    print("Launching Selenium for MyTek Processors...", flush=True)
    options = Options()
    # options.add_argument("--headless=new") # Run headless for speed, or remove to debug visually
    # Keeping visible might be safer for anti-bot, but headless usually works for MyTek if User-Agent is set.
    # User requested robust antibot handling. Headless sometimes triggers bots.
    # Let's try headless first with good UA, but if it fails we can switch.
    options.add_argument("--headless=new") 
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled") # Key for anti-bot
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    
    all_products = []
    seen_links = set()
    
    try:
        page = 1
        max_pages = 10 # Processors shouldn't have that many pages
        
        while page <= max_pages:
            url = f"{BASE_URL}?p={page}"
            print(f"Navigating to Page {page}: {url}", flush=True)
            driver.get(url)
            
            # Robust Wait: Wait for title OR product container
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".product-container, .message.info.empty"))
                )
            except:
                print("Timeout waiting for content. Retrying once...", flush=True)
                driver.refresh()
                time.sleep(5)
            
            # Aggressive Scroll to trigger all lazy loading
            last_height = driver.execute_script("return document.body.scrollHeight")
            for _ in range(3): # Scroll down in steps
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            # Scroll back up a bit just in case header covers something (rare but possible)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            items = soup.select(".product-container")
            
            if not items:
                print(f"No items found on page {page}. Stopping.", flush=True)
                break
                
            page_products = []
            for item in items:
                try:
                    link_elem = item.select_one(".product-item-link")
                    if not link_elem: continue
                    
                    title = link_elem.text.strip()
                    link = link_elem['href']
                    
                    if link in seen_links: continue
                    
                    # Image
                    img_elem = item.select_one(".product-item-photo img")
                    if not img_elem: img_elem = item.select_one("img")
                    image = img_elem['src'] if img_elem else ""
                    
                    # Price
                    price_elem = item.select_one(".final-price")
                    if not price_elem: price_elem = item.select_one(".price")
                    if not price_elem: price_elem = item.select_one(".price-box .price")
                    price_text = price_elem.text.strip() if price_elem else "0"
                    price = clean_price(price_text)
                    
                    # Availability
                    availability = "in-stock"
                    if "épuisé" in item.text.lower() or "hors stock" in item.text.lower():
                        availability = "out-of-stock"

                    # Description / Features Text (For Core Count)
                    # Try to get the description block or the full item text
                    desc_elem = item.select_one(".product-item-description")
                    full_text = item.text.upper() # Use full card text as fallback
                    if desc_elem:
                        full_text += " " + desc_elem.text.upper()

                    # Specs
                    spec_data = extract_cpu_details(title, full_text)
                    
                    # ID
                    pid = f"mytek-cpu-{len(seen_links) + 1}"
                    seen_links.add(link)
                    
                    p = {
                        "id": pid,
                        "title": title,
                        "price": price,
                        "image": image,
                        "brand": spec_data["brand"],
                        "category": spec_data["category"],
                        "source": "MyTek", 
                        "availability": availability,
                        "link": link,
                        "specs": spec_data
                    }
                    page_products.append(p)
                    
                except Exception as e:
                    print(f"Error parsing item: {e}")
                    continue
            
            print(f"   + Found {len(page_products)} products on page {page}", flush=True)
            all_products.extend(page_products)
            
            # Check Next Button
            next_btn = soup.select_one(".pages-item-next")
            if not next_btn:
                 # Alternative selector
                 next_btn = soup.select_one("a[title='Suivant']")
            
            if not next_btn:
                print("No next button found. End of catalogue.", flush=True)
                break
                
            page += 1
            # Random delay to be nice
            time.sleep(random.uniform(2, 4))
            
    except Exception as e:
        print(f"Critical Error during pagination: {e}", flush=True)

    # Phase 2: Visit each product for details
    print("Phase 2: Visiting product pages for detailed specs...", flush=True)
    count = 0
    for p in all_products:
        count += 1
        print(f"[{count}/{len(all_products)}] details: {p['title']}", flush=True)
        try:
             driver.get(p['link'])
             # Wait for body or specific element
             WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
             
             soup_pdp = BeautifulSoup(driver.page_source, 'html.parser')
             
             # Combined text from likely extraction points
             text_content = ""
             
             # Short description
             short_desc = soup_pdp.select_one('.product-info-main')
             if short_desc: text_content += " " + short_desc.get_text(" ", strip=True)
             
             # Attributes table/tab
             attrs = soup_pdp.select_one('#additional') 
             if attrs: text_content += " " + attrs.get_text(" ", strip=True)
             
             # Description tab
             desc_tab = soup_pdp.select_one('#description')
             if desc_tab: text_content += " " + desc_tab.get_text(" ", strip=True)
             
             # Re-run extraction with high-res text
             new_specs = extract_cpu_details(p['title'], text_content)
             
             # Update specs
             p['specs'] = new_specs
             # Update top level props if needed
             p['brand'] = new_specs['brand']
             
             time.sleep(0.5) 
             
        except Exception as e:
             print(f"Failed to scrape details for {p['title']}: {e}")

    driver.quit()
        
    print(f"Total extracted: {len(all_products)}", flush=True)
    
    if all_products:
        # Create dir if not exists
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        print(f"Saved to {OUTPUT_FILE}", flush=True)
    else:
        print("No products extracted. Nothing saved.", flush=True)

if __name__ == "__main__":
    scrape_selenium()
