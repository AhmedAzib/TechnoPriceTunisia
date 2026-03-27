from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time
import re

# Configuration
URL = "https://megapc.tn/shop/COMPOSANTS/PROCESSEUR"
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\megapc_processors.json"

import shutil
import os

def backup_data():
    if os.path.exists(OUTPUT_FILE):
        backup_path = OUTPUT_FILE.replace(".json", "_backup.json")
        try:
            shutil.copy2(OUTPUT_FILE, backup_path)
            print(f"Safety First: Backed up existing data to {backup_path}")
        except Exception as e:
            print(f"Warning: Could not backup file: {e}")


def clean_price(price_str):
    try:
        # Remove "DT", "TND", spaces
        cleaned = price_str.upper().replace("DT", "").replace("TND", "").strip()
        # "219 DT" -> "219"
        # Handle "1 299" -> "1299"
        cleaned = "".join(c for c in cleaned if c.isdigit() or c == ".")
        return float(cleaned)
    except:
        return 0.0

def scrape_megapc():
    backup_data() # SAFETY: Backup before doing anything
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") # Use legacy headless for stability if new one fails
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage") # Critical for some environments
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    results = []
    
    try:
        print(f"Navigating to {URL}...")
        driver.get(URL)
        
        raw_items = []
        
        # We'll try to find how many pages there are by looking at the highest data-page attribute
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-page]")))
            page_buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-page]")
            max_page = 0
            for btn in page_buttons:
                try:
                    p_val = int(btn.get_attribute("data-page"))
                    if p_val > max_page: max_page = p_val
                except: pass
            num_pages = max_page + 1
            print(f"Detected {num_pages} pages.")
        except:
            print("Could not detect page buttons, assuming 1 page.")
            num_pages = 1

        for p_idx in range(num_pages):
            print(f"Scraping Page {p_idx + 1}...")
            
            if p_idx > 0:
                try:
                    # Find the button for this specific page
                    btn = driver.find_element(By.CSS_SELECTOR, f"button[data-page='{p_idx}']")
                    # Scroll to it
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    time.sleep(1)
                    # Click via JS for stability
                    driver.execute_script("arguments[0].click();", btn)
                    print(f"Switched to Page {p_idx + 1}")
                    time.sleep(3) # Wait for content update
                except Exception as e:
                    print(f"Error navigating to page {p_idx + 1}: {e}")
                    break

            # Parse Page with BS4
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            products = soup.select("article.product-card")
            print(f"Found {len(products)} products on this page.")
            
            for p in products:
                try:
                    # Stock Check
                    txt = p.get_text().upper()
                    if "RUPTURE" in txt or "EPUISE" in txt:
                        continue
                    
                    title = p.get("title")
                    if not title:
                        title_tag = p.select_one("a p")
                        if title_tag: title = title_tag.get_text(strip=True)
                    
                    if not title: continue
                    
                    link_tag = p.select_one("a")
                    link = ""
                    if link_tag and link_tag.get("href"):
                        link = link_tag.get("href")
                        if link.startswith("/"): link = "https://megapc.tn" + link
                    
                    # Image Extraction - Ultra Robust
                    image = ""
                    
                    # DEBUG: Specific check for the problematic item
                    is_debug_item = "10105F" in title
                    if is_debug_item:
                        print(f"DEBUG: Inspecting {title}...")
                    
                    # Strategy: Gather ALL potential image URLs from the card
                    img_candidates = []
                    
                    # 1. Look for img tags
                    all_imgs = p.find_all("img")
                    for img in all_imgs:
                        # Gather all possible sources
                        srcs = [
                            img.get("data-src"),
                            img.get("src"),
                            img.get("data-lazy-src"),
                            img.get("srcset") # Sometimes first item in srcset
                        ]
                        
                        for s in srcs:
                            if s:
                                s = s.strip()
                                # specific cleanup for srcset
                                if " " in s: s = s.split(" ")[0] 
                                if len(s) > 5:
                                    img_candidates.append(s)

                    if is_debug_item:
                         print(f"DEBUG source candidates: {img_candidates}")

                    # 2. Filter candidates
                    valid_candidates = []
                    for c in img_candidates:
                        lower_c = c.lower()
                        
                        # Exclude obvious noise
                        if "base64" in lower_c: continue
                        if "placeholder" in lower_c: continue
                        if "blank" in lower_c: continue
                        if "assets/img" in lower_c: continue # Site assets
                        if "logo" in lower_c: continue
                        if "icon" in lower_c: continue
                        if "rating" in lower_c: continue
                        if "stars" in lower_c: continue
                        
                        # Fix URL
                        full_url = c
                        if c.startswith("//"): full_url = "https:" + c
                        elif c.startswith("/"): full_url = "https://megapc.tn" + c
                        elif not c.startswith("http"):
                             # If it's just a filename? Unlikely but possible
                             if "gi-ga" in c: full_url = "https://static.gi-ga.tech/" + c.lstrip("/")
                             else: continue # Skip unknown relative paths
                        
                        valid_candidates.append(full_url)
                        
                    if is_debug_item:
                        print(f"DEBUG valid candidates: {valid_candidates}")

                    # 3. Select best candidate
                    if valid_candidates:
                        # distinct_candidates = list(dict.fromkeys(valid_candidates))
                        image = valid_candidates[0] # Default to first valid
                        
                        # Refinement: Prefer "gallerie" or "uploads" if available
                        for vc in valid_candidates:
                            if "gallerie" in vc or "uploads" in vc:
                                image = vc
                                break
                    
                    if is_debug_item:
                        print(f"DEBUG Selected Image: {image}")
                    
                    price = 0.0
                    price_tag = p.select_one(".text-skin-primary")
                    if price_tag:
                        price = clean_price(price_tag.get_text())
                    
                    # Deduplicate
                    if any(x['title'] == title for x in raw_items):
                        continue

                    raw_items.append({
                        "title": title,
                        "link": link,
                        "image": image,
                        "price": price,
                        "brand": "AMD" if ("RYZEN" in title.upper() or "AMD" in title.upper()) else "Intel",
                        "source": "MegaPC",
                        "status": "En Stock",
                        "specs": {"category": "cpu"}
                    })
                except Exception as e:
                    print(f"Error parsing card: {e}")
        
        print(f"Collected {len(raw_items)} total unique In-Stock items. Now enriching details...")
        
        # Enrichment Loop (Visiting each link)
        enriched_results = []
        for item in raw_items:
            try:
                print(f"Enriching {item['title']}...")
                driver.get(item['link'])
                time.sleep(2)
                
                source = driver.page_source
                enrich_soup = BeautifulSoup(source, 'html.parser')

                # 1. Image Extraction (Priority: og:image -> distinct large image)
                og_image = enrich_soup.find("meta", property="og:image")
                if og_image and og_image.get("content"):
                    item['image'] = og_image["content"]
                    print(f"  -> Found valid image: {item['image']}")
                
                # Regex for cores, threads, clock speed
                c = re.search(r"(\d+)\s?(?:coeurs|cores|cœurs|CORES)", source, re.IGNORECASE)
                if c: item['specs']['cores'] = f"{c.group(1)} Cores"
                
                t = re.search(r"(\d+)\s?(?:threads|THREADS)", source, re.IGNORECASE)
                if t: item['specs']['threads'] = f"{t.group(1)} Threads"
                
                f = re.search(r"(?:Turbo|Boost|Max).*?(\d+[.,]\d+)\s?(?:GHz|GHZ)", source, re.IGNORECASE)
                if not f:
                    f = re.search(r"(?:Fréquence|Frequency|FREQUENCE).*?(\d+[.,]\d+)\s?(?:GHz|GHZ)", source, re.IGNORECASE)
                if f:
                    val = f.group(1).replace(",", ".")
                    item['specs']['clock_speed'] = f"{val} GHz"
                
                enriched_results.append(item)
            except Exception as e:
                print(f"Failed to enrich {item['title']}: {e}")
                enriched_results.append(item) # Add even if enrich fails
        
        results = enriched_results
            
    finally:
        driver.quit()
        
    # Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(results)} items to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_megapc()
