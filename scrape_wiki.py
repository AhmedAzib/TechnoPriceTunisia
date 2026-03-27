import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import random
import re
import os

# --- DETAIL EXTRACTION LOGIC (Merged from legacy script) ---
def extract_cpu_details(title, full_text=""):
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
    
    t_upper = title.upper()
    text_upper = full_text.upper()
    
    # 1. Brand
    if "INTEL" in t_upper or "CORE" in t_upper: spec_data["brand"] = "Intel"
    elif "AMD" in t_upper or "RYZEN" in t_upper: spec_data["brand"] = "AMD"
    
    # 2. CPU Model
    if spec_data["brand"] == "Intel":
        match = re.search(r'(CORE\s?I\d[-\s]?\d{4,5}[A-Z]?)', t_upper)
        if match: spec_data["cpu"] = f"Intel {match.group(1).title()}"
        else:
             if "CELERON" in t_upper: spec_data["cpu"] = "Intel Celeron"
             elif "PENTIUM" in t_upper: spec_data["cpu"] = "Intel Pentium"
             elif "I9" in t_upper: spec_data["cpu"] = "Intel Core i9" 
             elif "I7" in t_upper: spec_data["cpu"] = "Intel Core i7"
             elif "I5" in t_upper: spec_data["cpu"] = "Intel Core i5"
             elif "I3" in t_upper: spec_data["cpu"] = "Intel Core i3"
    elif spec_data["brand"] == "AMD":
        match = re.search(r'(RYZEN\s?\d\s?\d{4}[A-Z]*)', t_upper)
        if match: spec_data["cpu"] = match.group(1).title()
        else:
             if "RYZEN 9" in t_upper: spec_data["cpu"] = "Ryzen 9"
             elif "RYZEN 7" in t_upper: spec_data["cpu"] = "Ryzen 7"
             elif "RYZEN 5" in t_upper: spec_data["cpu"] = "Ryzen 5"
             elif "RYZEN 3" in t_upper: spec_data["cpu"] = "Ryzen 3"
             elif "ATHLON" in t_upper: spec_data["cpu"] = "AMD Athlon"
             elif "THREADRIPPER" in t_upper: spec_data["cpu"] = "AMD Threadripper"

    # 3. Generation Extraction
    generation = "Unknown"
    if spec_data["brand"] == "Intel":
        if "14" in t_upper and ("GEN" in t_upper or re.search(r'14\d{2}', t_upper)): generation = "14th Gen"
        elif "13" in t_upper and ("GEN" in t_upper or re.search(r'13\d{2}', t_upper)): generation = "13th Gen"
        elif "12" in t_upper and ("GEN" in t_upper or re.search(r'12\d{2}', t_upper)): generation = "12th Gen"
        elif "11" in t_upper and ("GEN" in t_upper or re.search(r'11\d{2}', t_upper)): generation = "11th Gen"
        elif "10" in t_upper and ("GEN" in t_upper or re.search(r'10\d{2}', t_upper)): generation = "10th Gen"
    elif spec_data["brand"] == "AMD":
        if "9000" in t_upper or re.search(r'9\d{3}', t_upper): generation = "Ryzen 9000 Series"
        elif "7000" in t_upper or re.search(r'7\d{3}', t_upper): generation = "Ryzen 7000 Series"
        elif "5000" in t_upper or re.search(r'5\d{3}', t_upper): generation = "Ryzen 5000 Series"
        elif "3000" in t_upper or re.search(r'3\d{3}', t_upper): generation = "Ryzen 3000 Series"
    
    spec_data["generation"] = generation
             
    # 4. Extract Core Count (Simplified)
    cores = "Unknown"
    core_match = re.search(r'(\d+)\s*Cores?', text_upper) or re.search(r'(\d+)\s*Cœurs', text_upper)
    if core_match:
        cores = f"{core_match.group(1)} Cores"
    spec_data["cores"] = cores

    # 5. Extract Clock Speed
    clock_speed = "Unknown"
    hz_match = re.findall(r'(\d+(?:[.,]\d+)?)\s*GHz', t_upper)
    vals = []
    for m in hz_match:
        try:
            val = float(m.replace(',', '.'))
            if 1.0 < val < 6.5: # Realistic range
                vals.append(val)
        except: pass
        
    if vals:
        clock_speed = f"{max(vals)} GHz"
    spec_data["clock_speed"] = clock_speed

    return spec_data

def clean_price(price_str):
    if not price_str: return 0.0
    clean = price_str.replace(' TND', '').replace(' ', '').replace('\u00a0', '').replace(',', '.')
    clean = re.sub(r'[^\d.]', '', clean)
    try: return float(clean)
    except: return 0.0

# --- MAIN SCRAPING FUNCTION ---
def scrape_wiki():
    options = uc.ChromeOptions()
    # options.add_argument('--headless') 
    driver = uc.Chrome(options=options, version_main=143)
    
    url = "https://wiki.tn/processeur/"
    all_products = []
    page = 1
    
    try:
        while url:
            print(f"Scraping page {page}: {url}")
            driver.get(url)
            
            # Safe scroll
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 3))
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)

            try:
                WebDriverWait(driver, 15).until(
                    lambda d: d.find_elements(By.CSS_SELECTOR, ".product-card--grid") or 
                              d.find_elements(By.CSS_SELECTOR, ".woocommerce-info")
                )
            except:
                print(f"Timeout waiting for page {page}.")

            product_cards = driver.find_elements(By.CSS_SELECTOR, ".product-card--grid")
            
            if not product_cards:
                print("No products found on this page. Stopping.")
                break
                
            print(f"Found {len(product_cards)} products on page {page}.")
            
            for card in product_cards:
                try:
                    title_el = card.find_element(By.CSS_SELECTOR, ".product-card__title a")
                    title = title_el.text.strip()
                    link = title_el.get_attribute("href")
                    
                    price = 0.0
                    try:
                        price_el = card.find_element(By.CSS_SELECTOR, ".product-card__price .amount bdi")
                        price = clean_price(price_el.text)
                    except: pass
                    
                    status = "Unknown"
                    try:
                        status_el = card.find_element(By.CSS_SELECTOR, ".product-availability .brxe-shortcode-dispo")
                        status = status_el.text.strip()
                    except:
                        try:
                            status_el = card.find_element(By.CSS_SELECTOR, ".stock")
                            status = status_el.text.strip()
                        except: pass

                    # Image extraction
                    image = ""
                    try:
                        img_el = card.find_element(By.CSS_SELECTOR, ".product-card__image img")
                        image = img_el.get_attribute("src")
                        # Try to get better resolution or real src if lazy loaded
                        lazy_src = img_el.get_attribute("data-lazy-src") or img_el.get_attribute("data-src")
                        if lazy_src:
                            image = lazy_src
                    except: pass

                    # Extract Detailed Specs
                    specs = extract_cpu_details(title, full_text=title) # Using title as text source

                    product = {
                        "id": f"wiki-cpu-{random.randint(10000,99999)}",
                        "title": title,
                        "price": price,
                        "image": image,
                        "currency": "TND",
                        "status": status,
                        "link": link,
                        "specs": specs,
                        "brand": specs["brand"],
                        "category": "cpu",
                        "source": "Wiki",
                        "availability": "in-stock" if ("En Arrivage" in status or "En Stock" in status) else "out-of-stock"
                    }
                    
                    # Avoid strict duplicates based on link
                    if not any(p['link'] == link for p in all_products):
                        all_products.append(product)
                        
                except Exception as e:
                    # print(f"Item Error: {e}")
                    continue
            
            # Check for next page
            next_buttons = driver.find_elements(By.CSS_SELECTOR, "a.next")
            if next_buttons:
                url = next_buttons[0].get_attribute("href")
                page += 1
                time.sleep(random.uniform(2, 4))
            else:
                print("No 'Next' button found. Reached end of pagination.")
                break

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        
    # Save to FRONTEND DATA DIRECTORY
    output_dir = r"C:\Users\USER\Documents\programmation\frontend\src\data"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "wiki_processors.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    
    print(f"Scraping complete. Saved {len(all_products)} products to {output_path}")

if __name__ == "__main__":
    scrape_wiki()
