
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
import re

class TechTunisiaFullScraper:
    def __init__(self):
        self.base_url = "https://tunisiatech.tn/57-pc-portable"
        self.output_file = "frontend/src/data/techtunisia_products.json"
        
    def clean_price(self, price_str):
        if not price_str: return 0.0
        # Remove currency and spaces, swap comma for dot
        clean = price_str.lower().replace('dt', '').replace('tnd', '').replace(' ', '').replace(',', '.')
        # Keep only digits and dot
        clean = re.sub(r'[^\d.]', '', clean)
        try:
            return float(clean)
        except:
            return 0.0

    def scrape(self):
        print("Starting TunisiaTech Full Scrape (Simple)...")
        
        options = Options()
        options.add_argument("--headless=new") 
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = webdriver.Chrome(options=options)
        
        all_products = []
        
        try:
            for page in range(1, 13):
                url = f"{self.base_url}?page={page}"
                print(f"Visiting Page {page}: {url}")
                driver.get(url)
                
                # Wait for products
                time.sleep(5) 
                
                # Target only the main product grid to avoid carousels
                # If .products container exists, use it. Otherwise exclude slick-cloned.
                # But to be safe, we just exclude slick-cloned or check parent.
                products = driver.find_elements(By.CSS_SELECTOR, ".product-miniature")
                print(f"Found {len(products)} products on page {page}.")
                
                if not products:
                    print(f"No products on page {page}, stopping.")
                    break
                    
                added_this_page = 0
                for i, p in enumerate(products):
                    try:
                        # Skip carousel clones
                        if "slick-cloned" in p.get_attribute("class"):
                            continue

                        # 1. Stock (Relaxed) - logic preserved
                        
                        # 2. Extract Data (UPDATED SELECTORS)
                        # Title: .product-name a (not h3.product-title)
                        try:
                            title_el = p.find_element(By.CSS_SELECTOR, ".product-name a")
                        except:
                            # Fallback
                            title_el = p.find_element(By.CSS_SELECTOR, "h3.product-title a")
                            
                        title = title_el.text.strip()
                        link = title_el.get_attribute("href")
                        
                        # Price
                        price_el = p.find_element(By.CSS_SELECTOR, ".product-price-and-shipping .price")
                        price = self.clean_price(price_el.text)
                        
                        # Image
                        img = ""
                        try:
                            img_el = p.find_element(By.CSS_SELECTOR, ".product-thumbnail img")
                            # Prioritize data-original (lazy load) then src
                            img = img_el.get_attribute("data-original") or img_el.get_attribute("src")
                        except: pass
                        
                        # Verify title matches "PC" or "Portable" or "Laptop" to avoid Washing Machines
                        # The user wants Laptops. 
                        # If the page 57-pc-portable contains washing machines, they might be in "Promo" carousel.
                        # We will strictly filter ONLY if we are sure, but let's at least log it.
                        if "machine" in title.lower() or "lave" in title.lower():
                            continue
                        
                        # No Filtering for now - User wanted "clean details" and "download them"
                        # Verify it's not empty title
                        if not title: continue
                        
                        all_products.append({
                            "title": title,
                            "price": price,
                            "image": img,
                            "link": link,
                            "stock": "En Stock",
                            "source": "TunisiaTech"
                        })
                        added_this_page += 1
                        
                    except Exception as e:
                        # print(f"Skipping item: {e}")
                        pass
                
                print(f"Added {added_this_page} items. Total so far: {len(all_products)}")
                
        except Exception as e:
            print(f"Global Error: {e}")
            
        finally:
            driver.quit()
            
        print(f"Scraping Complete. Found {len(all_products)} items.")
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        print(f"Saved to {self.output_file}")

if __name__ == "__main__":
    S = TechTunisiaFullScraper()
    S.scrape()
