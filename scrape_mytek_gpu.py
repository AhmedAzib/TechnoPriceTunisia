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
BASE_URL = "https://www.mytek.tn/informatique/composants-informatique/carte-graphique.html"
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\mytek_gpu.json"

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

def extract_gpu_details(title, full_text=""):
    spec_data = {
        "category": "gpu",
        "gpu": "Unknown",
        "brand": "Unknown",
        "memory": "Unknown"
    }
    
    t_upper = title.upper()
    text_upper = full_text.upper()
    
    # 1. Detect Brand (Manufacturer)
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
        
    # 2. Extract GPU Chipset
    # NVIDIA
    if "RTX 4090" in t_upper: spec_data["gpu"] = "RTX 4090"
    elif "RTX 4080" in t_upper: spec_data["gpu"] = "RTX 4080"
    elif "RTX 4070" in t_upper: 
        spec_data["gpu"] = "RTX 4070 Ti" if "TI" in t_upper else "RTX 4070"
    elif "RTX 4060" in t_upper: 
        spec_data["gpu"] = "RTX 4060 Ti" if "TI" in t_upper else "RTX 4060"
    elif "RTX 3090" in t_upper: spec_data["gpu"] = "RTX 3090"
    elif "RTX 3080" in t_upper: spec_data["gpu"] = "RTX 3080"
    elif "RTX 3070" in t_upper: spec_data["gpu"] = "RTX 3070"
    elif "RTX 3060" in t_upper: 
        spec_data["gpu"] = "RTX 3060 Ti" if "TI" in t_upper else "RTX 3060"
    elif "RTX 3050" in t_upper: spec_data["gpu"] = "RTX 3050"
    elif "RTX 2060" in t_upper: spec_data["gpu"] = "RTX 2060"
    elif "GTX 1660" in t_upper: spec_data["gpu"] = "GTX 1660"
    elif "GTX 1650" in t_upper: spec_data["gpu"] = "GTX 1650"
    elif "GTX 1630" in t_upper: spec_data["gpu"] = "GTX 1630"
    elif "GT 1030" in t_upper: spec_data["gpu"] = "GT 1030"
    elif "GT 730" in t_upper: spec_data["gpu"] = "GT 730"
    elif "GT 710" in t_upper: spec_data["gpu"] = "GT 710"
    
    # AMD
    elif "RX 7900" in t_upper: spec_data["gpu"] = "RX 7900"
    elif "RX 7800" in t_upper: spec_data["gpu"] = "RX 7800"
    elif "RX 7700" in t_upper: spec_data["gpu"] = "RX 7700"
    elif "RX 7600" in t_upper: spec_data["gpu"] = "RX 7600"
    elif "RX 6900" in t_upper: spec_data["gpu"] = "RX 6900"
    elif "RX 6800" in t_upper: spec_data["gpu"] = "RX 6800"
    elif "RX 6700" in t_upper: spec_data["gpu"] = "RX 6700"
    elif "RX 6600" in t_upper: spec_data["gpu"] = "RX 6600"
    elif "RX 6500" in t_upper: spec_data["gpu"] = "RX 6500"
    elif "RX 6400" in t_upper: spec_data["gpu"] = "RX 6400"
    elif "RX 580" in t_upper: spec_data["gpu"] = "RX 580"
    elif "RX 570" in t_upper: spec_data["gpu"] = "RX 570"
    elif "RX 550" in t_upper: spec_data["gpu"] = "RX 550"
    
    # 3. Extract Memory Size
    # Look for "24GB", "16 Go", etc.
    mem_match = re.search(r'(\d+)\s?(G|GO|GB)', t_upper)
    if mem_match:
         spec_data["memory"] = f"{mem_match.group(1)}GB"
            
    # 4. Extract Memory Speed (Gbps)
    # Patterns: "Horloge mémoire: 14 Gbit/s", "Vitesse de la mémoire: 2.1 Gbps", "19 Gbps", "21 Gbit/s"
    # Search in full_text_upper
    
    speed_match = re.search(r'(?:HORLOGE|VITESSE|SPEED).{0,20}?(?:MÉMOIRE|MEMORY).{0,10}?[:\-]?\s*(\d+(?:[.,]\d+)?)\s*(?:GBIT\/S|GBPS)', text_upper)
    if not speed_match:
        # Try finding just "X Gbps" near "Mémoire" if the first strict pattern fails
        speed_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:GBIT\/S|GBPS)', text_upper)

    if speed_match:
        val = speed_match.group(1).replace(',', '.')
        spec_data["memory_speed"] = f"{val} Gbit/s"

    return spec_data

def scrape_selenium():
    print("Launching Selenium for MyTek Graphics Cards (Deep Scrape)...", flush=True)
    options = Options()
    options.add_argument("--headless=new") 
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled") 
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    
    all_products = []
    product_data_list = [] # Store dicts with link, image, title from listing
    
    try:
        # Phase 1: Collect Links & Basic Info (Safe Source)
        page = 1
        max_pages = 5 
        
        while page <= max_pages:
            url = f"{BASE_URL}?p={page}"
            print(f"Collecting Data from Page {page}: {url}", flush=True)
            driver.get(url)
            
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".product-container, .message.info.empty"))
                )
            except:
                print("Timeout waiting for content.", flush=True)
                break
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            items = soup.select(".product-container")
            
            if not items:
                print(f"No items found on page {page}.", flush=True)
                break
                
            for item in items:
                try:
                    # Stock Check
                    is_exhausted = "épuisé" in item.text.lower() or "hors stock" in item.text.lower()
                    if is_exhausted: continue 
                        
                    link_elem = item.select_one(".product-item-link")
                    if not link_elem: continue
                    
                    prod_link = link_elem['href']
                    prod_title = link_elem.text.strip()
                    
                    # Capture Image SAFELY from Listing (Works 100%)
                    img_elem = item.select_one(".product-item-photo img")
                    if not img_elem: img_elem = item.select_one("img")
                    prod_image = img_elem['src'] if img_elem else ""

                    product_data_list.append({
                        'link': prod_link,
                        'title': prod_title,
                        'image': prod_image
                    })
                except:
                    continue
            
            # Check Next
            next_btn = soup.select_one(".pages-item-next")
            if not next_btn: next_btn = soup.select_one("a[title='Suivant']")
            if not next_btn: break
                
            page += 1
            time.sleep(1)

        print(f"Found {len(product_data_list)} products. Starting Deep Scrape for Specs...", flush=True)
        
        # Phase 2: Visit Each Product for Specs ONLY (Preserving Image)
        count = 0
        for p_data in product_data_list:
            count += 1
            link = p_data['link']
            print(f"[{count}/{len(product_data_list)}] Scraping {link}...", flush=True)
            
            try:
                driver.get(link)
                # Wait for specs
                try:
                    WebDriverWait(driver, 8).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".product.attribute.description, .additional-attributes-wrapper"))
                    )
                except:
                    pass
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Basic Info Refinement
                title_elem = soup.select_one(".page-title .base")
                final_title = title_elem.text.strip() if title_elem else p_data['title']
                
                # Improved Price Extraction with Fallbacks
                price = 0.0
                
                # 1. Try Meta Tag (Most Reliable if present)
                price_meta = soup.select_one('meta[property="product:price:amount"]')
                if price_meta and price_meta.get('content'):
                    try:
                        price = float(price_meta['content'])
                    except:
                        pass
                
                # 2. Try Standard Display Price (if meta failed or 0)
                if price == 0.0:
                    price_elem = soup.select_one(".product-info-price .price")
                    if not price_elem:
                        price_elem = soup.select_one(".price-final_price .price")
                    if not price_elem:
                        price_elem = soup.select_one(".price-box .price")
                    
                    if price_elem:
                        price = clean_price(price_elem.text)
                
                # 3. Last Resort (Old Price or Special Price structures)
                if price == 0.0:
                    special_price = soup.select_one(".special-price .price")
                    if special_price:
                        price = clean_price(special_price.text)
                    else:
                        op = soup.select_one(".regular-price .price") # Fallback to regular if no special
                        if op: price = clean_price(op.text)

                if price == 0.0:
                    print(f"WARNING: Zero price for {link}", flush=True)
                
                # USE SAFE IMAGE FROM LISTING
                image = p_data['image'] 
                if not image: # Fallback only if missing
                    img_elem = soup.select_one(".gallery-placeholder img")
                    if img_elem: image = img_elem['src']

                # Extract Full Description / Specs
                full_text = ""
                
                # 0. Meta Description (Capture ALL sources to find hidden specs)
                for meta_selector in ['meta[name="description"]', 'meta[property="og:description"]']:
                    meta_tag = soup.select_one(meta_selector)
                    if meta_tag and meta_tag.get('content'):
                        full_text += meta_tag['content'] + " "

                desc_div = soup.select_one(".product.attribute.description")
                if desc_div: full_text += desc_div.get_text(" ", strip=True) + " "
                
                # Table Specs
                specs_text = ""
                rows = soup.select(".additional-attributes-wrapper tr")
                for row in rows:
                    th = row.select_one("th")
                    td = row.select_one("td")
                    if th and td:
                        key = th.text.strip()
                        val = td.text.strip()
                        specs_text += f"{key}: {val} "
                
                full_text += specs_text
                full_text_upper = full_text.upper()

                # Extract CUDA Cores Specifically
                # Pattern 1: NOYAUX CUDA: 3840
                cuda_match = re.search(r'NOYAUX\s+CUDA\s*[:\-]?\s*(\d+)', full_text_upper)
                
                # Pattern 2: 3840 CUDA Cores (English)
                if not cuda_match:
                    cuda_match = re.search(r'(\d+)\s+CUDA\s+CORES', full_text_upper)
                
                cuda_cores = "Unknown"
                if cuda_match:
                    cuda_cores = f"{cuda_match.group(1)} Units"
                
                # Helper for standard specs
                spec_data = extract_gpu_details(final_title, full_text_upper)
                if cuda_cores != "Unknown":
                    spec_data["noyaux_cuda"] = cuda_cores # Add to specs

                # Extract Memory Bus (Bus Mémoire)
                # Pattern: "Bus Mémoire: 192 bits", "Interface Mémoire: 128 bits", "128-bit"
                bus_match = re.search(r'(?:BUS|INTERFACE)\s+(?:MÉMOIRE|MEMORY).{0,10}?[:\-]?\s*(\d+)\s*(?:BITS?)', full_text_upper)
                if not bus_match:
                    bus_match = re.search(r'(\d+)\s*BITS?', full_text_upper)
                
                if bus_match:
                    spec_data["memory_bus"] = f"{bus_match.group(1)} bits"

                # Extract Boost Clock (Boost)
                # Pattern: "Boost: 2692 MHz", "Boost: 2 602 MHz"
                boost_match = re.search(r'BOOST\s*[:\-]?\s*(\d+(?:\s*\d+)?)\s*MHZ', full_text_upper)
                if boost_match:
                    # Remove spaces in number (e.g. "2 602" -> "2602")
                    val = boost_match.group(1).replace(' ', '')
                    spec_data["boost_clock"] = f"{val} MHz"

                # Extract Memory Type (Type Mémoire)
                # Pattern: "Type de mémoire: GDDR6", "Type Mémoire: GDDR7"
                mem_type_match = re.search(r'(?:TYPE\s+(?:DE\s+)?MÉMOIRE|MEMORY\s+TYPE)\s*[:\-]?\s*([A-Z0-9]+)', full_text_upper)
                if mem_type_match:
                     spec_data["memory_type"] = mem_type_match.group(1)

                # Extract Extreme Performance (Performances extrêmes)
                # Pattern: "Performances extrêmes: 2 557 MHz", "Extreme Performance: 2600 MHz"
                extreme_match = re.search(r'(?:PERFORMANCES?\s+EXTRÊMES?|EXTREME\s+PERFORMANCES?)\s*[:\-]?\s*(\d+(?:\s*\d+)?)\s*MHZ', full_text_upper)
                if extreme_match:
                     val = extreme_match.group(1).replace(' ', '')
                     spec_data["extreme_performance"] = f"{val} MHz"
                
                pid = f"mytek-gpu-{count}"
                
                p = {
                    "id": pid,
                    "title": final_title,
                    "price": price,
                    "image": image,
                    "brand": spec_data["brand"],
                    "category": "gpu",
                    "source": "MyTek",
                    "availability": "in-stock",
                    "link": link,
                    "specs": spec_data,
                    "description": full_text
                }
                all_products.append(p)
                time.sleep(1) 
                
            except Exception as e:
                print(f"Error scraping product {link}: {e}", flush=True)
                continue

    except Exception as e:
        print(f"Critical Error: {e}", flush=True)

    driver.quit()
        
    print(f"Total extracted: {len(all_products)}", flush=True)
    
    if all_products:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        print(f"Saved to {OUTPUT_FILE}", flush=True)
    else:
        print("No products extracted.", flush=True)

if __name__ == "__main__":
    scrape_selenium()
