import requests
from bs4 import BeautifulSoup
import json
import re
import os
import random

# Configuration
BASE_URL = "https://skymil-informatique.com/25-processeur-intel"
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\skymil_intel.json"

def clean_price(price_str):
    if not price_str:
        return 0.0
    # Handle "239,000 TND"
    clean = price_str.upper().replace('TND', '').replace('DT', '').replace('\u00a0', '').strip()
    clean = clean.replace(',', '.') 
    clean = re.sub(r'[^\d.]', '', clean)
    try:
        return float(clean)
    except ValueError:
        return 0.0

def extract_cpu_details(title, description_html):
    spec_data = {
        "category": "cpu",
        "cpu": "Unknown",
        "brand": "Intel",
        "cores": "Unknown",
        "threads": "Unknown",
        "clock_speed": "Unknown",
        "cache": "Unknown",
        "graphics": "Unknown",
        "socket": "Unknown",
        "generation": "Unknown"
    }
    
    t_upper = title.upper()
    
    # Parse Description HTML
    desc_soup = BeautifulSoup(description_html, 'html.parser')
    desc_text = desc_soup.get_text(separator=' ', strip=True)
    full_text_upper = desc_text.upper()
    
    # 1. CPU Model Extraction
    # Core Ultra
    ultra_match = re.search(r'(CORE\s?ULTRA\s?\d\s?(?:PROCESSOR\s?)?\d{3}[A-Z]*)', t_upper)
    if ultra_match:
        raw = ultra_match.group(1).title()
        spec_data["cpu"] = f"Intel {raw.replace('Processor ', '')}"
    else:
        # Standard Core iX
        match = re.search(r'(CORE\s?I\d[-\s]?\d{3,5}[A-Z]?)', t_upper)
        if match:
             spec_data["cpu"] = f"Intel {match.group(1).title()}"
        else:
             if "CELERON" in t_upper: spec_data["cpu"] = "Intel Celeron"
             elif "PENTIUM" in t_upper: spec_data["cpu"] = "Intel Pentium"

    # 2. Generation Logic
    if "CORE ULTRA" in t_upper: 
        if "200" in t_upper or "285K" in t_upper or "265K" in t_upper or "245K" in t_upper: 
            spec_data["generation"] = "Core Ultra (Series 2)"
        else:
            spec_data["generation"] = "Core Ultra (Series 1)"
    elif "14" in t_upper and ("GEN" in t_upper or re.search(r'14\d{2}', t_upper)): spec_data["generation"] = "14th Gen"
    elif "13" in t_upper and ("GEN" in t_upper or re.search(r'13\d{2}', t_upper)): spec_data["generation"] = "13th Gen"
    elif "12" in t_upper and ("GEN" in t_upper or re.search(r'12\d{2}', t_upper)): spec_data["generation"] = "12th Gen"
    elif "11" in t_upper and ("GEN" in t_upper or re.search(r'11\d{2}', t_upper)): spec_data["generation"] = "11th Gen"
    elif "10" in t_upper and ("GEN" in t_upper or re.search(r'10\d{2}', t_upper)): spec_data["generation"] = "10th Gen"

    # 3. Spec Extraction from Emojis/Text
    # Use the <p> tags content directly if possible for better context
    
    # Cores
    # "🧠 œurs : 4 cœurs et 8 threads"
    # "⚙️ 2 cœurs et 2 threads"
    cores_match = re.search(r'(?:🧠|⚙️)\s*(?:CŒURS|ŒURS)?\s*:?\s*(\d+)\s*CŒURS', full_text_upper) # "🧠 œurs : 4 cœurs"
    if not cores_match:
         cores_match = re.search(r'(\d+)\s*CŒURS', full_text_upper)
    
    if cores_match:
        spec_data["cores"] = f"{cores_match.group(1)} Cores"

    # Threads
    threads_match = re.search(r'(\d+)\s*THREADS', full_text_upper)
    if threads_match:
        spec_data["threads"] = f"{threads_match.group(1)} Threads"

    # Frequency
    # "⚡ Fréquence : 3.7 GHz"
    freq_match = re.search(r'(?:⚡|🚀|🌀)\s*FRQUENCE\s*(?:DE\s?BASE)?\s*:?\s*(\d+(?:[.,]\d+)?)\s*GHZ', full_text_upper.replace('É', ''))
    if freq_match:
        val = freq_match.group(1).replace(',', '.')
        spec_data["clock_speed"] = f"{val} GHz"

    # Cache
    # "💾 Cache : 6 Mo" or "📦 Cache L3 : 6 Mo"
    cache_match = re.search(r'(?:💾|📦|🗂️)\s*CACHE\s*(?:L3)?\s*:?\s*(\d+\s*MO)', full_text_upper)
    if cache_match:
        spec_data["cache"] = cache_match.group(1).title()

    # Graphics
    # "🎨 Chipset graphique : Intel UHD Graphics 610"
    # "🎮 Chipset graphique : Pas de chipset"
    gpu_match = re.search(r'(?:🎨|🎮|🖥️)\s*CHIPSET\s*GRAPHIQUE\s*:?\s*([^<\n\r]+)', full_text_upper)
    if gpu_match:
        gpu_text = gpu_match.group(1).strip()
        if "AUCUN" in gpu_text or "PAS DE" in gpu_text:
            spec_data["graphics"] = "None"
        else:
            # Clean up: "Intel UHD Graphics 610"
            if "INTEL" in gpu_text:
                spec_data["graphics"] = gpu_text.title()
    
    return spec_data

def scrape_skymil():
    print("Launching Skymile Scraper...", flush=True)
    all_products = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    page = 1
    max_pages = 10 # Safety limit
    
    while page <= max_pages:
        url = f"{BASE_URL}?page={page}"
        print(f"Fetching Page {page}: {url}...", flush=True)
        
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 404:
                print(f"Page {page} not found.")
                break
                
            soup = BeautifulSoup(r.content, 'html.parser')
            
            # Select products
            items = soup.select("article.product-miniature")
            
            if not items:
                print(f"No items found on page {page}. Stopping.")
                break

            print(f"Found {len(items)} items on page {page}.", flush=True)
            
            # Deduplicate logic: Check if we are seeing the same products as page 1 (if site redirects invalid page to page 1)
            # Simple check: if first item title is same as first item of all_products, break
            if all_products and items:
                 first_title = items[0].select_one(".product-title a").get_text(strip=True)
                 if any(p['title'] == first_title for p in all_products):
                     print("Duplicate page detected (redirect to first page?). Stopping.")
                     break
            
            found_new = False
            for item in items:
                # Title
                title_elem = item.select_one(".product-title a")
                if not title_elem: continue
                title = title_elem.get_text(strip=True)
                link = title_elem['href']
                
                # Check absolute duplicate in current run
                if any(p['link'] == link for p in all_products):
                    continue

                # Stock Status
                input_qty = item.select_one('input[name="qty"]')
                # Usually if input qty exists, it can be bought. 
                # Also check specific "out of stock" flags if available
                # But skymil usually removes add to cart if OOS.
                add_btn = item.select_one(".add-to-cart")
                disabled = add_btn and "disabled" in add_btn.get("class", [])
                
                availability = "out-of-stock" if disabled else "in-stock"
                
                # Double check with user example "En stock" text
                # Try to find "En stock" in the item text
                if "En stock" in item.get_text():
                    availability = "in-stock"

                # ID
                try:
                    p_id = item['data-id-product']
                except:
                    p_id = f"skymil-cpu-{random.randint(1000,9999)}"

                # Price
                price_elem = item.select_one(".price")
                price = clean_price(price_elem.get_text(strip=True)) if price_elem else 0.0

                # Image
                img_elem = item.select_one(".thumbnail-container img")
                image = img_elem['src'] if img_elem else ""

                # Description (Specs)
                desc_elem = item.select_one(".product-description-short")
                desc_html = str(desc_elem) if desc_elem else ""
                
                specs = extract_cpu_details(title, desc_html)
                
                product = {
                    "id": f"skymil-cpu-{p_id}",
                    "title": title,
                    "price": price,
                    "image": image,
                    "brand": specs["brand"],
                    "category": "cpu",
                    "source": "Skymile",
                    "availability": availability,
                    "link": link,
                    "specs": specs
                }
                
                all_products.append(product)
                print(f"Scraped: {title} | {specs['cpu']}")
                found_new = True

            if not found_new:
                print("No new products found on this page.")
                break
                
            page += 1
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    # Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(all_products)} products to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_skymil()
