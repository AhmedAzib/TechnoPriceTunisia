import requests
from bs4 import BeautifulSoup
import json
import time
import re
import random

# Configuration
BASE_URL = "https://www.sbsinformatique.com/carte-mere-tunisie"
OUTPUT_FILE = "frontend/src/data/sbs_motherboards.json"

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

def extract_motherboard_specs(text):
    """
    Extracts motherboard specific specs from the description text.
    Target fields: Socket, Form Factor, Memory Type, Max Speed, Max Capacity.
    """
    specs = {}
    if not text:
        return specs
        
    text_upper = text.upper()
    
    # 1. Socket
    # Regex for common sockets
    socket_match = re.search(r'(?:SOCKET|LGA|AM4|AM5|TR4|sTRX4)\s?([\w\d]+)', text_upper)
    if socket_match:
        # Refine socket extraction
        if "LGA" in text_upper:
            lga_val = re.search(r'LGA\s?(\d+)', text_upper)
            if lga_val: specs['socket'] = f"LGA {lga_val.group(1)}"
        elif "AM4" in text_upper: specs['socket'] = "AM4"
        elif "AM5" in text_upper: specs['socket'] = "AM5"
        elif "TR4" in text_upper: specs['socket'] = "TR4"
        elif "STRX4" in text_upper: specs['socket'] = "sTRX4"
        
    # 2. Memory Type (DDR3, DDR4, DDR5)
    if "DDR5" in text_upper: specs['memory_type'] = "DDR5"
    elif "DDR4" in text_upper: specs['memory_type'] = "DDR4"
    elif "DDR3" in text_upper: specs['memory_type'] = "DDR3"
    
    # 3. Form Factor
    if "E-ATX" in text_upper or "EXTENDED ATX" in text_upper: specs['form_factor'] = "E-ATX"
    elif "MICRO-ATX" in text_upper or "MICRO ATX" in text_upper or "M-ATX" in text_upper or "UATX" in text_upper: specs['form_factor'] = "Micro-ATX"
    elif "MINI-ITX" in text_upper or "MINI ITX" in text_upper: specs['form_factor'] = "Mini-ITX"
    elif "ATX" in text_upper: specs['form_factor'] = "ATX" # Check ATX last as it is a substring of others
    
    # 4. Max Memory Speed
    # Look for "4666 MHz", "6400 MHz" etc.
    speed_matches = re.findall(r'(\d{4})\s?MHZ', text_upper)
    if speed_matches:
        # Convert to ints, filter legitimate range (1000-10000)
        valid_speeds = [int(s) for s in speed_matches if 1066 <= int(s) <= 12000]
        if valid_speeds:
            specs['memory_speed'] = f"{max(valid_speeds)} MHz"
            
    # Return raw text for full context if needed
    specs['raw_description'] = text
    return specs

def get_product_details(product_url):
    try:
        time.sleep(random.uniform(1.0, 2.0)) 
        response = requests.get(product_url, headers=HEADERS, timeout=30)
        if response.status_code != 200:
            print(f"Failed to fetch details {product_url}: {response.status_code}", flush=True)
            return {}
        
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        details = {}
        
        # Method 1: Description Div
        decs_div = soup.find('div', class_='tvproduct-page-decs')
        if decs_div:
            # Clean text
            text_content = decs_div.get_text('\n')
            text_content = clean_text(text_content)
            
            # Extract structured specs
            details.update(extract_motherboard_specs(text_content))
            
            # Keep original text for debugging/fallback
            details['description'] = text_content
            
        # Method 2: Data sheet (often has structured specs)
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
    max_pages = 20 # usually less for motherboards
    seen_urls = set()
    
    print("Starting SBS Motherboard Scraper...", flush=True)
    
    while page <= max_pages:
        url = f"{BASE_URL}?page={page}"
        print(f"Processing Page {page}...", flush=True)
        
        try:
            time.sleep(random.uniform(1.0, 2.0))
            response = requests.get(url, headers=HEADERS, timeout=30)
            if response.status_code != 200:
                print(f"Failed to fetch page {page}. Status: {response.status_code}", flush=True)
                break
            
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
                    
                    # Check 2: Overlay/Label (Primary Source of Truth)
                    unavailable = item.find('span', class_='product-unavailable')
                    if unavailable:
                        is_out_of_stock = True
                        
                    availability = item.find('span', class_='product-availability')
                    if availability:
                        text = availability.get_text().lower()
                        if "rupture" in text or "stock épuisé" in text:
                            is_out_of_stock = True

                    # User Request Correction: 
                    # Some items like "GIGABYTE A520M K V2" have disabled buttons but are requested.
                    # If there is NO explicit "Rupture" label, and it has a price, we assume it's valid.
                    
                    if is_out_of_stock:
                        continue
                        
                    # Extract Data
                    title_div = item.find('div', class_='product-title')
                    if not title_div: continue
                    link_tag = title_div.find('a')
                    if not link_tag: continue
                    
                    title = clean_text(link_tag.get_text())
                    product_link = link_tag['href']
                    
                    if product_link in seen_urls:
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
                        
                    print(f"  + Found: {title}", flush=True)
                    
                    # Navigate to details to get full specs
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
                    
                    products.append(product_data)
                    new_items_on_page += 1
                    
                except Exception as e:
                    print(f"Error extracting item: {e}", flush=True)
                    continue
            
            if new_items_on_page == 0:
                print("No in-stock items found on this page.", flush=True)
                # Don't break immediately, might be mixed stock pages
                
            # Pagination Logic
            next_link = soup.find('a', rel='next')
            if not next_link:
                print("No next page found. Finished.", flush=True)
                break
                
            page += 1
            
        except Exception as e:
            print(f"Error looping pages: {e}", flush=True)
            break
            
        # Intermediate Save
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
            
    # Final Save (Critical if loop breaks early)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
        
    print(f"Done. Saved {len(products)} motherboards to {OUTPUT_FILE}", flush=True)

if __name__ == "__main__":
    scrape_sbs()
