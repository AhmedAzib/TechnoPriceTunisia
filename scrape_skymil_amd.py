import requests
from bs4 import BeautifulSoup
import json
import re
import os
import random

# Configuration
BASE_URL = "https://skymil-informatique.com/131-processeur-amd"
OUTPUT_FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\skymil_amd.json"

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

def extract_cpu_details(title, description_html):
    spec_data = {
        "category": "cpu",
        "cpu": "Unknown",
        "brand": "AMD",
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
    # Ryzen 5 1600AF, Ryzen 9 9950X
    match = re.search(r'(RYZEN\s?\d\s?\d{4}[A-Z]*)', t_upper)
    if match:
         spec_data["cpu"] = match.group(1).title()
    else:
         if "ATHLON" in t_upper: spec_data["cpu"] = "AMD Athlon"
         elif "THREADRIPPER" in t_upper: spec_data["cpu"] = "AMD Threadripper"

    # 2. Generation / Series Logic
    if "9000" in t_upper or re.search(r'9\d{3}', t_upper): spec_data["generation"] = "Ryzen 9000 Series"
    elif "8000" in t_upper or re.search(r'8\d{3}', t_upper): spec_data["generation"] = "Ryzen 8000 Series"
    elif "7000" in t_upper or re.search(r'7\d{3}', t_upper): spec_data["generation"] = "Ryzen 7000 Series"
    elif "5000" in t_upper or re.search(r'5\d{3}', t_upper): spec_data["generation"] = "Ryzen 5000 Series"
    elif "4000" in t_upper or re.search(r'4\d{3}', t_upper): spec_data["generation"] = "Ryzen 4000 Series"
    elif "3000" in t_upper or re.search(r'3\d{3}', t_upper): spec_data["generation"] = "Ryzen 3000 Series"
    elif "1000" in t_upper or "1600" in t_upper: spec_data["generation"] = "Ryzen 1000 Series"

    # 3. Spec Extraction from Emojis/Text
    
    # Cores
    # "🧠 œurs : 4 cœurs"
    # "🧩 6 Cœurs / 12 Threads"
    cores_match = re.search(r'(?:🧠|🧩|🔷)\s*(?:CŒURS|CORES)?\s*:?\s*(\d+)\s*C', full_text_upper)
    if not cores_match:
         cores_match = re.search(r'(\d+)\s*CŒURS', full_text_upper)
    
    if cores_match:
        spec_data["cores"] = f"{cores_match.group(1)} Cores"

    # Threads
    # "12 Threads"
    threads_match = re.search(r'(\d+)\s*THREADS', full_text_upper)
    if threads_match:
        spec_data["threads"] = f"{threads_match.group(1)} Threads"

    # Frequency
    # "⚡ Fréquence : 3.2 GHz"
    # "⏱️ Fréquences : 4.3 GHz"
    freq_match = re.search(r'(?:⚡|🚀|🌀|⏱️)\s*FR[ÉE]QUENCE[S]?\s*(?:DE\s?BASE)?\s*:?\s*(\d+(?:[.,]\d+)?)\s*GHZ', full_text_upper)
    if freq_match:
        val = freq_match.group(1).replace(',', '.')
        spec_data["clock_speed"] = f"{val} GHz"

    # Cache
    # "🧠 Cache : 16 Mo L3"
    # "🗂️ Cache : L1... L3 : 64 Mo"
    # Look for L3 specifically if possible, or just "Cache : X Mo"
    l3_match = re.search(r'L3\s*:?\s*(\d+)\s*MO', full_text_upper)
    if l3_match:
         spec_data["cache"] = f"{l3_match.group(1)} Mo"
    else:
        cache_match = re.search(r'(?:💾|📦|🗂️|🧠)\s*CACHE\s*:?\s*(\d+\s*MO)', full_text_upper)
        if cache_match:
            spec_data["cache"] = cache_match.group(1).title()

    # Graphics
    # "🖥️ Contrôleur graphique : Aucun"
    # "🎨 Graphiques intégrés : AMD Radeon Graphics"
    gpu_match = re.search(r'(?:🎨|🎮|🖥️|🔍)\s*(?:CHIPSET|CONTRÔLEUR|GRAPHIQUES?)\s*(?:GRAPHIQUE|INTÉGRÉS?)\s*:?\s*([^<\n\r]+)', full_text_upper)
    if gpu_match:
        gpu_text = gpu_match.group(1).strip()
        if "AUCUN" in gpu_text or "PAS DE" in gpu_text:
            spec_data["graphics"] = "None"
        elif "RADEON" in gpu_text:
             spec_data["graphics"] = "AMD Radeon Graphics"
        else:
             spec_data["graphics"] = gpu_text.title()

    # Socket
    # "🔌 Socket : AM4"
    # "🧩 Socket : AMD AM5"
    socket_match = re.search(r'(?:🔌|🧩|💻)\s*SOCKET\s*:?\s*([^<\n\r]+)', full_text_upper)
    if socket_match:
        sock_text = socket_match.group(1).strip()
        if "AM5" in sock_text: spec_data["socket"] = "AM5"
        elif "AM4" in sock_text: spec_data["socket"] = "AM4"
        elif "TR4" in sock_text: spec_data["socket"] = "TR4"

    return spec_data

def scrape_skymil():
    print("Launching Skymile AMD Scraper...", flush=True)
    all_products = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    page = 1
    max_pages = 10 
    
    while page <= max_pages:
        url = f"{BASE_URL}?page={page}"
        print(f"Fetching Page {page}: {url}...", flush=True)
        
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 404:
                print(f"Page {page} not found.")
                break
                
            soup = BeautifulSoup(r.content, 'html.parser')
            
            items = soup.select("article.product-miniature")
            
            if not items:
                print(f"No items found on page {page}. Stopping.")
                break

            print(f"Found {len(items)} items on page {page}.", flush=True)
            
            # Deduplicate logic
            if all_products and items:
                 first_title = items[0].select_one(".product-title a").get_text(strip=True)
                 if any(p['title'] == first_title for p in all_products):
                     print("Duplicate page detected. Stopping.")
                     break
            
            found_new = False
            for item in items:
                # Title
                title_elem = item.select_one(".product-title a")
                if not title_elem: continue
                title = title_elem.get_text(strip=True)
                link = title_elem['href']
                
                # Check absolute duplicate
                if any(p['link'] == link for p in all_products):
                    continue

                # Stock Status
                input_qty = item.select_one('input[name="qty"]')
                add_btn = item.select_one(".add-to-cart")
                disabled = add_btn and "disabled" in add_btn.get("class", [])
                
                availability = "out-of-stock" if disabled else "in-stock"
                
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
