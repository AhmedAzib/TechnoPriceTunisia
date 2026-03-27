import requests
from bs4 import BeautifulSoup
import json
import time

class LaptopRestorerBS4:
    def __init__(self):
        self.output_tn = "frontend/src/data/tunisianet_new.json"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
    def clean_price(self, price_str):
        if not price_str: return 0.0
        # Cleaning: Remove spaces, nbsp, currency
        clean = price_str.replace(',', '.').replace(' ', '').replace('\u00a0', '').replace('\u202f', '').replace('DT', '').replace('TND', '')
        clean = "".join([c for c in clean if c.isdigit() or c == '.'])
        try:
            return float(clean)
        except:
            return 0.0

    def scrape(self):
        print("Scraping Tunisianet LAPTOPS (BS4)...")
        base_url = "https://www.tunisianet.com.tn/702-ordinateur-portable"
        all_laptops = []
        
        for page in range(1, 51): # 50 pages max
            url = f"{base_url}?page={page}"
            print(f"Visiting {url}...")
            
            try:
                r = requests.get(url, headers=self.headers, timeout=15)
                if r.status_code != 200:
                    print(f"Failed to fetch {url} (Status {r.status_code})")
                    break
                    
                soup = BeautifulSoup(r.content, 'html.parser')
                products = soup.select(".product-miniature")
                count = len(products)
                print(f"Found {count} products on page {page}.")
                
                if count == 0:
                    print("No products found. Stopping.")
                    break
                    
                for p in products:
                    try:
                        title_el = p.select_one(".product-title a")
                        if not title_el: continue
                        title = title_el.get_text(strip=True)
                        link = title_el['href']
                        
                        price = 0.0
                        # Try standard price
                        price_el = p.select_one(".price")
                        if price_el:
                            price = self.clean_price(price_el.get_text(strip=True))
                            
                        # Try meta itemprop
                        if price == 0.0:
                            meta = p.select_one("span[itemprop='price']")
                            if meta and meta.has_attr('content'):
                                price = self.clean_price(meta['content'])
                        
                        img = ""
                        img_el = p.select_one("img")
                        if img_el:
                            img = img_el.get('src', '')
                            
                        item = {
                            "title": title,
                            "price": price,
                            "image": img,
                            "link": link,
                            "brand": "Unknown",
                            "stock": "En Stock"
                        }
                        all_laptops.append(item)
                    except Exception as e:
                        print(f"Error parsing item: {e}")
            
            except Exception as e:
                print(f"Request error: {e}")
                break
                
            time.sleep(1) # Be polite
            
            # Log progress
            if page % 10 == 0:
                print(f"Scraped {len(all_laptops)} so far...")

        print(f"Total Scraped: {len(all_laptops)}")
        return all_laptops

    def restore(self):
        laptops = self.scrape()
        if laptops:
            with open(self.output_tn, 'w', encoding='utf-8') as f:
                json.dump(laptops, f, indent=2, ensure_ascii=False)
            print(f"Restored {len(laptops)} laptops to {self.output_tn} with CORRECTED prices.")

if __name__ == "__main__":
    R = LaptopRestorerBS4()
    R.restore()
