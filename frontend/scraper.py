import requests
from bs4 import BeautifulSoup
import json
import re
import os

# CONFIG: 12 Pages to maintain 500+ items
URLS = [ 
    {"url": "https://www.tunisianet.com.tn/702-pc-portable-gamer", "cat": "Gamer"}, 
    {"url": "https://www.tunisianet.com.tn/301-pc-portable-tunisie", "cat": "Business"} 
] 
MAX_PAGES = 12 
OUTPUT_FILE = "src/data/products.json"

all_products = [] 
current_id = 1

def get_specs(text, category): 
    # Clean text but keep standard formats
    clean_text = text.upper().replace("-", " ").replace("\n", " ").replace("  ", " ") 
    specs = { "brand": "Other", "cpu": "Unknown", "gpu": "Integrated", "ram": "8GB", "hz": "60Hz", "storage": "256GB", "screen": "15.6", "res": "FHD", "panel": "IPS", "os": "FreeDOS", "category": category }

    # --- 1. CPU (The "Dragnet" List) ---
    # High End
    if "ULTRA 9" in clean_text: specs["cpu"] = "Core Ultra 9"
    elif "ULTRA 7" in clean_text: specs["cpu"] = "Core Ultra 7"
    elif "ULTRA 5" in clean_text: specs["cpu"] = "Core Ultra 5"
    elif "I9" in clean_text: specs["cpu"] = "Core i9"
    elif "I7" in clean_text: specs["cpu"] = "Core i7"
    elif "I5" in clean_text: specs["cpu"] = "Core i5"
    elif "I3" in clean_text: specs["cpu"] = "Core i3"
    # AMD High End
    elif "RYZEN 9" in clean_text: specs["cpu"] = "Ryzen 9"
    elif "RYZEN 7" in clean_text: specs["cpu"] = "Ryzen 7"
    elif "RYZEN 5" in clean_text: specs["cpu"] = "Ryzen 5"
    elif "RYZEN 3" in clean_text: specs["cpu"] = "Ryzen 3"
    # Apple
    elif "M3" in clean_text: specs["cpu"] = "Apple M3"
    elif "M2" in clean_text: specs["cpu"] = "Apple M2"
    elif "M1" in clean_text: specs["cpu"] = "Apple M1"
    # Low End / Budget (The missing ones)
    elif "CELERON" in clean_text or "N4020" in clean_text or "N4500" in clean_text: specs["cpu"] = "Celeron"
    elif "PENTIUM" in clean_text or "N6000" in clean_text or "SILVER" in clean_text: specs["cpu"] = "Pentium"
    elif "ATHLON" in clean_text or "3020E" in clean_text: specs["cpu"] = "Athlon"

    # --- 2. GPU ---
    if "4090" in clean_text: specs["gpu"] = "RTX 4090"
    elif "4080" in clean_text: specs["gpu"] = "RTX 4080"
    elif "4070" in clean_text: specs["gpu"] = "RTX 4070"
    elif "4060" in clean_text: specs["gpu"] = "RTX 4060"
    elif "4050" in clean_text: specs["gpu"] = "RTX 4050"
    elif "3060" in clean_text: specs["gpu"] = "RTX 3060"
    elif "3050" in clean_text: specs["gpu"] = "RTX 3050"
    elif "2050" in clean_text: specs["gpu"] = "RTX 2050"
    elif "1650" in clean_text: specs["gpu"] = "GTX 1650"
    elif "ARC" in clean_text: specs["gpu"] = "Intel Arc"
    elif "MX" in clean_text: specs["gpu"] = "NVIDIA MX"
    elif "RADEON" in clean_text: specs["gpu"] = "Radeon"
    elif "IRIS" in clean_text or "XE" in clean_text: specs["gpu"] = "Intel Iris Xe"

    # --- 3. BRAND ---
    brands = ["MSI", "ASUS", "LENOVO", "HP", "DELL", "ACER", "APPLE", "GIGABYTE", "HUAWEI", "SAMSUNG", "INFINIX", "MICROSOFT"] 
    for b in brands: 
        if b in clean_text: specs["brand"] = b.capitalize(); break

    # --- 4. RAM ---
    ram = re.search(r'(\d+)\s*GO', clean_text)
    if ram: specs["ram"] = f"{ram.group(1)}GB"
    
    # --- 5. STORAGE ---
    if "1 TO" in clean_text or "1TB" in clean_text: specs["storage"] = "1TB SSD"
    elif "512" in clean_text: specs["storage"] = "512GB SSD"
    elif "256" in clean_text: specs["storage"] = "256GB SSD"
    elif "128" in clean_text: specs["storage"] = "128GB SSD"
    
    # --- 6. HZ ---
    hz = re.search(r'(\d{2,3})\s*HZ', clean_text) 
    if hz: specs["hz"] = f"{hz.group(1)}Hz"

    # --- 7. OS ---
    if "WIN" in clean_text: specs["os"] = "Windows 11"
    
    # --- 8. RESOLUTION ---
    if "WQXGA" in clean_text or "QHD" in clean_text or "2K" in clean_text: specs["res"] = "QHD (2K)" 
    elif "UHD" in clean_text or "4K" in clean_text: specs["res"] = "UHD (4K)" 
    elif "FHD" in clean_text: specs["res"] = "FHD (1080p)"
    elif "HD" in clean_text and "FHD" not in clean_text: specs["res"] = "HD (720p)"
    
    # --- 9. PANEL ---
    if "OLED" in clean_text: specs["panel"] = "OLED"

    # --- 10. SCREEN SIZE ---
    if "17.3" in clean_text: specs["screen"] = "17.3\""
    elif "16" in clean_text: specs["screen"] = "16.0\""
    elif "15.6" in clean_text: specs["screen"] = "15.6\""
    elif "14" in clean_text: specs["screen"] = "14.0\""
    elif "13" in clean_text: specs["screen"] = "13.3\""

    return specs

print(f"Starting ULTIMATE SCRAPE (Filtering Trash & Accessories)...")

for source in URLS: 
    for page in range(1, MAX_PAGES + 1): 
        try: 
            print(f"Scanning {source['cat']} Page {page}...") 
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            r = requests.get(f"{source['url']}?page={page}", headers=headers) 
            soup = BeautifulSoup(r.content, 'html.parser') 
            items = soup.find_all('div', class_='item-product')

            if not items: break
            for item in items:
                try:
                    title_tag = item.find('h2', class_='product-title').find('a')
                    title = title_tag.text.strip()
                    
                    # --- TRASH FILTER ---
                    # Skip items that are clearly accessories
                    bad_words = ["SACOCHE", "SOURIS", "CASQUE", "COQUE", "CHARGEUR", "REFROIDISSEUR", "STATION D'ACCUEIL"]
                    if any(bad in title.upper() for bad in bad_words):
                        print(f"   [SKIPPED] Accessory found: {title[:20]}...")
                        continue
                        
                    desc_tag = item.find('div', class_='product-description-short')
                    desc = desc_tag.text.strip() if desc_tag else ""
                    
                    full_text = f"{title} {desc}"
                    
                    price = float(re.sub(r'[^\d]', '', item.find('span', class_='price').text)) / 1000
                    img = item.find('img')['data-full-size-image-url']
                    link = title_tag['href']
                    
                    specs = get_specs(full_text, source['cat'])
                    
                    # Log remaining unknowns to help debugging
                    if specs['cpu'] == "Unknown":
                        print(f"   [STILL UNKNOWN] {title[:40]}...")
                    
                    all_products.append({
                        "id": current_id, "title": title, "price": price, 
                        "image": img, "link": link, "specs": specs, "brand": specs["brand"]
                    })
                    current_id += 1
                except: continue
        except: break

os.makedirs("src/data", exist_ok=True) 
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f: 
    json.dump(all_products, f, indent=2) 
print(f"CLEANUP COMPLETE! {len(all_products)} High-Quality Laptops Saved.")
