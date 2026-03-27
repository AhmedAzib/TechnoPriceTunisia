
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
import os

# Configuration
URL = "https://megapc.tn/shop/COMPOSANTS/CARTE%20GRAPHIQUE"
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\megapc_gpu.json"

def clean_price(price_str):
    try:
        cleaned = price_str.upper().replace("DT", "").replace("TND", "").strip()
        cleaned = "".join(c for c in cleaned if c.isdigit() or c == ".")
        return float(cleaned)
    except:
        return 0.0

def clean_text(text):
    if not text: return ""
    # Remove emojis and non-standard symbols, keep alphanumeric and basic punctuation
    # Regex explanation: Match anything NOT (alphanumeric, whitespace, standard punctuation)
    # This strips emojis like 🧠, 💾, 🚀 etc.
    return re.sub(r'[^\w\s\-\.,\/\(\)\+]', '', text).strip()

def scrape_megapc_gpu():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    results = []
    
    try:
        print(f"Navigating to {URL}...")
        driver.get(URL)
        time.sleep(5) # Initial load
        
        raw_items = []
        
        # Pagination Handling
        try:
            # Scroll to bottom to trigger any loads or find pagination
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Simple assumption: Check for pagination buttons
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
                    btn = driver.find_element(By.CSS_SELECTOR, f"button[data-page='{p_idx}']")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(3)
                except Exception as e:
                    print(f"Error navigating to page {p_idx + 1}: {e}")
                    break

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            products = soup.select("article.product-card")
            print(f"Found {len(products)} products on page {p_idx+1}.")
            
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
                        
                    price = 0.0
                    price_tag = p.select_one(".text-skin-primary")
                    if price_tag:
                        price = clean_price(price_tag.get_text())
                        
                    # Basic Image (High quality one usually in detail page, but grab thumbnail as backup)
                    image = ""
                    img_tag = p.select_one("img")
                    if img_tag:
                        src = img_tag.get("data-src") or img_tag.get("src")
                        if src:
                            if src.startswith("//"): image = "https:" + src
                            elif src.startswith("/"): image = "https://megapc.tn" + src
                            else: image = src

                    # Deduplicate
                    if any(x['title'] == title for x in raw_items):
                        continue
                        
                    raw_items.append({
                        "title": title,
                        "link": link,
                        "image": image,
                        "price": price,
                        "source": "MegaPC",
                        "status": "En Stock",
                        "category": "gpu",
                        "specs": {"category": "gpu"}
                    })
                except Exception as e:
                    print(f"Error extracting list item: {e}")

        print(f"Collected {len(raw_items)} items. Enriching...")
        
        # Enrichment
        enriched_results = []
        for item in raw_items:
            try:
                print(f"Enriching {item['title']}...")
                driver.get(item['link'])
                time.sleep(2)
                
                source = driver.page_source
                soup = BeautifulSoup(source, 'html.parser')
                
                # Update Image (OG Image is usually best)
                og_image = soup.find("meta", property="og:image")
                if og_image and og_image.get("content"):
                    item['image'] = og_image["content"]
                
                # Extract Description / Specs
                # MegaPC usually has specifications in a list or text block
                # User Example used emojis, suggesting text content.
                # Look for the spec list container
                
                description_text = soup.get_text(" ", strip=True) 
                
                # We will try to parse line by line from specific containers if possible, 
                # but full text regex is robust for this specific format user provided.
                
                # 1. GPU / Chipset
                # "GPU : NVIDIA GeForce RTX 5050"
                m_gpu = re.search(r"GPU\s*:\s*(.+?)(?:\s+Mémoire|\s+Fréquence|\s+Cœurs|$)", description_text, re.IGNORECASE)
                if m_gpu:
                    item['specs']['gpu'] = clean_text(m_gpu.group(1))
                else:
                    item['specs']['gpu'] = clean_text(item['title']) # Fallback
                    
                # 2. Memory (Amount + Type + Speed)
                # "Mémoire : 8GB GDDR6 – 20 Gbps"
                m_mem = re.search(r"Mémoire\s*:\s*(.+?)(?:\s+Fréquence|\s+Cœurs|$)", description_text, re.IGNORECASE)
                if m_mem:
                    mem_str = m_mem.group(1).strip()
                    # Extract VRAM: "8GB"
                    m_vram = re.search(r"(\d+)\s?(?:GB|Go)", mem_str, re.IGNORECASE)
                    if m_vram: item['specs']['vram'] = f"{m_vram.group(1)} GB"
                    
                    # Extract Type: "GDDR6"
                    m_type = re.search(r"(GDDR\d+[X]?)", mem_str, re.IGNORECASE)
                    if m_type: item['specs']['memory_type'] = m_type.group(1).upper()
                    
                    # Extract Speed: "20 Gbps" => vitesse_memoire
                    m_speed = re.search(r"(\d+(?:[.,]\d+)?)\s?(?:Gbps|Gbit\/s)", mem_str, re.IGNORECASE)
                    if m_speed: item['specs']['vitesse_memoire'] = m_speed.group(1).replace(",", ".")
                    
                # 3. Boost Clock
                # "Fréquence Boost : Jusqu’à 2617 MHz"
                m_boost = re.search(r"Fréquence\s*Boost\s*:\s*.*?(?:Jusqu’à)?\s*(\d+)\s*MHz", description_text, re.IGNORECASE)
                if m_boost:
                    item['specs']['boost_clock'] = f"{m_boost.group(1)} MHz"
                
                # 4. CUDA Cores
                # "Cœurs CUDA : 2560 unités"
                m_cuda = re.search(r"Cœurs\s*CUDA\s*:\s*(\d+)", description_text, re.IGNORECASE)
                if m_cuda:
                    item['specs']['cuda_cores'] = m_cuda.group(1)
                    
                # 5. PSU
                # "Alim. requise : 550 W"
                m_psu = re.search(r"Alim\.?\s*requise\s*:\s*(\d+)\s*W", description_text, re.IGNORECASE)
                if m_psu:
                    item['specs']['psu'] = f"{m_psu.group(1)} W"
                
                # 6. Bus (Often in description or inferred, but checking text)
                # Not explicitly in user example, but maybe "128-bit"?
                # Checking for "Interface Mémoire" or just "X bit" ?
                m_bus = re.search(r"(\d+)\s*bit", description_text, re.IGNORECASE)
                if m_bus:
                    item['specs']['bus_memoire'] = f"{m_bus.group(1)} bit"

                # 7. Extreme Performance (Check if description has "Extreme Performance")
                # User asked to check for "Extreme Performance: 2635 MHz" type string
                # Note: The scraper should just grab description. The ProductsPage.jsx logic does extraction.
                # BUT, better to pre-extract if we can.
                item['description'] = description_text # Store full text for frontend regex fallback
                
                enriched_results.append(item)
                
            except Exception as e:
                print(f"Error enriching {item['title']}: {e}")
                enriched_results.append(item)
        
        results = enriched_results

    finally:
        driver.quit()
        
    # Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(results)} GPUs to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_megapc_gpu()
