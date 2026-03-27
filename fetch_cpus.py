import json
import time
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# File paths
JSON_PATH = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"

def load_data():
    if not os.path.exists(JSON_PATH):
        print(f"Error: {JSON_PATH} not found.")
        return []
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Data saved.")

def normalize_cpu(cpu_text):
    if not cpu_text:
        return "Unknown"
    
    # Clean up whitespace
    cpu_text = cpu_text.strip()
    
    # Common cleanup
    # Remove "Processeur" prefix if extracted from meta sometimes
    cpu_text = re.sub(r'^Processeur\s*[:|-]?\s*', '', cpu_text, flags=re.IGNORECASE)
    
    return cpu_text

def get_cpu_from_soup(soup):
    # Strategy 1: Table
    try:
        table = soup.select_one("#product-attribute-specs-table")
        if table:
            rows = table.select("tr")
            for row in rows:
                th = row.select_one("th")
                if th and "Processeur" in th.get_text():
                    td = row.select_one("td")
                    if td:
                        return td.get_text(strip=True)
    except Exception as e:
        pass

    # Strategy 2: Meta Description
    try:
        meta_desc = soup.select_one('meta[name="description"]')
        if meta_desc:
            content = meta_desc.get("content", "")
            # Look for "Processeur:" followed by text until a comma or hyphen or end
            # Example: ... - Processeur: Mediatek Helio G91 Ultra (12 nm) Octa-core - ...
            match = re.search(r'Processeur\s*:\s*([^,\-]+)', content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
    except Exception as e:
        pass
        
    return "Unknown"

def main():
    data = load_data()
    if not data:
        return

    print(f"Loaded {len(data)} products.")
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    # Speed up loading by disabling images
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=options)
    
    processed_count = 0
    
    try:
        for product in data:
            # Check if CPU is already known and not "Unknown"
            # (Assuming we might want to retry "Unknown" ones, or just skip all if properly populated)
            # For this run, let's assume we want to fill missing ones.
            # If 'specs' doesn't exist, create it (though it should)
            if 'specs' not in product:
                product['specs'] = {}
            
            current_cpu = product['specs'].get('cpu')
            if current_cpu and current_cpu != "Unknown":
                continue # Skip if we already have it
            
            url = product.get('link')
            if not url:
                continue

            print(f"Processing ({processed_count + 1}/{len(data)}): {product.get('title')[:30]}...", flush=True)
            
            try:
                driver.get(url)
                # Wait a bit for potential JS - though standard extraction needs plain HTML mostly for these parts
                # But MyTek might be dynamic.
                # Let's wait mainly for body
                time.sleep(2) 
                
                soup = BeautifulSoup(driver.page_source, "html.parser")
                cpu = get_cpu_from_soup(soup)
                
                # Normalize
                cpu = normalize_cpu(cpu)
                
                product['specs']['cpu'] = cpu
                print(f"  -> Found CPU: {cpu}", flush=True)
                
                processed_count += 1
                
                # Save every 10 updates
                if processed_count % 10 == 0:
                    save_data(data)
                    
            except Exception as e:
                print(f"  -> Error processing {url}: {e}", flush=True)

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        driver.quit()
        save_data(data) # Final save
        print("Done.")

if __name__ == "__main__":
    main()
