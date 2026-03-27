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
BASE_URL = "https://www.mytek.tn/informatique/composants-informatique/barrettes-memoire.html"
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\mytek_rams.json"

def clean_price(price_str):
    if not price_str: return 0.0
    clean = price_str.upper().replace('TND', '').replace('DT', '').replace('\u00a0', '').strip()
    clean = clean.replace(',', '.') 
    clean = re.sub(r'[^\d.]', '', clean)
    try:
        return float(clean)
    except ValueError:
        return 0.0

def extract_ram_details(title, full_text=""):
    spec_data = {
        "category": "ram",
        "brand": "Unknown",
        "memory_capacity": "Unknown",
        "memory_type": "Unknown",
        "memory_speed": "Unknown",
        "form_factor": "DIMM",
        "rgb": "No"
    }
    
    t_upper = title.upper()
    text_upper = full_text.upper()
    
    # Brand detection
    brands = ["ADATA", "PNY", "CORSAIR", "G.SKILL", "KINGSTON", "CRUCIAL", "TEAMGROUP", "HYPERX", "LEXAR", "PATRIOT", "KLEVV", "APACER", "SILICON POWER", "GEIL"]
    for b in brands:
        if b in t_upper:
            spec_data["brand"] = b
            if b == "G.SKILL": spec_data["brand"] = "G.Skill"
            elif b == "TEAMGROUP": spec_data["brand"] = "TeamGroup"
            elif b == "CORSAIR": spec_data["brand"] = "Corsair"
            elif b == "KINGSTON": spec_data["brand"] = "Kingston"
            break

    # Form factor
    if "SO-DIMM" in text_upper or "SODIMM" in text_upper or "PC PORTABLE" in t_upper or "LAPTOP" in t_upper:
        spec_data["form_factor"] = "SO-DIMM"

    # Memory Type
    for t in ["DDR5", "DDR4", "DDR3L", "DDR3", "DDR2"]:
        if t in t_upper or t in text_upper:
            spec_data["memory_type"] = t
            break

    # Capacity
    cap_match = re.search(r'(\d+)\s*(?:GO|GB)', t_upper)
    if not cap_match:
        cap_match = re.search(r'(\d+)\s*(?:GO|GB)', text_upper)
        
    if cap_match:
        val = int(cap_match.group(1))
        # Handle kits (e.g., 2 x 8 Go)
        if "2X" in t_upper.replace(" ", "") or "2 X " in t_upper:
             # if title says "16 Go (2x 8Go)"
             spec_data["memory_capacity"] = f"{val}GB"
        else:
             spec_data["memory_capacity"] = f"{val}GB"

    # Speed
    speed_match = re.search(r'(\d{3,4})\s*MHZ', t_upper)
    if not speed_match:
        speed_match = re.search(r'(\d{3,4})\s*MHZ', text_upper)
        
    if speed_match:
        spec_data["memory_speed"] = f"{speed_match.group(1)} MHz"

    # RGB
    if "RGB" in t_upper or "ARGB" in t_upper:
        spec_data["rgb"] = "Yes"

    return spec_data

def scrape_selenium():
    print("Launching Selenium for MyTek RAMs...", flush=True)
    options = Options()
    options.add_argument("--headless=new") 
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled") 
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    
    all_products = []
    seen_links = set()
    
    try:
        page = 1
        max_pages = 20
        
        while page <= max_pages:
            url = f"{BASE_URL}?p={page}"
            print(f"Navigating to Page {page}: {url}", flush=True)
            driver.get(url)
            
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".product-container, .message.info.empty"))
                )
            except:
                print("Timeout waiting for content. Retrying once...", flush=True)
                driver.refresh()
                time.sleep(5)
            
            # Scroll trigger
            last_height = driver.execute_script("return document.body.scrollHeight")
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height: break
                last_height = new_height
            
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
                    
                    img_elem = item.select_one(".product-item-photo img")
                    if not img_elem: img_elem = item.select_one("img")
                    image = img_elem['src'] if img_elem else ""
                    
                    price_elem = item.select_one(".final-price")
                    if not price_elem: price_elem = item.select_one(".price")
                    if not price_elem: price_elem = item.select_one(".price-box .price")
                    price_text = price_elem.text.strip() if price_elem else "0"
                    price = clean_price(price_text)
                    
                    availability = "in-stock"
                    item_text = item.text.lower()
                    if "épuisé" in item_text or "hors stock" in item_text:
                        availability = "out-of-stock"
                        continue # Skip out of stock completely
                        
                    desc_elem = item.select_one(".product-item-description")
                    full_text = item.text.upper()
                    if desc_elem:
                        full_text += " " + desc_elem.text.upper()

                    spec_data = extract_ram_details(title, full_text)
                    
                    pid = f"mytek-ram-{len(seen_links) + 1}"
                    seen_links.add(link)
                    
                    p = {
                        "id": pid,
                        "title": title,
                        "price": price,
                        "image": image,
                        "brand": spec_data["brand"],
                        "category": "ram",
                        "source": "MyTek", 
                        "availability": availability,
                        "link": link,
                        "specs": spec_data
                    }
                    page_products.append(p)
                    
                except Exception as e:
                    print(f"Error parsing item: {e}")
                    continue
            
            print(f"   + Found {len(page_products)} in-stock products on page {page}", flush=True)
            all_products.extend(page_products)
            
            next_btn = soup.select_one(".pages-item-next")
            if not next_btn:
                 next_btn = soup.select_one("a[title='Suivant']")
            
            if not next_btn:
                print("No next button found. End of catalogue.", flush=True)
                break
                
            page += 1
            time.sleep(random.uniform(2, 4))
            
    except Exception as e:
        print(f"Critical Error during pagination: {e}", flush=True)

    # Note: Skipping phase 2 detailed crawl because MyTek RAM titles and brief descriptions usually contain all info
    # (Speed, Type, Capacity, Form factor), keeping it fast and efficient!

    driver.quit()
        
    print(f"Total extracted: {len(all_products)}", flush=True)
    
    if all_products:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        print(f"Saved to {OUTPUT_FILE}", flush=True)
    else:
        print("No products extracted. Nothing saved.", flush=True)

if __name__ == "__main__":
    scrape_selenium()
