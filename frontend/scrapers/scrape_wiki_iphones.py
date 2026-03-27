import json
import time
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class WikiIphoneScraper:
    def __init__(self):
        self.base_url = "https://wiki.tn/iphone"
        self.output_file = "../src/data/wiki_iphones.json"
        self.driver = None
        self.products = []
        self.max_pages = 5 # iPhones usually don't have many pages, assume 5 max
        
    def setup_driver(self):
        options = Options()
        # options.add_argument("--headless=new") # Run visible to be safe or headless if preferred
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)

    def clean_price(self, price_str):
        if not price_str: return 0.0
        clean_str = price_str.lower().replace('tnd', '').replace('dt', '').replace(' ', '').replace('\xa0', '').strip()
        clean_str = clean_str.replace(',', '.')
        clean_str = re.sub(r'[^\d.]', '', clean_str)
        try: return float(clean_str)
        except: return 0.0

    def clean_text(self, text):
        if not text: return ""
        return re.sub(r'\s+', ' ', text).strip()

    def scrape(self):
        self.setup_driver()
        print(f"Connecting to {self.base_url}")
        
        try:
            for page in range(1, self.max_pages + 1):
                url = f"{self.base_url}/page/{page}/" if page > 1 else self.base_url
                print(f"Scraping Page {page}: {url}")
                
                self.driver.get(url)
                
                if "Just a moment" in self.driver.title:
                    print("Cloudflare detected! Waiting...")
                    time.sleep(10)

                # Check if 404 or no products
                if "Page introuvable" in self.driver.title or len(self.driver.find_elements(By.CSS_SELECTOR, ".product-card")) == 0:
                    print("No more pages.")
                    break

                # Scroll
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(1)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                # HTML snippet provided uses .product-card
                cards = self.driver.find_elements(By.CSS_SELECTOR, ".product-card")
                
                if not cards:
                    print("No product cards found via .product-card selector.")
                    break
                
                page_added = 0
                for card in cards:
                    try:
                        # STOCKS CHECK
                        # User snippet: <div class="... stock-status-badge ...">En Stock</div>
                        # OR <div class="... stock-status-badge ...">En Arrivage</div>
                        try:
                            bg_elem = card.find_element(By.CSS_SELECTOR, ".stock-status-badge")
                            stock_text = bg_elem.text.lower()
                        except:
                            stock_text = ""
                        
                        # Fallback to card HTML
                        html_content = card.get_attribute('innerHTML').lower()
                        
                        is_in_stock = False
                        if "en stock" in stock_text or "en stock" in html_content:
                            is_in_stock = True
                        if "en arrivage" in stock_text or "en arrivage" in html_content:
                            is_in_stock = True
                        
                        # User requested "only en stock" initially but now wants others.
                        # "En Arrivage" is close enough. "Rupture" is not.
                        if not is_in_stock:
                            continue

                        # TITLE & LINK
                        # Snippet: .product-card__title a
                        title_elem = card.find_element(By.CSS_SELECTOR, ".product-card__title a")
                        title = self.clean_text(title_elem.text)
                        link = title_elem.get_attribute('href')
                        
                        # PRICE
                        # Snippet: .product-card__price ... ins amount bdi OR .price amount bdi
                        # Note: User snippet had <ins> for detailed price.
                        try:
                            # Try finding <ins> first (sale price)
                            ins_price = card.find_elements(By.CSS_SELECTOR, "ins .amount bdi")
                            if ins_price:
                                price_text = ins_price[0].text
                            else:
                                # Normal price
                                price_text = card.find_element(By.CSS_SELECTOR, ".price .amount bdi").text
                            price = self.clean_price(price_text)
                        except:
                            price = 0.0

                        # IMAGE
                        # Snippet: .product-card__image img
                        # Used data-lazy-src
                        try:
                            img_elem = card.find_element(By.CSS_SELECTOR, ".product-card__image img")
                            
                            candidates = [
                                img_elem.get_attribute('data-lazy-src'),
                                img_elem.get_attribute('data-lazy-srcset'),
                                img_elem.get_attribute('srcset'),
                                img_elem.get_attribute('src')
                            ]
                            
                            image_url = ""
                            for cand in candidates:
                                if cand and "data:image" not in cand:
                                    # Pick largest if srcset
                                    if "," in cand:
                                        parts = cand.split(',')
                                        # usually last is largest
                                        image_url = parts[-1].strip().split(' ')[0]
                                    else:
                                        image_url = cand
                                    break
                            
                            # Clean resolution suffix from the URL just in case
                            # e.g. -300x300.jpg -> .jpg
                            if image_url:
                                image_url = re.sub(r'-\d+x\d+(\.\w+)$', r'\1', image_url)

                        except:
                            image_url = ""

                        # ID
                        slug = link.strip('/').split('/')[-1]
                        prod_id = f"wk-iphone-{slug}"

                        product = {
                            "id": prod_id,
                            "title": title,
                            "price": price,
                            "image": image_url,
                            "link": link,
                            "source": "Wiki", # User wants "Wiki" source still
                            "category": "Smartphone",
                            "specs": {
                                "raw": title,
                                "cpu": "Apple A-Series", # Can infer later
                                "ram": "Unknown",
                                "storage": "Unknown" # Can infer from title later
                            }
                        }
                        
                        self.products.append(product)
                        page_added += 1

                    except Exception as e:
                        print(f"Error extracting card: {e}")
                        continue

                print(f"  -> Added {page_added} iPhones from page {page}")

        except Exception as e:
            print(f"Global Error: {e}")
        finally:
            if self.driver:
                self.driver.quit()
            
            # Save
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.products, f, indent=4, ensure_ascii=False)
            print(f"Saved {len(self.products)} iPhones to {self.output_file}")

if __name__ == "__main__":
    scraper = WikiIphoneScraper()
    scraper.scrape()
