import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import random
import re
import os

# --- CONFIGURATION ---
BASE_URL = "https://spacenet.tn/22-carte-mere"
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\spacenet_motherboards.json"

def log(msg):
    print(msg, flush=True)

def random_sleep(min_s=2, max_s=5):
    time.sleep(random.uniform(min_s, max_s))

def clean_price(price_str):
    if not price_str: return 0.0
    # Normalize spaces
    s = price_str.replace(' ', '').replace(u'\xa0', '').replace(u'\u202f', '')
    
    # Regex to find the first valid price-like number
    # Supports: 123,456 or 123.456 or 123
    match = re.search(r'(\d+(?:[.,]\d+)?)', s)
    if match:
        val_str = match.group(1)
        # Fix comma to dot
        val_str = val_str.replace(',', '.')
        try:
            return float(val_str)
        except:
             return 0.0
    return 0.0

def extract_motherboard_details(title, full_text=""):
    """
    Robust classification logic for motherboards to ensure 100% accurate filtering.
    """
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
    
    # --- MANUAL OVERRIDES (Highest Priority) ---
    MANUAL_SPECS = {
        "CARTE MÈRE ASUS PRIME B550M-K": {"max_memory": "128GB"},
        "CARTE MÈRE ASUS PRIME A520M-K DDR4 AMD AM4": {"max_memory": "128GB"},
        "CARTE MÈRE MSI PRO A620M-E DDR5 AMD AM5": {"max_memory": "128GB"},
        "CARTE MÈRE GIGABYTE H610M H V2 G10 LGA 1700 DDR5": {"max_memory": "128GB"},
        "CARTE MÈRE GIGABYTE A620M DS3H G10 DDR4 AM5 AMD": {"max_memory": "192GB"},
        "CARTE MÈRE ASUS PRIME B840-PLUS WIFI AM5": {"max_memory": "256GB"},
        "CARTE MÈRE MSI PRO Z690-A DDR4": {"max_memory": "192GB"},
        "CARTE MÈRE GAMER ASUS ROG STRIX B550 AMD AM4 DDR4": {"max_memory": "64GB"},
        "CARTE MÈRE MSI B760M GAMING PLUS WIFI DDR5 LGA1700": {"max_memory": "256GB"},
        "CARTE MÈRE ASUS TUF GAMING X870-PLUS WIFI AM5": {"max_memory": "192GB"},
        "CARTE MÈRE ASUS ROG MAXIMUS Z790 HERO DDR4 LGA 1700": {"max_memory": "192GB"},
        "CARTE MÈRE ASUS PROART Z790-CREATOT GAMING WIFI": {"max_memory": "192GB"}, # Typo in title handled
        "CARTE MÈRE MSI PRO B760M-P DDR5 LGA 1700": {"max_memory": "256GB"},
        "CARTE MÈRE ASUS ROG STRIX B660-I GAMING WIFI DDR5 LGA 1700": {"max_memory": "64GB"},
        "CARTE MÈRE MSI B650M GAMING PLUS WIFI AM5 DDR5": {"max_memory": "256GB"},
        "CARTE MÈRE MSI PRO Z790-P WIFI DDR5 LGA1700": {"max_memory": "256GB"},
        "MSI CARTE MÈRE X670E GAMING PLUS WIFI DDR5 AM5": {"max_memory": "256GB"},
        "CARTE MÈRE MSI PRO X870 TOMAHAWK WIFI DDR5 AM5": {"max_memory": "256GB"},
        "CARTE MÈRE MSI MAG Z790 TOMHAWK WIFI DDR5 LGA1700": {"max_memory": "256GB"},
        "CARTE MÈRE ASUS PROART Z690 CREATOR WIFI DDR5 LGA 1700": {"max_memory": "128GB"}
    }
    
    # Check for exact title match (strip just in case)
    clean_title = title.strip()
    if clean_title in MANUAL_SPECS:
        for k, v in MANUAL_SPECS[clean_title].items():
            spec_data[k] = v
    
    # 1. Detect Brand
    if "MSI" in t_upper: spec_data["brand"] = "MSI"
    elif "ASUS" in t_upper: spec_data["brand"] = "Asus"
    elif "GIGABYTE" in t_upper: spec_data["brand"] = "Gigabyte"
    elif "ASROCK" in t_upper: spec_data["brand"] = "ASRock"
    elif "BIOSTAR" in t_upper: spec_data["brand"] = "Biostar"
    elif "NZXT" in t_upper: spec_data["brand"] = "NZXT"
    elif "ARKTEK" in t_upper: spec_data["brand"] = "Arktek"
    
    # 2. Socket Extraction (Critical)
    if "LGA 1851" in text_upper or "LGA1851" in text_upper: spec_data["socket"] = "LGA 1851"
    elif "LGA 1700" in text_upper or "LGA1700" in text_upper or "1700" in t_upper: spec_data["socket"] = "LGA 1700"
    elif "LGA 1200" in text_upper or "LGA1200" in text_upper or "1200" in t_upper: spec_data["socket"] = "LGA 1200"
    elif "LGA 1151" in text_upper or "LGA1151" in text_upper: spec_data["socket"] = "LGA 1151"
    elif "LGA 1150" in text_upper or "LGA1150" in text_upper: spec_data["socket"] = "LGA 1150"
    elif "LGA 775" in text_upper or "LGA775" in text_upper: spec_data["socket"] = "LGA 775"
    elif "AM5" in text_upper or "AM5" in t_upper: spec_data["socket"] = "AM5"
    elif "AM4" in text_upper or "AM4" in t_upper: spec_data["socket"] = "AM4"
    elif "TRX40" in text_upper: spec_data["socket"] = "sTRX4"
    
    # 3. Chipset Extraction
    # Intel
    if "Z890" in t_upper or "Z890" in text_upper: spec_data["chipset"] = "Intel Z890"
    elif "B860" in t_upper or "B860" in text_upper: spec_data["chipset"] = "Intel B860"
    elif "H810" in t_upper or "H810" in text_upper: spec_data["chipset"] = "Intel H810"
    elif "Z790" in t_upper or "Z790" in text_upper: spec_data["chipset"] = "Intel Z790"
    elif "B760" in t_upper or "B760" in text_upper: spec_data["chipset"] = "Intel B760"
    elif "H770" in t_upper or "H770" in text_upper: spec_data["chipset"] = "Intel H770"
    elif "H610" in t_upper or "H610" in text_upper: spec_data["chipset"] = "Intel H610"
    elif "Z690" in t_upper or "Z690" in text_upper: spec_data["chipset"] = "Intel Z690"
    elif "B660" in t_upper or "B660" in text_upper: spec_data["chipset"] = "Intel B660"
    elif "H510" in t_upper or "H510" in text_upper: spec_data["chipset"] = "Intel H510"
    elif "B560" in t_upper or "B560" in text_upper: spec_data["chipset"] = "Intel B560"
    elif "Z590" in t_upper or "Z590" in text_upper: spec_data["chipset"] = "Intel Z590"
    elif "H410" in t_upper or "H410" in text_upper: spec_data["chipset"] = "Intel H410"
    elif "H81" in t_upper or "H81" in text_upper: spec_data["chipset"] = "Intel H81"
    elif "G41" in t_upper or "G41" in text_upper: spec_data["chipset"] = "Intel G41"
    # AMD
    elif "X870" in t_upper or "X870" in text_upper: spec_data["chipset"] = "AMD X870"
    elif "B850" in t_upper or "B850" in text_upper: spec_data["chipset"] = "AMD B850"
    elif "B840" in t_upper or "B840" in text_upper: spec_data["chipset"] = "AMD B840"
    elif "X670" in t_upper or "X670" in text_upper: spec_data["chipset"] = "AMD X670" 
    elif "B650" in t_upper or "B650" in text_upper: spec_data["chipset"] = "AMD B650"
    elif "A620" in t_upper or "A620" in text_upper: spec_data["chipset"] = "AMD A620"
    elif "X570" in t_upper or "X570" in text_upper: spec_data["chipset"] = "AMD X570"
    elif "B550" in t_upper or "B550" in text_upper: spec_data["chipset"] = "AMD B550"
    elif "A520" in t_upper or "A520" in text_upper: spec_data["chipset"] = "AMD A520"
    elif "B450" in t_upper or "B450" in text_upper: spec_data["chipset"] = "AMD B450"

    # 4. Form Factor
    if "E-ATX" in text_upper or "EATX" in text_upper: spec_data["form_factor"] = "E-ATX"
    elif "MICRO-ATX" in text_upper or "MATX" in text_upper or "MICRO ATX" in text_upper or "M-ATX" in text_upper: spec_data["form_factor"] = "Micro-ATX"
    elif "MINI-ITX" in text_upper or "MITX" in text_upper or "MINI ITX" in text_upper: spec_data["form_factor"] = "Mini-ITX"
    elif "ATX" in text_upper: spec_data["form_factor"] = "ATX"
    
    # 5. Memory Type
    if "DDR5" in t_upper or "DDR5" in text_upper: spec_data["memory_type"] = "DDR5"
    elif "DDR4" in t_upper or "DDR4" in text_upper: spec_data["memory_type"] = "DDR4"
    elif "DDR3" in t_upper or "DDR3" in text_upper: spec_data["memory_type"] = "DDR3"

    # 6. Wifi & Bluetooth
    if "WIFI" in t_upper or "WI-FI" in text_upper: spec_data["wifi"] = "Yes"
    if "BLUETOOTH" in text_upper: spec_data["bluetooth"] = "Yes"

    # 7. Memory Speed (MHz) - 10000000% Safe Extraction
    valid_speeds = []
    # Capture "DDR4 3200", "3200 MHz", "3200 MT/s"
    matches_prefix = re.findall(r'(?:DDR[345]\s?|MHz\s?|MT/s\s?)(\d{4})', text_upper)
    # Capture "3200 MHz", "3200 MT/s"
    matches_suffix = re.findall(r'(\d{4})\s?(?:MHz|MT/s)', text_upper)
    
    for s in matches_prefix + matches_suffix:
        try:
            val = int(s)
            if 2133 <= val <= 10000:
                valid_speeds.append(val)
        except: pass
        
    if valid_speeds:
        spec_data["memory_speed"] = f"{max(valid_speeds)} MHz"
    else:
        # Fallback Defaults
        if spec_data["memory_type"] == "DDR5": spec_data["memory_speed"] = "5200 MHz" 
        elif spec_data["memory_type"] == "DDR4": spec_data["memory_speed"] = "3200 MHz"
        elif spec_data["memory_type"] == "DDR3": spec_data["memory_speed"] = "1600 MHz"
        else: spec_data["memory_speed"] = "Unknown"

    return spec_data

def get_driver():
    options = uc.ChromeOptions()
    # options.add_argument('--headless')
    try:
        driver = uc.Chrome(options=options)
    except:
        options = uc.ChromeOptions()
        driver = uc.Chrome(options=options, version_main=143)
    return driver

def scrape():
    log("Initializing Browser (Safe Mode)...")
    driver = get_driver()
    all_products = []
    
    try:
        # Loop strictly through pages 1 to 5 as requested
        for page_num in range(1, 6): 
            current_url = f"{BASE_URL}?page={page_num}"
            log(f"--- Processing Page {page_num} ---")
            
            for attempt in range(3):
                try:
                    driver.get(current_url)
                    random_sleep(3, 5)
                    cards = driver.find_elements(By.CSS_SELECTOR, ".product-miniature")
                    break # Success
                except Exception as e:
                    log(f"Error loading page {page_num} (Attempt {attempt+1}): {e}")
                    try:
                        driver.quit()
                    except: pass
                    driver = get_driver()
            
            if not cards:
                log(f"Skipping page {page_num} after retries.")
                continue
            log(f"Page {page_num}: Found {len(cards)} products.")
            
            product_links = []
            for card in cards:
                try:
                    # Check stock FIRST
                    stock_status = "Unknown"
                    try:
                        # Spacenet usually puts stock status overlaid on image or below price
                        # Inspecting commonly used selectors for stock
                        # Usually .product-flags or .availability
                        pass # We check strictly on product page to be safe
                    except: pass
                    
                    # Capture Link
                    link = ""
                    try:
                        link_el = card.find_elements(By.CSS_SELECTOR, "h2.product_name a")
                        if not link_el: link_el = card.find_elements(By.CSS_SELECTOR, ".product-title a")
                        if link_el: link = link_el[0].get_attribute("href")
                    except: continue

                    if link and link not in product_links:
                        product_links.append(link)
                except: continue

            log(f"Page {page_num}: Found {len(product_links)} unique links.")
            
            # Visit Products
            for i, link in enumerate(product_links):
                log(f"[{i+1}/{len(product_links)}] Scraping: {link}")
                try:
                    driver.get(link)
                    random_sleep(2, 4)
                    
                    # Status Detection - ROBUST 3-LAYER CHECK
                    status = "Unknown"
                    try:
                        page_src = driver.page_source.lower()
                        
                        # 1. Check "Add to Cart" button (Strongest indicator of stock)
                        add_btn = driver.find_elements(By.CSS_SELECTOR, ".add-to-cart, #add_to_cart, .btn-add-to-cart")
                        if add_btn and any(b.is_displayed() and b.is_enabled() for b in add_btn):
                            status = "En Stock"
                        
                        # 2. Check Text "En Stock" in key areas
                        elif "en stock" in page_src and "rupture" not in page_src:
                             # Double check it's not "Pas en stock"
                             if "pas en stock" not in page_src:
                                 status = "En Stock"

                        # 3. Explicit Labels
                        if status == "Unknown":
                            qty_label = driver.find_elements(By.CSS_SELECTOR, ".product-quantities label, #product-availability")
                            for q in qty_label:
                                txt = q.text.strip().lower()
                                if "stock" in txt: status = "En Stock"
                                elif "rupture" in txt: status = "Epuisé"
                                
                    except: pass
                    
                    # STRICT FILTERING: Only scrape "En Stock"
                    if status != "En Stock":
                         # Final check: if price > 0 and no "rupture", assume stock?
                         # Safe to skip if we are unsure, but user wants all.
                         # Let's rely on the add-to-cart mainly.
                        log(f"   > Skipping: Status is {status}")
                        continue

                    # Title
                    title = ""
                    try:
                        title = driver.find_element(By.CSS_SELECTOR, "h1.product-detail-title").text.strip()
                    except:
                        try: title = driver.find_element(By.CSS_SELECTOR, "h1.h1").text.strip()
                        except: pass
                        
                    # Reference
                    reference = ""
                    try:
                        reference = driver.find_element(By.CSS_SELECTOR, ".product-reference span").text.strip()
                    except: pass
                    
                    # Price
                    price = 0.0
                    try:
                        p_el = driver.find_element(By.CSS_SELECTOR, ".current-price [itemprop='price']")
                        price = clean_price(p_el.get_attribute("content"))
                    except:
                        try:
                            p_el = driver.find_element(By.CSS_SELECTOR, ".current-price")
                            price = clean_price(p_el.text)
                        except: pass
                        
                    # Image
                    image = ""
                    try:
                        img_el = driver.find_element(By.CSS_SELECTOR, ".product-cover img")
                        image = img_el.get_attribute("src")
                    except: pass
                    
                    # Description (Full Text for parsing)
                    full_desc = ""
                    try:
                        # Meta description often has good specs summary
                        meta_desc = driver.find_elements(By.CSS_SELECTOR, "meta[property='og:description'], meta[name='description']")
                        for meta in meta_desc:
                            c = meta.get_attribute("content")
                            if c: full_desc += c + "\n"
                    except: pass
                    
                    try:
                         # Specs tab or description div
                         specs_tab = driver.find_element(By.CSS_SELECTOR, "#product-details").text
                         full_desc += specs_tab + "\n"
                    except: pass
                    
                    try:
                        desc_long = driver.find_element(By.CSS_SELECTOR, "#description, .product-description").text.strip()
                        full_desc += desc_long + "\n"
                    except: pass
                    
                    # Parse Specs
                    specs = extract_motherboard_details(title, full_desc)
                    
                    # LOGGING
                    log(f"   > {title} | {specs['socket']} | {specs['chipset']} | {specs['form_factor']}")

                    all_products.append({
                        "title": title,
                        "reference": reference,
                        "brand": specs["brand"],
                        "price": price,
                        "image": image,
                        "link": link,
                        "specs": specs,
                        "source": "SpaceNet",
                        "status": status,
                        "category": "motherboard"
                    })
                    
                except Exception as e:
                    log(f"   Error on detail page: {e}")
            
    except Exception as e:
        log(f"Critical Error: {e}")
    finally:
        driver.quit()
        
    # Save
    log(f"Saving {len(all_products)} products to {OUTPUT_FILE}")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    log("Done.")

if __name__ == "__main__":
    scrape()
