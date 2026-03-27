
import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re

class SpaceNetGPUScraper:
    def __init__(self):
        self.base_url = "https://spacenet.tn/21-carte-graphique"
        self.output_file = "../src/data/spacenet_gpu.json"
        
        # User requested "1000% safe" - Ensuring high quality headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8'
        }
        self.products = []

    def clean_price(self, price_str):
        if not price_str:
            return 0.0
        # User Format: "799,000 DT TTC" -> 799.0
        # "1 619,000 DT TTC" -> 1619.0
        
        clean = price_str.lower().replace('dt', '').replace('ttc', '').strip()
        # Remove thousands separators (space or non-breaking space)
        clean = clean.replace(' ', '').replace('\xa0', '').replace('\u202f', '') 
        # Replace decimal separator
        clean = clean.replace(',', '.')
        
        # Extract first valid float
        match = re.search(r'(\d+\.?\d*)', clean)
        if match:
            return float(match.group(1))
        return 0.0

    def parse_specs(self, desc_text):
        # User provided details usually found in description paragraph similar to:
        # "Carte Graphique MSI GeForce RTX 3050 - Chipset graphique: NVIDIA GeForce RTX 3050 - Nombre de cœurs: 2560 unités..."
        
        specs = {}
        
        # Normalize
        text = desc_text.replace('\n', ' ').replace('\r', '')
        
        # Extract pairs:  Label: Value  (delimited by - or start/end)
        # Note: Spacenet descriptions often follow "Key: Value - Key: Value" format
        
        # 1. Chipset (GPU Model)
        # "Chipset graphique : NVIDIA GeForce RTX 5060 Ti"
        m = re.search(r'Chipset\s*graphique\s*[:]\s*([^-\.]+)', text, re.IGNORECASE)
        if m: specs['gpu'] = m.group(1).strip()
        
        # 2. Memory (VRAM)
        # "Mémoire graphique : 16 Go" or "Mémoire graphique: 8Go"
        m = re.search(r'Mémoire\s*graphique\s*[:]\s*([^-\.]+)', text, re.IGNORECASE)
        if m: specs['vram'] = m.group(1).strip()
        
        # 3. Memory Type
        # "Type de mémoire : GDDR7"
        m = re.search(r'Type\s*de\s*mémoire\s*[:]\s*([^-\.]+)', text, re.IGNORECASE)
        if m: specs['memory_type'] = m.group(1).strip()
        
        # 4. Memory Speed
        # "Vitesse mémoire : 28 Gbit/s"
        m = re.search(r'Vitesse\s*mémoire\s*[:]\s*([^-\.]+)', text, re.IGNORECASE)
        if m: specs['memory_speed'] = m.group(1).strip()
        
        # 5. Bus
        # "Bus mémoire : 128 bits"
        m = re.search(r'Bus\s*mémoire\s*[:]\s*([^-\.]+)', text, re.IGNORECASE)
        if m: specs['memory_bus'] = m.group(1).strip()
        
        # 6. PSU
        # "Bloc d'alimentation recommandé : 600 W"
        m = re.search(r'(?:Bloc\s*d\'alimentation|Alimentation)\s*recommandé\s*[:]\s*([^-\.]+)', text, re.IGNORECASE)
        if m: specs['psu'] = m.group(1).strip()
        
        # 7. Cores (CUDA/Stream)
        # "Nombre de cœurs: 2560 unités" or "Cœurs : 4608 Units"
        m = re.search(r'(?:Nombre\s*de\s*cœurs|Cœurs)\s*[:]\s*([^-\.]+)', text, re.IGNORECASE)
        if m: specs['cores'] = m.group(1).strip()
        else:
             m = re.search(r'Cuda\s*Cores\s*[:]\s*([^-\.]+)', text, re.IGNORECASE)
             if m: specs['cores'] = m.group(1).strip()

        # 8. Boost Clock
        # "Fréquence boostée : Boost : 1807 MHz"
        m = re.search(r'Fréquence\s*boostée\s*[:]\s*([^-\.]+)', text, re.IGNORECASE)
        if m: specs['boost_clock'] = m.group(1).strip()
        
        # 9. Extreme Performance (Safe Extraction)
        # "Fréquence boostée : 2602 MHz (Extreme Performance: 2617 MHz (MSI Center))"
        # Often nested inside the boost clock text or separately
        m = re.search(r'Extreme\s*Performance\s*[:]\s*([^)\.]+)', text, re.IGNORECASE)
        if m: specs['extreme_performance'] = m.group(1).strip()

        return specs

    def scrape(self):
        page = 1
        # Hard limit for safety, though they usually have fewer pages for GPUs
        max_pages = 10 
        
        while page <= max_pages:
            url = f"{self.base_url}?page={page}"
            print(f"Scraping {url}...")
            
            try:
                # SSL Verify False to prevent hangs on some corp networks/proxies
                resp = requests.get(url, headers=self.headers, timeout=30, verify=False)
                if resp.status_code != 200:
                    print(f"Status {resp.status_code} at page {page}. Stopping.", flush=True)
                    break
                
                soup = BeautifulSoup(resp.content, 'html.parser')
                items = soup.select('.product-miniature')
                
                if not items:
                    print("No more products found.", flush=True)
                    break
                
                added_count = 0
                for item in items:
                    # 1. STOCK CHECK (User: "download all the en stock")
                    stock_elem = item.select_one('.product-quantities label')
                    if not stock_elem:
                        # Sometimes stock label is missing if out of stock or pre-order
                        # Safest to assume skip if not explicitly "En stock"
                        continue
                        
                    stock_text = stock_elem.get_text(strip=True).lower()
                    if "en stock" not in stock_text:
                        continue
                        
                    # 2. Extract Basic Info
                    title_tag = item.select_one('.product_name a')
                    if not title_tag: continue
                    
                    title = title_tag.get_text(strip=True)
                    link = title_tag['href']
                    
                    price_tag = item.select_one('.price')
                    price_str = price_tag.get_text(strip=True) if price_tag else "0"
                    price_val = self.clean_price(price_str)
                    
                    img_tag = item.select_one('.cover_image img')
                    img_src = img_tag['src'] if img_tag else ""
                    
                    # 3. Extract Detailed Specs from Product Page
                    # Listing page description is often empty or incomplete.
                    # We must visit the link.
                    specs = {}
                    try:
                        # Politeness/Throttling
                        time.sleep(0.5) 
                        print(f"    Fetching details: {link} ...", end="", flush=True)
                        
                        p_resp = requests.get(link, headers=self.headers, timeout=15, verify=False)
                        if p_resp.status_code == 200:
                            p_soup = BeautifulSoup(p_resp.content, 'html.parser')
                            
                            # Spacenet detailed specs are usually in a tab or just in #description
                            # Try multiple selectors
                            full_desc = ""
                            
                            # 1. Main features block (often under price or right column)
                            features_sec = p_soup.select_one('.product-features')
                            if features_sec:
                                full_desc += features_sec.get_text(" ", strip=True) + " "
                            
                            # 2. Description Tab
                            desc_tab = p_soup.select_one('.product-description') # standard prestashop
                            if desc_tab:
                                full_desc += desc_tab.get_text(" ", strip=True) + " "
                                
                            # 3. Short Description (if on page)
                            short_desc = p_soup.select_one('#product-description-short-content') or p_soup.select_one('.product-desc-short')
                            if short_desc:
                                full_desc += short_desc.get_text(" ", strip=True) + " "

                            specs = self.parse_specs(full_desc)
                            specs['description'] = full_desc[:500] + "..." # Truncate for JSON size/preview
                            print(" Done.", flush=True)
                        else:
                            print(f" Failed ({p_resp.status_code}).", flush=True)
                            
                    except Exception as e:
                        print(f" Error fetching details: {e}", flush=True)
                    
                    product = {
                        "id": f"sn-gpu-{item.get('data-id-product')}",
                        "title": title,
                        "price": price_val,
                        "image": img_src,
                        "link": link,
                        "source": "Spacenet", # Normalized name
                        "category": "gpu",
                        "specs": specs,
                        "availability": "in-stock"
                    }
                    
                    # DEDUPLICATION CHECK (1000% SAFE)
                    existing_ids = [p['id'] for p in self.products]
                    if product['id'] not in existing_ids:
                        self.products.append(product)
                        added_count += 1
                
                print(f"  + Added {added_count} GPUs from page {page}", flush=True)
                
                # Incremental Save (Safety)
                with open(self.output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.products, f, indent=2, ensure_ascii=False)
                
                # Check for "Next" button specifically to be safe
                next_btn = soup.select_one('a.next')
                if not next_btn:
                    # Double check pagination list just in case
                    # But usually 'next' class is reliable on Spacenet themes (PrestaShop)
                    print("No next page button found.", flush=True)
                    break
                    
                page += 1
                time.sleep(1.0) # Politeness
                
            except Exception as e:
                print(f"Error on page {page}: {e}", flush=True)
                break
                
        # Save Result
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        print(f"Done. Saved {len(self.products)} GPUs to {self.output_file}")

if __name__ == "__main__":
    s = SpaceNetGPUScraper()
    s.scrape()
