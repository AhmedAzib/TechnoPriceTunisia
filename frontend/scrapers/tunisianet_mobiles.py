
import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os

# --- UTILS ---
def clean_text(text):
    return text.strip().replace('\n', ' ').replace('\r', '')

def clean_price(price_text):
    # Remove 'DT', spaces, handle comma as decimal
    clean = price_text.lower().replace('dt', '').replace('tnd', '').replace(' ', '').replace('&nbsp;', '').strip()
    clean = clean.replace(',', '.')
    # Remove non-numeric except dot
    clean = re.sub(r'[^\d.]', '', clean)
    try:
        return float(clean)
    except:
        return 0

class TunisianetMobileScraper:
    def __init__(self):
        self.base_url = "https://www.tunisianet.com.tn/596-smartphone-tunisie"
        self.output_file = "tunisianet_mobiles.json"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.products = []

    def scrape(self):
        print(f"Starting scrape of {self.base_url}...")
        
        # Range 1 to 16 as requested
        for page in range(1, 17): 
            url = f"{self.base_url}?page={page}&order=product.price.asc"
            print(f"Scraping Page {page}/16: {url}")
            
            try:
                response = requests.get(url, headers=self.headers, timeout=15)
                if response.status_code != 200:
                    print(f"Failed to fetch page {page}: {response.status_code}")
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')
                items = soup.select('.product-miniature')

                if not items:
                    print("No products found on this page. Stopping.")
                    break

                for item in items:
                    try:
                        # Extract Details
                        title_el = item.select_one('.product-title a')
                        price_el = item.select_one('.price')
                        img_el = item.select_one('.product-thumbnail img')
                        
                        if title_el and price_el:
                            title = clean_text(title_el.text)
                            link = title_el['href']
                            price_raw = price_el.text
                            price = clean_price(price_raw)
                            image = img_el['src'] if img_el else ""
                            
                            # ID generation (simple hash or from link)
                            pid_match = re.search(r'/(\d+)-', link)
                            pid = f"tn-{pid_match.group(1)}" if pid_match else f"tn-{hash(link)}"

                            # Specs Extraction (Naive attempt from description if available, otherwise title)
                            desc_el = item.select_one('.product-description-short')
                            specs_text = clean_text(desc_el.text) if desc_el else ""

                            product = {
                                "id": pid,
                                "title": title,
                                "price": price,
                                "image": image,
                                "link": link,
                                "source": "Tunisianet",
                                "category": "Smartphone",
                                "specs": {
                                    "raw": specs_text # Keep raw text for normalization later
                                }
                            }
                            self.products.append(product)
                            print(f"  + Found: {title[:50]}... ({price} DT)")
                            
                    except Exception as e:
                        print(f"  ! Error extracting item: {e}")

                time.sleep(1) # Be polite

            except Exception as e:
                print(f"Error scraping page {page}: {e}")

        self.save()

    def save(self):
        print(f"Saving {len(self.products)} products to {self.output_file}...")
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, ensure_ascii=False, indent=2)
        print("Done!")

if __name__ == "__main__":
    scraper = TunisianetMobileScraper()
    scraper.scrape()
