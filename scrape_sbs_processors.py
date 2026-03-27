from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import re
import random

# Configuration
BASE_URL = "https://www.sbsinformatique.com/processeur-tunisie"
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\sbs_processors.json"

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

def extract_cpu_details_from_pdp(driver):
    spec_data = {
        "category": "cpu",
        "cpu": "Unknown",
        "brand": "Unknown",
        "generation": "Unknown",
        "cores": "Unknown",
        "clock_speed": "Unknown",
        "graphics": "Unknown",
        "memory_type": "Unknown",
        "threads": "Unknown",
        "cache": "Unknown"
    }
    
    # Get all text from the page to use as context
    try:
        # Try to find the specs table or list
        # Look for "Fiche technique" or similar
        full_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Also try to specifically target spec rows if possible
        # SBS likely uses a table structure for specs
    except:
        full_text = ""

    t_upper = ""
    try:
        title_elem = driver.find_element(By.TAG_NAME, "h1")
        t_upper = title_elem.text.upper()
    except:
        pass
        
    specs_map = {}
    
    # Iterate through potential spec rows (generic approach for SBS)
    # Often in tables tr > th/td or dl > dt/dd
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "tr") # Generic table row
        for row in rows:
            try:
                col1 = row.find_element(By.CSS_SELECTOR, "th").text.strip().upper()
                col2 = row.find_element(By.CSS_SELECTOR, "td").text.strip()
                specs_map[col1] = col2
            except:
                continue
                
        # Also check for li or other structures
        if not specs_map:
             items = driver.find_elements(By.CSS_SELECTOR, "li")
             for item in items:
                 text = item.text
                 if ":" in text:
                     parts = text.split(":", 1)
                     specs_map[parts[0].strip().upper()] = parts[1].strip()
    except:
        pass

    # 1. Brand
    if "INTEL" in t_upper or "CORE" in t_upper: spec_data["brand"] = "Intel"
    elif "AMD" in t_upper or "RYZEN" in t_upper: spec_data["brand"] = "AMD"
    
    # 2. CPU Model
    if spec_data["brand"] == "Intel":
        match = re.search(r'(CORE\s?I\d[-\s]?\d{4,5}[A-Z]?)', t_upper)
        if match: spec_data["cpu"] = f"Intel {match.group(1).title()}"
        elif "CELERON" in t_upper: spec_data["cpu"] = "Intel Celeron"
        elif "PENTIUM" in t_upper: spec_data["cpu"] = "Intel Pentium"
        elif "ULTRA" in t_upper: spec_data["cpu"] = "Intel Core Ultra"
    elif spec_data["brand"] == "AMD":
        match = re.search(r'(RYZEN\s?\d\s?\d{4}[A-Z]*)', t_upper)
        if match: spec_data["cpu"] = match.group(1).title()
        elif "ATHLON" in t_upper: spec_data["cpu"] = "AMD Athlon"

    # 3. Specs from Map
    text_blob = (full_text + " " + " ".join([f"{k} {v}" for k,v in specs_map.items()])).upper()
    
    # Cores
    # "Nombre de core 2"
    cores = "Unknown"
    core_val = specs_map.get("NOMBRE DE CORE") or specs_map.get("NB DE COEURS")
    if not core_val:
        m = re.search(r'NOMBRE DE CORE\s?:\s?(\d+)', text_blob)
        if m: core_val = m.group(1)
        else:
             m = re.search(r'NOMBRE DE CORE\s+(\d+)', text_blob) # User example: "Nombre de core 2" (no colon?)
             if m: core_val = m.group(1)

    if core_val:
        cores = f"{core_val} Cores"
    
    # Fallback Cores Logic (Same as others)
    if cores == "Unknown":
        known_models = {
            "G5905": "2 Cores", "G6405": "2 Cores", "G3930": "2 Cores", "G4900": "2 Cores",
            "12100": "4 Cores", "10100": "4 Cores", "10105": "4 Cores", "14100": "4 Cores", "13100": "4 Cores", "9100": "4 Cores",
            "12400": "6 Cores", "11400": "6 Cores", "10400": "6 Cores", "9400": "6 Cores", "8400": "6 Cores",
            "12600": "10 Cores", "13400": "10 Cores", "14400": "10 Cores",
            "12700": "12 Cores", "12700K": "12 Cores", "12700KF": "12 Cores",
            "13600": "14 Cores", "14600": "14 Cores",
            "13700": "16 Cores", "14700": "20 Cores",
            "12900": "16 Cores", "13900": "24 Cores", "14900": "24 Cores", "285K": "24 Cores",
            "4500": "6 Cores", "5500": "6 Cores", "5600": "6 Cores", "5600G": "6 Cores", "5600X": "6 Cores",
            "7500F": "6 Cores", "7600": "6 Cores", "8600G": "6 Cores", "9600X": "6 Cores", "3600": "6 Cores", "4600G": "6 Cores", "4650G": "6 Cores",
            "5700": "8 Cores", "5800": "8 Cores", "7700": "8 Cores", "9700": "8 Cores", "3700X": "8 Cores", "3800X": "8 Cores", "9800X3D": "8 Cores",
            "5900": "12 Cores", "7900": "12 Cores", "9900": "12 Cores",
            "5950": "16 Cores", "7950": "16 Cores", "9950": "16 Cores", "2950X": "16 Cores"
        }
        for model, count in known_models.items():
            # Simple substring check (stripped of F/K/X suffixes for generic match if needed, but here we list bases)
            # We check if the model number appears in the title
            if model in t_upper:
                cores = count
                break
    spec_data["cores"] = cores

    # Frequency
    # "Fréquence CPU 3,5 GHz"
    clock_speed = "Unknown"
    freq_val = specs_map.get("FRÉQUENCE CPU")
    if not freq_val:
        m = re.search(r'FRÉQUENCE CPU\s?[:\s]?\s?(\d+(?:[.,]\d+)?)\s?GHZ', text_blob)
        if m: 
            clock_speed = f"{m.group(1).replace(',', '.')} GHz"
    else:
        m = re.search(r'(\d+(?:[.,]\d+)?)', freq_val)
        if m: clock_speed = f"{m.group(1).replace(',', '.')} GHz"
        
    spec_data["clock_speed"] = clock_speed

    # Threads
    threads = "Unknown"
    th_val = specs_map.get("NOMBRE DE THREADS")
    if not th_val:
        m = re.search(r'NOMBRE DE THREADS\s?[:\s]?\s?(\d+)', text_blob)
        if m: th_val = m.group(1)
    
    if th_val: threads = f"{th_val} Threads"
    spec_data["threads"] = threads

    # Generation
    generation = "Unknown"
    if spec_data["brand"] == "Intel":
        if "14" in t_upper and ("GEN" in t_upper or re.search(r'14\d{2}', t_upper)): generation = "14th Gen"
        elif "13" in t_upper and ("GEN" in t_upper or re.search(r'13\d{2}', t_upper)): generation = "13th Gen"
        elif "12" in t_upper and ("GEN" in t_upper or re.search(r'12\d{2}', t_upper)): generation = "12th Gen"
        elif "11" in t_upper and ("GEN" in t_upper or re.search(r'11\d{2}', t_upper)): generation = "11th Gen"
        elif "10" in t_upper and ("GEN" in t_upper or re.search(r'10\d{2}', t_upper)): generation = "10th Gen"
        elif "CELERON" in t_upper or "PENTIUM" in t_upper: generation = "Intel Legacy"
    elif spec_data["brand"] == "AMD":
        if "9000" in t_upper or re.search(r'9\d{3}', t_upper): generation = "Ryzen 9000 Series"
        elif "8000" in t_upper or re.search(r'8\d{3}', t_upper): generation = "Ryzen 8000 Series"
        elif "7000" in t_upper or re.search(r'7\d{3}', t_upper): generation = "Ryzen 7000 Series"
        elif "5000" in t_upper or re.search(r'5\d{3}', t_upper): generation = "Ryzen 5000 Series"
        elif "4000" in t_upper or re.search(r'4\d{3}', t_upper): generation = "Ryzen 4000 Series"
        elif "3000" in t_upper or re.search(r'3\d{3}', t_upper): generation = "Ryzen 3000 Series"
    
    spec_data["generation"] = generation

    return spec_data

def scrape_sbs_processors():
    print("Launching Selenium for SBS Informatique Processors...", flush=True)
    all_products = []
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # 1. Scrape Listing Pages to get URLs
        product_urls = []
        page = 1
        while page <= 3: # Assuming 30 products -> ~2-3 pages max
            url = f"{BASE_URL}?page={page}"
            if page == 1: url = BASE_URL
            
            print(f"Navigating to Page {page}: {url}", flush=True)
            driver.get(url)
            time.sleep(3)
            
            items = driver.find_elements(By.CSS_SELECTOR, "article.product-miniature, .product-miniature") # Typical Prestashop selector, verify if needed
             # Wait, SBS selector might be different. Let's try broad search.
            if not items:
                items = driver.find_elements(By.CSS_SELECTOR, ".product-container, .item-product")
            
            if not items:
                 # Fallback: look for any links with 'processeur' in href
                 links = driver.find_elements(By.CSS_SELECTOR, "a")
                 for l in links:
                     href = l.get_attribute('href')
                     if href and "processeur-" in href and href not in product_urls:
                         product_urls.append(href)
            else:
                for item in items:
                    try:
                        link_elem = item.find_element(By.TAG_NAME, "a")
                        href = link_elem.get_attribute('href')
                        if href and href not in product_urls:
                            product_urls.append(href)
                    except:
                        continue
            
            # Check for next page
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "a.next")
                if not next_btn: break
            except:
                pass
                
            page += 1
        
        # Remove duplicates and irrelevant links
        product_urls = list(set([u for u in product_urls if "processeur" in u or "amd" in u or "intel" in u]))
        print(f"Found {len(product_urls)} product links. Starting extraction...", flush=True)
        
        # 2. Visit Each Product
        for i, link in enumerate(product_urls):
            print(f"[{i+1}/{len(product_urls)}] Scraping {link}...")
            try:
                driver.get(link)
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
                
                # Title
                title = driver.find_element(By.TAG_NAME, "h1").text.strip()
                
                # Price
                try:
                    # Prefer .current-price as it seems most reliable
                    try:
                         price_elem = driver.find_element(By.CSS_SELECTOR, ".current-price")
                         price_text = price_elem.text.strip()
                    except:
                         # Fallback to finding any price with text
                         candidates = driver.find_elements(By.CSS_SELECTOR, ".price, .product-price")
                         price_text = ""
                         for c in candidates:
                             if c.text.strip():
                                 price_text = c.text.strip()
                                 break
                    
                    price = clean_price(price_text)
                except:
                    price = 0.0
                
                # Image
                try:
                    img_elem = driver.find_element(By.CSS_SELECTOR, ".images-container img, #bigpic")
                    image = img_elem.get_attribute('src')
                except:
                    image = ""
                    
                # Specs
                specs = extract_cpu_details_from_pdp(driver)
                
                product = {
                    "id": f"sbs-cpu-{random.randint(10000,99999)}",
                    "title": title,
                    "price": price,
                    "image": image,
                    "brand": specs["brand"],
                    "category": "cpu",
                    "source": "SBS Informatique",
                    "availability": "in-stock", # Assuming if scraping PDP it exists, check availability text if needed
                    "link": link,
                    "specs": specs
                }
                
                # Quick Availability Check
                try:
                     avail_text = driver.find_element(By.ID, "product-availability").text.upper()
                     if "RUPTURE" in avail_text or "OUT OF STOCK" in avail_text:
                         product["availability"] = "out-of-stock"
                except:
                    pass
                
                if product["availability"] == "in-stock":
                    all_products.append(product)
                    
                time.sleep(1) # Polite delay
                
            except Exception as e:
                print(f"Error scraping product {link}: {e}")
                continue
                
    except Exception as e:
        print(f"Global Error: {e}")
    finally:
        driver.quit()
        
    print(f"Total extracted: {len(all_products)}")
    
    # Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_sbs_processors()
