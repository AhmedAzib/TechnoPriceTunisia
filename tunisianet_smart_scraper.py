import requests
from bs4 import BeautifulSoup
import json
import time
import random

# Configuration
OUTPUT_FILE = "tunisianet_computers.json"

# URLs to scrape
# 301: Laptops (Ordinateur Portable)
# 302: Desktops (Ordinateur de Bureau)
# 700: Gamer Laptops ? Wait, let's verify. 
# Based on site navigation:
# Informatique -> Ordinateur Portable (id 301)
# Informatique -> Ordinateur de Bureau (id 302)
# Informatique -> Pc Portable Gamer (id 681 - from previous artifact read, wait, let me re-check the chunk)
# Chunk said: [Pc Portable Gamer](https://www.tunisianet.com.tn/681-pc-portable-gamer)
# Chunk said: [Pc de Bureau Gamer](https://www.tunisianet.com.tn/682-pc-de-bureau-gamer)
# So I should use 681 and 682, not 700/701.

URLS = [
    "https://www.tunisianet.com.tn/301-ordinateur-portable",
    "https://www.tunisianet.com.tn/302-ordinateur-de-bureau",
    "https://www.tunisianet.com.tn/681-pc-portable-gamer",
    "https://www.tunisianet.com.tn/682-pc-de-bureau-gamer",
    "https://www.tunisianet.com.tn/373-pc-de-bureau", # Also "Pc de bureau" ? Check if 302 covers it.
    # The chunk showed "Ordinateur de Bureau" (701) AND "Pc de bureau" (373). 
    # Actually chunk said: [Ordinateur de Bureau](https://www.tunisianet.com.tn/701-ordinateur-de-bureau)
    # AND [Pc de bureau](https://www.tunisianet.com.tn/373-pc-de-bureau)
    # I will add all of them to be safe and let deduplication handle it.
    "https://www.tunisianet.com.tn/701-ordinateur-de-bureau",
    "https://www.tunisianet.com.tn/702-ordinateur-portable", # Chunk also showed this ID.
    "https://www.tunisianet.com.tn/703-pc-portable-pro",
    "https://www.tunisianet.com.tn/686-pc-tout-en-un",
]

PHONE_KEYWORDS = [
    "smartphone", "téléphone", "gsm", "mobile", 
    "infinix", "oppo", "vivo", "redmi", "realme", 
    "iphone", "galaxy a", "galaxy s", "galaxy z", "galaxy m",
    "tecno", "itel", "nokia", "huawei"
]

# Words that might trigger false positives if alone, but okay if "Laptop" or "Pc" isn't present?
# Actually, strict exclusion if title HAS "Smartphone" or "Gsm".
# "Iphone" is definitely a phone.

def is_phone(title):
    t = title.lower()
    for kw in PHONE_KEYWORDS:
        if kw in t:
            # Safe guard: "Mobile Workstation" ?
            if kw == "mobile" and "workstation" in t:
                continue
            return True
    return False

def scrape():
    seen_keys = set()
    all_products = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    print("Starting Tunisianet Smart Scraper...")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Phone Filter: Active")

    for base_url in URLS:
        print(f"\nScraping Category: {base_url}")
        page = 1
        while True:
            url = f"{base_url}?page={page}"
            print(f"   Page {page}...", end='\r')
            
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code != 200:
                    print(f"\n   Failed to load page {page} (Status: {resp.status_code})")
                    break
                
                soup = BeautifulSoup(resp.content, 'html.parser')
                products = soup.select('.item-product') # or .product-miniature
                
                if not products:
                    products = soup.select('.product-miniature')
                
                if not products:
                    print(f"\n   ⚠️ No products found on page {page}. Checking if end of category.")
                    break
                
                items_added_on_page = 0
                
                for p in products:
                    try:
                        # Title
                        title_el = p.select_one('.product-title a')
                        if not title_el: continue
                        title = title_el.text.strip()
                        link = title_el['href']
                        
                        # Phone Filter
                        if is_phone(title):
                            # print(f"      Skipped Phone: {title}")
                            continue

                        # Reference (for strict deduplication)
                        # Usually matches "Reference : ..." but might be hidden or in different place.
                        # Tunisianet usually puts reference in a span .product-reference usually inside description or hidden.
                        # We will try to fetch it if available, else filter by Title + Price + Link
                        
                        # Price
                        price_el = p.select_one('.price')
                        price = price_el.text.strip().replace('\xa0', '').replace('DT', '').replace(',', '.').strip() if price_el else "0"
                        
                        try:
                           price_val = float(price)
                        except:
                           price_val = 0.0

                        # Image
                        img_el = p.select_one('.product-thumbnail img')
                        img = img_el['src'] if img_el else ""

                        # Create Deduplication Key
                        # Strict: Title + Link (Link usually contains ID)
                        # User said: "if they have 1 diffrence let them" -> So if Title OR Link is different, keep it.
                        # But we want to avoid EXACT duplicates (same product scraped from "Laptops" and "Gamer Laptops")
                        # Usually the Link is the most unique identifier.
                        
                        uniq_key = link # strict unique url
                        
                        if uniq_key in seen_keys:
                            continue
                        
                        seen_keys.add(uniq_key)
                        
                        all_products.append({
                            "title": title,
                            "price": price_val,
                            "link": link,
                            "image": img,
                            "source": "Tunisianet"
                        })
                        items_added_on_page += 1
                        
                    except Exception as e:
                        continue

                # print(f"   Page {page}: +{items_added_on_page} items (Total: {len(all_products)})")
                
                # Check for "Next" button
                next_btn = soup.select_one('a.next')
                if not next_btn or 'disabled' in next_btn.get('class', []):
                    # print(f"\n   End of category at page {page}")
                    break
                
                page += 1
                # time.sleep(0.5) # Be polite
                
            except Exception as e:
                print(f"\n   Error on page {page}: {e}")
                break
    
    print(f"\nScraping Complete!")
    print(f"Total Unique Computers: {len(all_products)}")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=4, ensure_ascii=False)
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape()
