
from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import time
import concurrent.futures
import random

INPUT_FILE = "spacenet_laptop_leads.txt"
OUTPUT_FILE = "src/data/spacenet_raw.json"
MAX_WORKERS = 10

def get_product_data(url):
    # Filters
    exclude_keywords = [
        'chargeur', 'sacoche', 'souris', 'clavier', 'casque', 'cable', 'câble', 
        'adaptateur', 'support', 'refroidisseur', 'micro', 'protection', 'etui', 
        'toner', 'cartouche', 'imprimante', 'ecran', 'barrette', 'disque', 'composant',
        'hub-usb', 'station-d-accueil', 'web-cam', 'manette', 'tapis-souris', 'cle-usb',
        'pate-thermique', 'logiciel', 'antivirus', 'microsoft-office'
    ]
    include_keywords = ['pc', 'portable', 'ordinateur', 'macbook', 'laptop']
    
    # Pre-check URL to save request bandwidth
    url_lower = url.lower()
    if any(bad in url_lower for bad in exclude_keywords):
        return None
    
    # Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # Random sleep to be nice
        time.sleep(random.uniform(0.1, 0.5))
        
        response = requests.get(url, headers=headers, impersonate="chrome110", timeout=30)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Meta Extraction
        title_tag = soup.find("meta", property="og:title")
        title = title_tag["content"] if title_tag else ""
        
        # Double check Title for excluded keywords
        title_lower = title.lower()
        if any(bad in title_lower for bad in exclude_keywords):
            return None
            
        # Ensure it is actually a computer (Double check)
        # Some items might be 'Ventilateur pour PC Portable'
        # The URL filter is good, but Title filter is better.
        # Strict inclusion: must have one of include_keywords
        if not any(good in title_lower for good in include_keywords):
            # Fallback: check category meta if available
            cat_tag = soup.find("meta", property="product:category") # Not standard OG, but schema sometimes has it
            # If we are unsure, maybe skip? 
            # User said "add ALL", so let's be lenient on inclusion if exclusion passed.
            pass

        price_tag = soup.find("meta", property="product:price:amount")
        price = price_tag["content"] if price_tag else "0.000"
        
        image_tag = soup.find("meta", property="og:image")
        image = image_tag["content"] if image_tag else ""
        
        brand_tag = soup.find("meta", property="product:brand")
        brand = brand_tag["content"] if brand_tag else "Unknown"
        
        # Determine "Type" based on title
        p_type = "Laptop"
        if "gamer" in title_lower or "gaming" in title_lower:
            p_type = "Gamer"
        elif "macbook" in title_lower or "apple" in title_lower or "imac" in title_lower: # User said no desktop, but iMac is AIO. User said "no desktop". iMac is desktop.
             if "imac" in title_lower:
                 return None # Skip iMac
             p_type = "MacBook"
        
        # Skip weird prices
        try:
             if float(price) < 100: # Unlikely to be a laptop
                 return None
        except:
             pass

        return {
            "name": title,
            "price": f"{price} TND",
            "image": image,
            "link": url,
            "brand": brand,
            "type": p_type
        }

    except Exception as e:
        # print(f"Error scraping {url}: {e}")
        return None

def main():
    print("Loading URLs...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"Total Candidates: {len(urls)}")
    
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(get_product_data, url): url for url in urls}
        
        completed = 0
        for future in concurrent.futures.as_completed(future_to_url):
            data = future.result()
            if data:
                results.append(data)
            
            completed += 1
            if completed % 50 == 0:
                print(f"Processed {completed}/{len(urls)}... (Found {len(results)} valid products)")
                
    print(f"Scraping complete. Found {len(results)} products.")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
        
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
