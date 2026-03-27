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
BASE_URL = "https://spacenet.tn/20-processeur"
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\spacenet_full_dump.json"

def log(msg):
    print(msg, flush=True)

def random_sleep(min_s=3, max_s=6):
    time.sleep(random.uniform(min_s, max_s))

# --- PARSING HELPERS ---
def parse_specs_text(full_text):
    specs = {
        "frequency": "Unknown",
        "cores": "Unknown",
        "threads": "Unknown",
        "cache": "Unknown",
        "socket": "Unknown",
        "memory_type": "Unknown"
    }
    if not full_text: return specs
    text = full_text.replace("\xa0", " ").strip()

    # Frequency
    freq_match = re.search(r'(?:Fréquence|Vitesse).*?[:]\s*([\d.,]+\s*(?:GHz|MHz))', text, re.IGNORECASE)
    if freq_match: specs["frequency"] = freq_match.group(1).strip()
    else:
        freq_match = re.search(r'(\d+[.,]\d+\s*GHz)', text, re.IGNORECASE)
        if freq_match: specs["frequency"] = freq_match.group(1).strip()

    # Cores
    cores_match = re.search(r'(\d+)\s*C[oe]urs?', text, re.IGNORECASE)
    if cores_match: specs["cores"] = f"{cores_match.group(1)} Cores"

    # Threads
    threads_match = re.search(r'(\d+)\s*Threads?', text, re.IGNORECASE)
    if threads_match: specs["threads"] = f"{threads_match.group(1)} Threads"

    # Cache
    cache_match = re.search(r'(\d+\s*(?:Mo|MB))\s*(?:Intel|Smart)?\s*Cache', text, re.IGNORECASE)
    if not cache_match:
        cache_match = re.search(r'Mémoire Cache\s*[:]\s*(\d+\s*(?:Mo|MB))', text, re.IGNORECASE)
    if cache_match: specs["cache"] = cache_match.group(1).strip()

    # Socket
    socket_match = re.search(r'Socket\s*[:]\s*([A-Za-z0-9]+)', text, re.IGNORECASE)
    if socket_match: specs["socket"] = socket_match.group(1).strip()

    # Memory
    mem_match = re.search(r'DDR\d', text, re.IGNORECASE)
    if mem_match: specs["memory_type"] = mem_match.group(0).upper()

    return specs

def clean_price(price_str):
    if not price_str: return 0.0
    clean = re.sub(r'[^\d,]', '', price_str).replace(',', '.')
    try: return float(clean)
    except: return 0.0

def scrape():
    log("Initializing Browser (Safe Mode - Full Scan Enhanced)...")
    options = uc.ChromeOptions()
    # options.add_argument('--headless') 
    driver = uc.Chrome(options=options, version_main=143)
    
    all_products = []
    
    try:
        # Loop strictly through pages
        for page_num in range(1, 10): 
            current_url = f"{BASE_URL}?page={page_num}"
            log(f"--- Processing Page {page_num} ---")
            # Retry logic for page navigation
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    driver.get(current_url)
                    random_sleep(4, 7)
                    if "404" in driver.title:
                        log("Page 404 - Reached end.")
                        break
                    cards = driver.find_elements(By.CSS_SELECTOR, ".product-miniature")
                    if cards:
                        break # Success
                    else:
                        log(f"No products found (Attempt {attempt+1}/{max_retries})")
                        if attempt == max_retries - 1:
                            log("Final attempt failed - Stopping.")
                except Exception as e:
                    log(f"Navigation Error (Attempt {attempt+1}): {e}")
                    if attempt == max_retries - 1: break
                    time.sleep(5)
            
            if not cards and "404" in driver.title: break
            if not cards: break
            
            log(f"Page {page_num}: Found {len(cards)} products.")
            
            product_links = []
            
            for card in cards:
                try:
                    # Capture Link
                    link = ""
                    try:
                        link_el = card.find_elements(By.CSS_SELECTOR, "h2.product_name a")
                        if not link_el: link_el = card.find_elements(By.CSS_SELECTOR, ".product_name a")
                        if not link_el: link_el = card.find_elements(By.CSS_SELECTOR, ".product-title a")
                        if link_el: link = link_el[0].get_attribute("href")
                        else: continue
                    except: continue

                    if link not in product_links:
                        product_links.append(link)
                    
                except Exception: continue

            log(f"Page {page_num}: Found {len(product_links)} items to process (All Statuses).")
            if not product_links:
                continue

            # Visit Products
            for i, link in enumerate(product_links):
                log(f"[{i+1}/{len(product_links)}] Scraping: {link}")
                try:
                    driver.get(link)
                    random_sleep(3, 5)
                    
                    # Status Detection
                    status = "En Stock" # Default fallback
                    try:
                        # Priority check for availability label
                        avail_labels = driver.find_elements(By.CSS_SELECTOR, "#product-availability")
                        if avail_labels:
                            txt = avail_labels[0].text.strip()
                            if "stock" in txt.lower(): status = "En Stock"
                            elif "rupture" in txt.lower() or "épui" in txt.lower(): status = "Epuisé"
                            elif "commande" in txt.lower(): status = "Sur Commande"
                            elif "arrivage" in txt.lower(): status = "Arrivage"
                    except: pass
                    
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
                    
                    # Brand
                    brand = "Unknown"
                    t_lower = title.lower()
                    if "intel" in t_lower: brand = "Intel"
                    elif "amd" in t_lower or "ryzen" in t_lower: brand = "AMD"
                    
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
                    
                    # Description
                    full_desc = ""
                    try:
                        meta_desc = driver.find_elements(By.CSS_SELECTOR, "meta[property='og:description'], meta[name='description']")
                        for meta in meta_desc:
                            c = meta.get_attribute("content")
                            if c: full_desc += c + "\n"
                    except: pass
                    
                    try:
                        desc_short = driver.find_element(By.CSS_SELECTOR, "#product-description-short-content, .product-description-short").text.strip()
                        full_desc += desc_short + "\n"
                    except: pass
                    
                    try:
                        desc_long = driver.find_element(By.CSS_SELECTOR, "#description, .product-description").text.strip()
                        full_desc += desc_long + "\n"
                    except: pass
                    
                    # Parse Specs
                    specs = parse_specs_text(full_desc)
                    log(f"   > Status: {status} | Desc Len: {len(full_desc)} | Cores: {specs.get('cores')} | Freq: {specs.get('frequency')}")

                    all_products.append({
                        "title": title,
                        "reference": reference,
                        "brand": brand,
                        "price": price,
                        "image": image,
                        "link": link,
                        "specs": specs,
                        "source": "SpaceNet",
                        "status": status
                    })
                    
                except Exception as e:
                    log(f"   Error on detail page: {e}")
            
        # Save
        log(f"Saving {len(all_products)} products to {OUTPUT_FILE}")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        log("Done.")
        
    except Exception as e:
        log(f"Critical Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape()
