
import requests
from bs4 import BeautifulSoup
import json
import time
import re
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SBSGPUScraper:
    def __init__(self):
        # User provided link: https://www.sbsinformatique.com/cartes-graphiques-tunisie?q=Prix-TND-119-12549
        self.start_url = "https://www.sbsinformatique.com/cartes-graphiques-tunisie?q=Prix-TND-119-12549"
        self.output_file = "../src/data/sbs_gpus.json"
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.google.com/'
        }
        self.products = []

    def clean_price(self, price_str):
        if not price_str:
            return 0.0
        # Format: "1 290,000 TND" -> 1290.0
        clean = price_str.lower().replace('tnd', '').replace('dt', '').replace('ttc', '').strip()
        clean = clean.replace(' ', '').replace('\xa0', '').replace('\u202f', '') # Remove spaces
        clean = clean.replace(',', '.') # Fix decimal
        
        match = re.search(r'(\d+\.?\d*)', clean)
        if match:
            return float(match.group(1))
        return 0.0

    def parse_specs(self, desc_text):
        specs = {}
        # Normalize text
        text = desc_text.replace('\n', ' ').replace('\r', '').replace('\xa0', ' ')
        
        # 1. GPU Model (Chipset)
        m = re.search(r'(?:Chipset|Processeur)\s*graphique\s*[:]\s*([^-\.]+)', text, re.IGNORECASE)
        if m: specs['gpu'] = m.group(1).strip()
        
        # 2. VRAM (Mémoire)
        m = re.search(r'(?:Mémoire|Taille\s*mémoire)\s*(?:graphique)?\s*[:]\s*([^-\.]+)', text, re.IGNORECASE)
        if m: specs['vram'] = m.group(1).strip()
        
        # 3. Memory Type
        m = re.search(r'Type\s*de\s*mémoire\s*[:]\s*([^-\.]+)', text, re.IGNORECASE)
        if m: specs['memory_type'] = m.group(1).strip()
        
        # 4. Bus
        m = re.search(r'Bus\s*mémoire\s*[:]\s*([^-\.]+)', text, re.IGNORECASE)
        if m: specs['bus_memoire'] = m.group(1).strip()
        
        # 5. Connectors (Sortie)
        m = re.search(r'Sortie\s*(?:video|s)?\s*[:]\s*([^-\.]+)', text, re.IGNORECASE)
        if m: specs['connectors'] = m.group(1).strip()
        
        # 6. PSU (Alimentation)
        m = re.search(r'(?:Alimentation|PSU)\s*recommandé[e]?\s*[:]\s*([^-\.]+)', text, re.IGNORECASE)
        if m: specs['psu'] = m.group(1).strip()
        
        # 7. CUDA Cores
        m = re.search(r'(?:Cuda|Coeurs)\s*Cores?[:]\s*(\d+)', text, re.IGNORECASE)
        if m: specs['cuda_cores'] = m.group(1).strip()

        # 8. Boost Clock
        m = re.search(r'(?:Boost|Fréquence)\s*Clock\s*[:]\s*([^-\.]+)', text, re.IGNORECASE)
        if m: specs['boost_clock'] = m.group(1).strip()

        return specs

    def scrape(self):
        # Handle pagination if necessary. The URL has query params, so standard logical paging (?page=2) usually appends to it.
        # e.g. ...&page=2 or ?q=...&page=2
        
        page = 1
        max_pages = 5 # Safety limit
        
        current_url = self.start_url
        
        while page <= max_pages:
            print(f"Scraping Page {page}: {current_url}")
            
            try:
                resp = requests.get(current_url, headers=self.headers, verify=False, timeout=30)
                if resp.status_code != 200:
                    print(f"Failed to fetch page {page}: Status {resp.status_code}")
                    break
                
                soup = BeautifulSoup(resp.content, 'html.parser')
                
                # SBS Selectors (PrestaShop)
                # Usually .product-miniature or .item
                items = soup.select('.product-miniature')
                if not items:
                    # Fallback selectors
                    items = soup.select('.ajax_block_product') 
                
                if not items:
                    print(f"No products found on page {page}.")
                    # Debug: Dump HTML to see what's wrong if 0 items on page 1
                    if page == 1:
                        with open("sbs_debug.html", "w", encoding="utf-8") as f:
                            f.write(resp.text)
                    break
                
                print(f"Found {len(items)} items on page {page}")
                
                added_on_page = 0
                for item in items:
                    try:
                        # Extract Product Info
                        title_elem = item.select_one('.product-title a') or item.select_one('.product-name') or item.select_one('h3.h3.product-title a')
                        if not title_elem:
                            continue
                            
                        title = title_elem.get_text(strip=True)
                        link = title_elem.get('href')
                        
                        price_elem = item.select_one('.price')
                        price_str = price_elem.get_text(strip=True) if price_elem else ""
                        price = self.clean_price(price_str)
                        
                        img_elem = item.select_one('.thumbnail.product-thumbnail img') or item.select_one('.cover-image')
                        img_src = img_elem.get('src') if img_elem else ""
                        
                        # Stock
                        # Sometimes specified as "En Stock" or "Rupture"
                        stock_elem = item.select_one('.product-availability') or item.select_one('.availability')
                        stock_status = "unknown"
                        if stock_elem:
                            if "en stock" in stock_elem.get_text(strip=True).lower():
                                stock_status = "in-stock"
                            elif "rupture" in stock_elem.get_text(strip=True).lower():
                                stock_status = "out-of-stock"
                        else:
                            # If no explicit tag, but price is valid, assume in-stock? 
                            # User said "download those gpus".
                            # I will default to in-stock if price > 0
                            if price > 0:
                                stock_status = "in-stock"

                        # Filter: User specifically listed items.
                        # I will assume "download those gpus" means I should get everything in the query result.
                        if stock_status == "out-of-stock":
                            # Should I skip? User said "download those gpus". 
                            # The list implies they are viewable. 
                            # Usually scrapers skip OOS. I'll include them but mark availability.
                            pass

                        # Detailed Specs (Visit Page)
                        specs = {}
                        if link:
                            # print(f"  > Fetching details: {title[:30]}...")
                            try:
                                p_resp = requests.get(link, headers=self.headers, verify=False, timeout=15)
                                if p_resp.status_code == 200:
                                    p_soup = BeautifulSoup(p_resp.content, 'html.parser')
                                    # Description
                                    desc_div = p_soup.select_one('.product-description') or p_soup.select_one('#description')
                                    desc_text = desc_div.get_text(strip=True) if desc_div else ""
                                    specs = self.parse_specs(desc_text)
                                    specs['description'] = desc_text[:1000] # Cap length
                            except Exception as e:
                                print(f"    Error fetching details: {e}")

                        # Create Product Object
                        product = {
                            "id": f"sbs-gpu-{item.get('data-id-product', title[:10])}", # Fallback ID
                            "title": title,
                            "price": price,
                            "image": img_src,
                            "link": link,
                            "source": "SBS Informatique",
                            "category": "gpu",
                            "specs": specs,
                            "availability": stock_status
                        }
                        
                        self.products.append(product)
                        added_on_page += 1
                        
                    except Exception as e:
                        print(f"Error parsing item: {e}")
                        continue
                
                print(f"  + Extracted {added_on_page} products.")
                
                # Next Page Logic
                # Check for "next" link in pagination
                next_link = soup.select_one('a.next') or soup.select_one('li.pagination_next a')
                if next_link:
                    current_url = next_link.get('href')
                    page += 1
                    time.sleep(1) 
                else:
                    print("No next page.")
                    break
                    
            except Exception as e:
                print(f"Global Error: {e}")
                break
        
        # Save
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(self.products)} products to {self.output_file}")

if __name__ == "__main__":
    scraper = SBSGPUScraper()
    scraper.scrape()
