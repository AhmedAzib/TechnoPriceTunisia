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
import sys

# Configuration
URLS_TO_SCRAPE = [
    "https://www.mytek.tn/smartphone.html",
    "https://www.mytek.tn/telephonie-tunisie/smartphone-mobile-tunisie/iphone.html"
]
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"

def clean_price(price_str):
    if not price_str:
        return 0.0
    clean = price_str.replace('TND', '').replace('DT', '').replace(',', '.').replace('\u00a0', '').strip()
    clean = re.sub(r'[^\d.]', '', clean)
    try:
        return float(clean)
    except ValueError:
        return 0.0

def extract_specs(title):
    spec_data = {
        "screen": "Unknown",
        "storage": "Unknown",
        "ram": "Unknown",
        "camera": "Unknown",
        "battery": "Unknown",
        "os": "Android"
    }
    
    title_upper = title.upper()
    
    # Simple Spec Logic
    brands = ["SAMSUNG", "APPLE", "XIAOMI", "REDMI", "INFINIX", "TECNO", "OPPO", "REALME", "VIVO", "HONOR", "HUAWEI", "NOKIA", "ITEL", "LESIA", "OSCAL"]
    brand = "Unknown"
    for b in brands:
         if b in title_upper:
             brand = b.title()
             if brand == "Apple": spec_data["os"] = "iOS"
             break
    
    # Storage/RAM Heuristic
    caps = re.findall(r'(\d+)\s*(?:GO|GB|TO|TB)', title_upper)
    numeric_caps = sorted([int(c) for c in caps], reverse=True)
    
    if len(numeric_caps) >= 1:
        spec_data["storage"] = f"{numeric_caps[0]}GB"
        if len(numeric_caps) >= 2:
             spec_data["ram"] = f"{numeric_caps[1]}GB"
             
    return spec_data, brand

def scrape_selenium():
    print("Launching Selenium...", flush=True)
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    
    all_products = []
    seen_links = set()
    
    try:
        for base_url in URLS_TO_SCRAPE:
            print(f"--- Scraping URL: {base_url} ---", flush=True)
            page = 1
            max_pages = 50
            
            while page <= max_pages:
                url = f"{base_url}?p={page}"
                print(f"Navigating to Page {page}...", flush=True)
                driver.get(url)
                
                # Wait for products or empty message
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".product-container, .message.info.empty"))
                    )
                except:
                    print("Timeout waiting for products. Maybe end of list?", flush=True)
                    break
                    
                # Scroll down
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(2)
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                items = soup.select(".product-container")
                
                if not items:
                    print(f"No items found on page {page}. Stopping this URL.", flush=True)
                    break
                    
                page_products = []
                for item in items:
                    try:
                        link_elem = item.select_one(".product-item-link")
                        if not link_elem: continue
                        
                        title = link_elem.text.strip()
                        link = link_elem['href']
                        
                        if link in seen_links:
                             continue
                        
                        img_elem = item.select_one(".product-item-photo img")
                        if not img_elem: img_elem = item.select_one("img")
                        image = img_elem['src'] if img_elem else ""
                        
                        price_elem = item.select_one(".final-price")
                        if not price_elem: price_elem = item.select_one(".price")
                        if not price_elem: price_elem = item.select_one(".price-box .price")
                             
                        price_text = price_elem.text.strip() if price_elem else "0"
                        price = clean_price(price_text)
                        
                        availability = "in-stock"
                        if "épuisé" in item.text.lower() or "hors stock" in item.text.lower():
                             availability = "out-of-stock"
                            
                        specs, brand = extract_specs(title)
                        
                        # ID Generation using seen_links count to be stableish
                        pid = f"mytek-mob-{len(seen_links) + 1}"
                        
                        seen_links.add(link)
                        
                        p = {
                            "id": pid,
                            "title": title,
                            "price": price,
                            "image": image,
                            "brand": brand,
                            "source": "MyTek",
                            "availability": availability,
                            "link": link,
                            "specs": specs
                        }
                        page_products.append(p)
                    except Exception as e:
                        continue
                
                print(f"   + Found {len(page_products)} NEW products on page {page}", flush=True)
                all_products.extend(page_products)
                
                # Check Next Button
                next_btn = soup.select_one("a[aria-label='Next']")
                if not next_btn: next_btn = soup.select_one(".next")
                
                if not next_btn:
                    print("No next button. End of catalogue section.", flush=True)
                    break
                    
                page += 1
                
    except Exception as e:
        print(f"Critical Selenium Error: {e}", flush=True)
    finally:
        driver.quit()
        
    print(f"Total extracted: {len(all_products)}", flush=True)
    
    if all_products:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        print(f"Saved to {OUTPUT_FILE}", flush=True)
    else:
        print("No products extracted. Nothing saved.", flush=True)

if __name__ == "__main__":
    scrape_selenium()
