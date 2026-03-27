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
BASE_URL = "https://www.wiki.tn/processeur"
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\wiki_processors.json"

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
             elif "ULTRA" in t_upper: spec_data["cpu"] = "Intel Core Ultra"
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
        elif "CELERON" in t_upper or "PENTIUM" in t_upper: generation = "Intel Legacy"
        elif "ULTRA" in t_upper: generation = "Core Ultra (Series 1)" # Assumption for now
    elif spec_data["brand"] == "AMD":
        if "9000" in t_upper or re.search(r'9\d{3}', t_upper): generation = "Ryzen 9000 Series"
        elif "8000" in t_upper or re.search(r'8\d{3}', t_upper): generation = "Ryzen 8000 Series"
        elif "7000" in t_upper or re.search(r'7\d{3}', t_upper): generation = "Ryzen 7000 Series"
        elif "5000" in t_upper or re.search(r'5\d{3}', t_upper): generation = "Ryzen 5000 Series"
        elif "4000" in t_upper or re.search(r'4\d{3}', t_upper): generation = "Ryzen 4000 Series"
        elif "3000" in t_upper or re.search(r'3\d{3}', t_upper): generation = "Ryzen 3000 Series"
    
    spec_data["generation"] = generation
             
    # 4. Extract Core Count
    cores = "Unknown"
    # Try regex first
    core_match = re.search(r'(\d+)\s*Cores?', text_upper)
    if not core_match:
        core_match = re.search(r'(\d+)\s*Cœurs', text_upper)
    
    if core_match:
        cores = f"{core_match.group(1)} Cores"
    else:
        # Fallback Keywords
        if "DUAL CORE" in t_upper: cores = "2 Cores"
        elif "QUAD CORE" in t_upper: cores = "4 Cores"
        elif "HEXA CORE" in t_upper: cores = "6 Cores"
        elif "OCTA CORE" in t_upper: cores = "8 Cores"
        elif "DECA CORE" in t_upper: cores = "10 Cores"
        elif "DODÉCA CORE" in t_upper: cores = "12 Cores"
    
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
            if model in t_upper:
                cores = count
                break
    spec_data["cores"] = cores

    # 5. Extract Clock Speed
    clock_speed = "Unknown"
    # Exclude "Up To" or "Max" to find base clock if possible, or usually just grab the max GHZ listed as prominent
    # Wiki usually listing format: "i5-12400F / 2.5 GHz / ..."
    
    # Regex for X.Y GHz
    hz_match = re.findall(r'(\d+(?:[.,]\d+)?)\s*GHz', text_upper)
    vals = []
    for m in hz_match:
        try:
            val = float(m.replace(',', '.'))
            if 1.0 < val < 6.5: # Realistic range
                vals.append(val)
        except:
            pass
    if vals:
        # If multiple, usually min is base, max is turbo. Let's show max for exciting UI? Or Base?
        # User preferred specific values earlier. Let's just pick the largest one (Turbo) as it looks better/is common marketing, 
        # unless it's strictly defined. Actually, usually "Clock Speed" refers to Base or Boost. 
        # Let's take the first one found if only one, or max if multiple to show potential. 
        # But wait, user edited previous scrapers to be robust. 
        # Safe bet: Largest value found is Boost, smallest is Base. 
        # Comparisons usually show Boost.
        clock_speed = f"{max(vals)} GHz"
        
    spec_data["clock_speed"] = clock_speed

    return spec_data

def scrape_wiki_processors():
    print("Launching Selenium for Wiki Processors...", flush=True)
    all_products = []
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # 1. Scrape Listing Pages
        product_urls = []
        # Wiki usually has ?page=2 etc.
        # Check standard category URL
        
        # Start with the probed URL
        driver.get(BASE_URL)
        time.sleep(5) # Wait for Cloudflare/Loading
        
        # Check if we are denied
        if "403 Forbidden" in driver.title or "Access denied" in driver.page_source:
             print(f"Access Denied on Initial Load. Title: {driver.title}")
             time.sleep(10)
        
        print(f"Page Title: {driver.title}")
        
        # Debug: Save Page Source
        with open("wiki_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved wiki_debug.html for inspection.")

        # Find products
        # Wiki uses .product-miniature or similar
        items = driver.find_elements(By.CSS_SELECTOR, "div.product-container")
        if not items:
             items = driver.find_elements(By.CSS_SELECTOR, "li.product-item")
        if not items:
             items = driver.find_elements(By.CSS_SELECTOR, ".product-miniature") # Typical Prestashop
        
        print(f"Found {len(items)} items on page 1.", flush=True)
        
        for item in items:
            try:
                link = item.find_element(By.CSS_SELECTOR, "a.product-name").get_attribute("href")
                if link and link not in product_urls:
                    product_urls.append(link)
            except:
                pass
                
        # Handle pagination if needed (Checking for "Suivant" button)
        # Simplify: Just scrape page 1 for now as it usually has recent stuff, or try loop if successful
        
        print(f"Found {len(product_urls)} products to scrape.", flush=True)
        
        # 2. Visit Each PDP
        for i, link in enumerate(product_urls):
            print(f"[{i+1}/{len(product_urls)}] Scraping {link}...")
            try:
                driver.get(link)
                # Wait for title
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
                
                title = driver.find_element(By.TAG_NAME, "h1").text.strip()
                
                # Availability
                availability = "in-stock"
                try:
                    # Wiki: "En stock" or "Rupture"
                    # Look for #availability_value or .availability-span
                    text_body = driver.find_element(By.TAG_NAME, "body").text.upper()
                    if "RUPTURE" in text_body or "HORS STOCK" in text_body:
                        availability = "out-of-stock"
                        # User wants In Stock? usually yes. But let's keep all and filter later or tag it.
                        # Actually user request usually implies visible valid products.
                        # Let's keep it but mark availability.
                except:
                    pass
                
                # Price
                try:
                    price_elem = driver.find_element(By.ID, "our_price_display")
                    price = clean_price(price_elem.text)
                except:
                    price = 0.0
                
                # Image
                try:
                    img_elem = driver.find_element(By.ID, "bigpic")
                    image = img_elem.get_attribute('src')
                except:
                    image = ""
                    
                # Description / Specs
                # Wiki usually has specs in a tab or div
                full_text = driver.find_element(By.TAG_NAME, "body").text
                
                # Extract Specs
                specs = extract_cpu_details(title, full_text=full_text)
                
                product = {
                    "id": f"wiki-cpu-{random.randint(10000,99999)}",
                    "title": title,
                    "price": price,
                    "image": image,
                    "brand": specs["brand"],
                    "category": "cpu",
                    "source": "Wiki",
                    "availability": availability,
                    "link": link,
                    "specs": specs
                }
                
                if availability == "in-stock": # Filter strictly if desired, or keep all. Let's keep in-stock for catalog quality.
                     all_products.append(product)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Error scraping {link}: {e}")
    
    except Exception as e:
        print(f"Global Error: {e}")
    finally:
        driver.quit()
        
    print(f"Total extracted: {len(all_products)}")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_wiki_processors()
