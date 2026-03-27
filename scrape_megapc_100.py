import requests
from bs4 import BeautifulSoup
import json
import time

class MegaPCLaptopScraper:
    def __init__(self):
        self.base_url = "https://megapc.tn/shop/category/ordinateur-portable"
        self.output_file = "frontend/src/data/megapc_new.json"
        self.target_count = 100
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
    def clean_price(self, price_str):
        if not price_str: return 0.0
        clean = price_str.replace(' ', '').replace('DT', '').replace('TND', '').replace('dt', '').replace(',', '.')
        # Remove non-numeric/dot
        clean = "".join([c for c in clean if c.isdigit() or c == '.'])
        try:
            return float(clean)
        except:
            return 0.0

    def scrape(self):
        print(f"Scraping MegaPC Laptops (Target: {self.target_count})...")
        
        all_laptops = []
        page = 1
        
        while len(all_laptops) < self.target_count:
            url = f"{self.base_url}?page={page}"
            print(f"Visiting {url}...")
            
            try:
                r = requests.get(url, headers=self.headers, timeout=15)
                if r.status_code != 200:
                    print(f"Failed status {r.status_code}")
                    break
                    
                soup = BeautifulSoup(r.content, 'html.parser')
                
                # Selectors based on megapc_full.py
                articles = soup.select("article.product-card")
                if not articles:
                    print(f"No articles found on page {page}. (Maybe end of pagination?)")
                    # Try alternative selector if site changed?
                    # check for simple div products
                    break
                    
                print(f"Found {len(articles)} items on page {page}.")
                
                for art in articles:
                    if len(all_laptops) >= self.target_count: break
                    
                    try:
                        # Stock Check
                        # Look for badges
                        card_text = art.get_text(" ", strip=True).lower()
                        if "rupture" in card_text or "hors stock" in card_text:
                            # print("Skipping out of stock item")
                            continue
                            
                        # Title
                        title = art.get('title')
                        if not title:
                            t_el = art.select_one("p.text-skin-base")
                            if t_el: title = t_el.get_text(strip=True)
                        if not title: continue
                        
                        # Price
                        price = 0.0
                        p_el = art.select_one("span.text-skin-primary")
                        if p_el:
                            price = self.clean_price(p_el.get_text(strip=True))
                            
                        # Link
                        link = ""
                        a_el = art.select_one("a")
                        if a_el: link = a_el.get('href')
                        
                        # Image
                        img = ""
                        img_el = art.select_one("img")
                        if img_el:
                            img = img_el.get('src') or img_el.get('data-src') or ""
                            
                        # Dedupe check
                        if any(x['link'] == link for x in all_laptops):
                            continue
                            
                        item = {
                            "title": title,
                            "price": price,
                            "image": img,
                            "link": link,
                            "brand": "Unknown", # Normalized later
                            "stock": "En Stock"
                        }
                        
                        all_laptops.append(item)
                        # print(f" + {title[:30]} ({price})")
                        
                    except Exception as e:
                        pass
                
                page += 1
                time.sleep(1)
                
            except Exception as e:
                print(f"Error scraping: {e}")
                break
                
        print(f"Total Scraped: {len(all_laptops)}")
        
        if len(all_laptops) > 0:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(all_laptops, f, indent=2, ensure_ascii=False)
            print(f"Saved to {self.output_file}")
            
if __name__ == "__main__":
    S = MegaPCLaptopScraper()
    S.scrape()
