
import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os

# --- UTILS ---
def clean_price(price_text):
    clean = price_text.lower().replace('dt', '').replace('tnd', '').replace(' ', '').replace('&nbsp;', '').strip()
    clean = clean.replace(',', '.')
    clean = re.sub(r'[^\d.]', '', clean)
    try:
        return float(clean)
    except:
        return 0

class TunisiaTechMobileScraper:
    def __init__(self):
        self.output_file = r"c:\Users\USER\Documents\programmation\frontend\src\data\tunisiatech_mobiles.json"
        self.base_url = "https://tunisiatech.tn/25-smartphones-tunisie"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.products = []

    def save_data(self):
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(self.products)} products to {self.output_file}")

    def scrape(self):
        print(f"Starting scrape of {self.base_url}...")
        
        page = 1
        max_pages = 100 # Ensure we go deep
        seen_urls = set()

        while page <= max_pages:
            # Sort by price DESCENDING to get expensive phones first (if loop breaks)
            # url = f"{self.base_url}?page={page}&order=product.price.asc"
            url = f"{self.base_url}?page={page}&order=product.price.desc"
            print(f"Scraping Page {page}: {url}")
            
            try:
                response = requests.get(url, headers=self.headers, timeout=15)
                if response.status_code != 200:
                    print(f"Failed to fetch page {page}: {response.status_code}")
                    break
                
                # Check for redirect to page 1 or previous page (infinite loop protection)
                if response.url != url and "page=1" in response.url and page > 1:
                     print("Redirected to page 1. Stopping.")
                     break

                soup = BeautifulSoup(response.content, 'html.parser')
                items = soup.select('.product-miniature')

                if items:
                    # Debug print removed
                    pass

                new_items_count = 0
                for item in items:
                    try:
                        # --- STOCK CHECK ---
                        is_in_stock = False
                        
                        # Check 1: Class .available
                        if item.select(".available"):
                            is_in_stock = True
                        
                        # Check 2: Text content
                        if not is_in_stock:
                            avail_el = item.select_one(".product-availability")
                            if avail_el:
                                txt = avail_el.text.lower()
                                if "stock" in txt or "disponible" in txt or "arrivage" in txt:
                                    is_in_stock = True

                        if not is_in_stock:
                            # print("Skipped item: Not in stock")
                            continue

                        # Extract
                        title_el = item.select_one('.product-name a')
                        if not title_el:
                             title_el = item.select_one('.product-title a') # Fallback

                        price_el = item.select_one('.price')
                        img_el = item.select_one('.product-thumbnail img')
                        
                        if title_el and price_el:
                            title = title_el.text.strip()
                            link = title_el['href']
                            
                            # Skip accessories and non-smartphones
                            exclude_keywords = [
                                'etui', 'film', 'cable', 'ecouteur', 'écouteur', 'chargeur', 
                                'montre', 'watch', 'buds', 'kit', 'support', 'adaptateur',
                                'protection', 'silicone', 'coque', 'power bank', 'batterie',
                                'incassable'
                            ]
                            
                            t_lower = title.lower()
                            if any(x in t_lower for x in exclude_keywords):
                                # print(f"Skipped Access/Other: {title}")
                                continue
                            
                            price = clean_price(price_el.text)
                            
                            # Filter out very cheap feature phones / accessories (< 100 DT)
                            # Exception: keep if it explicitly says "smartphone" (though some cheap ones might not)
                            # But Itel 2163N is 42DT. Smartwatches can be 139DT.
                            # Safe bet: Exclude if price < 150 AND not "smartphone"? 
                            # Let's just rely on keywords + price floor for "garbage".
                            if price < 70: # Most feature phones and accessories are below this
                                continue

                            image = img_el.get('data-original') or img_el.get('data-full-size-image-url') or img_el.get('src') or ""
                            
                            print(f"Product found: {title} - {price}")

                            pid_match = re.search(r'/(\d+)-', link)
                            pid = f"tt-{pid_match.group(1)}" if pid_match else f"tt-{hash(link)}"

                            product = {
                                "id": pid,
                                "title": title,
                                "price": price,
                                "image": image,
                                "link": link,
                                "source": "TunisiaTech",
                                "category": "Smartphone",
                                "specs": { "raw": title }
                            }
                            
                            # Deduplicate by ID in the main list
                            if not any(p['id'] == pid for p in self.products):
                                self.products.append(product)
                                new_items_count += 1
                                print(f"  + Added: {title[:40]}... ({price} DT)")

                    except Exception as e:
                        pass
                
                # if new_items_count == 0 and page > 1:
                #      print("No new items found on this page. Stopping.")
                #      break
                pass

                self.save_data()

                # Pagination Check
                next_btn = soup.select_one("a.next.js-search-link")
                if not next_btn:
                    print("Last page reached.")
                    break
                
                page += 1
                time.sleep(1)

            except Exception as e:
                print(f"Error on page {page}: {e}")
                break

        print("Done!")

if __name__ == "__main__":
    scraper = TunisiaTechMobileScraper()
    scraper.scrape()

