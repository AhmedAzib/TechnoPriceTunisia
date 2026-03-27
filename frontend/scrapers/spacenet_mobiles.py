
import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re

class SpaceNetScraper:
    def __init__(self):
        self.base_url = "https://spacenet.tn/130-smartphone-tunisie"
        self.output_file = "../src/data/spacenet_mobiles.json"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        self.products = []
        self.existing_data = []
        self.load_existing_data()

    def load_existing_data(self):
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    self.existing_data = json.load(f)
                    print(f"Loaded {len(self.existing_data)} existing products.")
            except json.JSONDecodeError:
                self.existing_data = []

    def save_data(self):
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(self.products)} products to {self.output_file}")

    def clean_price(self, price_str):
        if not price_str:
            return 0.0
        # Remove DT, spaces, non-breaking spaces
        clean_str = price_str.lower().replace('dt', '').replace(' ', '').replace('\xa0', '').strip()
        # Replace comma with dot
        clean_str = clean_str.replace(',', '.')
        # Remove any other non-numeric chars except dot
        clean_str = re.sub(r'[^\d.]', '', clean_str)
        try:
            return float(clean_str)
        except ValueError:
            return 0.0

    def is_smartphone(self, title):
        title_lower = title.lower()
        exclude_keywords = [
            'montre', 'watch', 'bracelet', 'ecouteur', 'écouteur', 'buds', 'kit', 
            'étui', 'etui', 'coque', 'film', 'protection', 'cable', 'câble', 
            'chargeur', 'support', 'adaptateur', 'batterie', 'power bank', 
            'tablette', 'tab', 'ipad'
        ]
        
        for keyword in exclude_keywords:
            if keyword in title_lower:
                return False
        return True

    def scrape(self):
        max_pages = 17
        
        for page in range(1, max_pages + 1):
            url = f"{self.base_url}?page={page}"
            print(f"Scraping Page {page}: {url}")
            
            try:
                response = requests.get(url, headers=self.headers, timeout=15)
                if response.status_code != 200:
                    print(f"Failed to fetch page {page}. Status: {response.status_code}")
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')
                product_cards = soup.select('.product-miniature')
                
                if not product_cards:
                    print("No products found on this page.")
                    break

                page_new_count = 0
                
                for card in product_cards:
                    try:
                        # Stock Check - Strict "En stock"
                        stock_label = card.select_one('.product-quantities label')
                        if not stock_label:
                            # print("Skipping - No stock label")
                            continue
                            
                        stock_text = stock_label.get_text(strip=True).lower()
                        if "en stock" not in stock_text:
                            # print(f"Skipping - Not in stock: {stock_text}")
                            continue

                        # Extract Title
                        title_elem = card.select_one('.product_name a')
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        link = title_elem['href']
                        
                        # Filter non-smartphones
                        if not self.is_smartphone(title):
                            # print(f"Skipping non-smartphone: {title}")
                            continue

                        # Extract Price
                        price_elem = card.select_one('.price')
                        price = self.clean_price(price_elem.get_text(strip=True)) if price_elem else 0.0

                        # Extract Image
                        image_elem = card.select_one('.cover_image img')
                        image_url = ""
                        if image_elem:
                            image_url = image_elem.get('src', '')

                        # Create Product Object
                        product = {
                            "id": f"sn-{card.get('data-id-product', 'unknown')}",
                            "title": title,
                            "price": price,
                            "image": image_url,
                            "link": link,
                            "source": "SpaceNet",
                            "category": "Smartphone",
                            "specs": {
                                "raw": title # Will be parsed by frontend
                            }
                        }
                        
                        self.products.append(product)
                        page_new_count += 1
                        
                    except Exception as e:
                        print(f"Error extracting product: {e}")
                        continue

                print(f"  -> Added {page_new_count} products from page {page}")
                
                # Incremental Save
                self.save_data()
                
                # Be nice to the server
                time.sleep(1)

            except Exception as e:
                print(f"Error scrapping page {page}: {e}")

        print(f"Scraping completed. Total products: {len(self.products)}")

if __name__ == "__main__":
    scraper = SpaceNetScraper()
    scraper.scrape()
