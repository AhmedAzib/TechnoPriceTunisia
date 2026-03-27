import requests
from bs4 import BeautifulSoup
import json
import time
import re
import random

# Configuration
BASE_URL = "https://www.sbsinformatique.com/cartes-graphiques-tunisie?q=Prix-TND-119-12549"
OUTPUT_FILE = "sbs_gpu.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

def clean_text(text):
    if not text:
        return ""
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_price(price_text):
    if not price_text:
        return 0.0
    # "1 234,000 TND" -> 1234.0
    clean_p = re.sub(r'[^\d,.]', '', price_text) 
    clean_p = clean_p.replace(',', '.')
    try:
        clean_p = clean_p.replace(' ', '')
        return float(clean_p)
    except:
        return 0.0

def parse_spec_lines(text):
    specs = {}
    if not text:
        return specs
        
    # Split by <br> tags first if possible, but here we get text with newlines
    lines = text.split('\n')
    current_key = None
    
    for line in lines:
        line = clean_text(line)
        if not line:
            continue
            
        # Skip noise lines that might appear in the description
        if line in ["Taxe incluse", "Rupture de stock", "En stock", "Quantité :", "1", "ZOTAC"]:
            continue
        # Skip price-like lines if they appear in description
        if "TND" in line and any(c.isdigit() for c in line):
            continue

        # Common separators: ":", "-", "–"
        
        # Remove leading dash/hyphen
        if line.startswith('-') or line.startswith('–'):
            line = line[1:].strip()
            
        if ':' in line:
            parts = line.split(':', 1)
            key = clean_text(parts[0])
            value = clean_text(parts[1])
            
            # Heuristic: Keys shouldn't be too long. If it is, it might be a sentence with a colon.
            if len(key) < 60 and key and value:
                specs[key] = value
                current_key = key
            else:
                 # Treat as continuation or description
                 if current_key:
                    specs[current_key] += " " + line
        elif "Refroidissement" in line and "WINDFORCE" in line:
             specs["Refroidissement"] = line.replace("Refroidissement", "").strip()
             current_key = "Refroidissement"
        else:
            # Continuation line?
            if current_key:
                specs[current_key] += " " + line

    return specs

def get_product_details(product_url):
    try:
        # 10000% SAFE: Increased delay
        time.sleep(random.uniform(2.0, 4.0)) 
        response = requests.get(product_url, headers=HEADERS, timeout=30)
        if response.status_code != 200:
            print(f"Failed to fetch details {product_url}: {response.status_code}", flush=True)
            return {}
        
        # FORCE UTF-8
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.content, 'html.parser')
        details = {}
        
        # Method: Description Div (tvproduct-page-decs)
        decs_div = soup.find('div', class_='tvproduct-page-decs')
        if decs_div:
            # Replace <br> with newlines to ensure clean separation
            for br in decs_div.find_all('br'):
                br.replace_with('\n')
            
            text_content = decs_div.get_text('\n')
            details.update(parse_spec_lines(text_content))
            
        # Fallback/Supplemental: Data sheet
        data_sheet = soup.find('dl', class_='data-sheet')
        if data_sheet:
            dt_elements = data_sheet.find_all('dt', class_='name')
            dd_elements = data_sheet.find_all('dd', class_='value')
            for dt, dd in zip(dt_elements, dd_elements):
                key = clean_text(dt.get_text()).rstrip(':')
                value = clean_text(dd.get_text())
                if key and value:
                    details[key] = value
                    
        return details

    except Exception as e:
        print(f"Error fetching details from {product_url}: {e}")
        return {}

def scrape_sbs():
    products = []
    page = 1
    max_pages = 50 
    seen_urls = set()
    consecutive_empty_pages = 0
    
    print("Starting SBS Scraper (Ultra Safe Mode)...", flush=True)
    print(f"Target: {BASE_URL}", flush=True)
    
    while page <= max_pages:
        url = f"{BASE_URL}&page={page}"
        print(f"Processing Page {page}...", flush=True)
        
        try:
            # Random delay before page load
            time.sleep(random.uniform(2.0, 3.0))
            response = requests.get(url, headers=HEADERS, timeout=30)
            if response.status_code != 200:
                print(f"Failed to fetch page {page}. Status: {response.status_code}", flush=True)
                break
            
            # FORCE UTF-8
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.content, 'html.parser')
            product_items = soup.find_all('article', class_='product-miniature')
            
            if not product_items:
                print("No products found on page.", flush=True)
                break
            
            new_items_on_page = 0
            
            for item in product_items:
                try:
                    # STRICT STOCK CHECK
                    is_out_of_stock = False
                    
                    # Check 1: Button state/class
                    cart_btn = item.find('button', class_='add-to-cart')
                    if cart_btn:
                        if cart_btn.has_attr('disabled'):
                            is_out_of_stock = True
                        classes = cart_btn.get('class', [])
                        if 'tvproduct-out-of-stock' in classes or 'disable' in classes:
                            is_out_of_stock = True
                    else:
                        # No cart button often means out of stock
                        is_out_of_stock = True
                        
                    # Check 2: Overlay/Label
                    unavailable = item.find('span', class_='product-unavailable')
                    if unavailable:
                        is_out_of_stock = True
                        
                    availability = item.find('span', class_='product-availability')
                    if availability:
                        text = availability.get_text().lower()
                        if "rupture" in text or "stock épuisé" in text:
                            is_out_of_stock = True

                    if is_out_of_stock:
                        # print("  - Skipping (Out of Stock)")
                        continue
                        
                    # Extract Data
                    title_div = item.find('div', class_='product-title')
                    if not title_div: continue
                    link_tag = title_div.find('a')
                    if not link_tag: continue
                    
                    title = clean_text(link_tag.get_text())
                    product_link = link_tag['href']
                    
                    # DUPLICATE PREVENTION
                    if product_link in seen_urls:
                        # print(f"  - Skipping duplicate: {title}")
                        continue
                    
                    seen_urls.add(product_link)
                    
                    # Price
                    price = 0.0
                    price_div = item.find('div', class_='product-price-and-shipping')
                    if price_div:
                        price_span = price_div.find('span', class_='price')
                        if price_span:
                            price = parse_price(price_span.get_text())
                            
                    # Image
                    image_url = ""
                    img_tag = item.find('img')
                    if img_tag:
                        image_url = img_tag.get('src', '')
                        
                    print(f"  + Scraped: {title}", flush=True)
                    
                    # Verify details
                    specs = get_product_details(product_link)
                    
                    product_data = {
                        "title": title,
                        "link": product_link,
                        "price": price,
                        "image": image_url,
                        "source": "SBS Informatique",
                        "status": "En Stock",
                        "specs": specs
                    }
                    
                    # FILTER: Exclude non-GPU items
                    title_upper = title.upper()
                    excluded_keywords = ["BRACKET", "SUPPORT", "BRIDGE", "CABLE", "BOITIER"]
                    if any(keyword in title_upper for keyword in excluded_keywords):
                        print(f"  - Skipping non-GPU item: {title}", flush=True)
                        continue

                    products.append(product_data)
                    new_items_on_page += 1
                    
                except Exception as e:
                    print(f"Error extracting item: {e}", flush=True)
                    continue
            
            if new_items_on_page == 0:
                consecutive_empty_pages += 1
                if consecutive_empty_pages >= 2:
                    print("No new items found for 2 pages. Stopping to prevent loops.", flush=True)
                    break
            else:
                consecutive_empty_pages = 0

            # Pagination Logic
            next_link = soup.find('a', rel='next')
            if not next_link:
                print("No next page found.", flush=True)
                break
                
            page += 1
            time.sleep(1) # Polite delay between pages
            
        except Exception as e:
            print(f"Error looping pages: {e}", flush=True)
            break
            
        # Save Progress after each page
        print(f"Saving progress ({len(products)} products)...", flush=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
            
    # Final Save
    print(f"Saving final {len(products)} products to {OUTPUT_FILE}...", flush=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    print("Done.", flush=True)

if __name__ == "__main__":
    scrape_sbs()
