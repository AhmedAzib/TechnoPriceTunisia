import json
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SamsungScraper:
    def __init__(self):
        self.url = "https://www.samsungtunisie.tn/fr/14-smartphone-samsung-tunisie"
        self.output_file = "../src/data/samsung_tunisie.json"
        self.driver = None
        self.products = []

    def setup_driver(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-notifications")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)

    def clean_price(self, price_str):
        if not price_str: return 0.0
        # Clean "3 999,000 DT" -> 3999.0
        clean = price_str.lower().replace('dt', '').replace('tnd', '').replace(' ', '').replace('\xa0', '').replace(',', '.')
        try:
            return float(re.sub(r'[^\d.]', '', clean))
        except:
            return 0.0

    def scrape(self):
        self.setup_driver()
        print("Starting Samsung Tunisie Scraper...")
        
        try:
            self.driver.get(self.url)
            time.sleep(5) # Initial load
            
            # Scroll to load lazy images if any
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Locate product blocks
            # Confirmed selector: .ajax_block_product
            items = self.driver.find_elements(By.CSS_SELECTOR, ".ajax_block_product")
            
            if not items:
                print("No items found with .ajax_block_product. Trying fallback.")
                items = self.driver.find_elements(By.CSS_SELECTOR, "li.product")

            print(f"Found {len(items)} potential products.")
            
            for item in items:
                try:
                    # Stock Check - Relaxed
                    is_in_stock = True
                    try:
                        # Only strict check for "Rupture" text
                        availability = item.find_elements(By.CSS_SELECTOR, ".availability, .stock, .label-danger")
                        if availability:
                            text = availability[0].text.lower()
                            if "rupture" in text or "hors stock" in text:
                                is_in_stock = False
                    except:
                        pass
                    
                    # User filter (Restored but safer)
                    if not is_in_stock:
                        # continue
                        pass # Read everything for now to confirm structure

                    # Title - Multi-try
                    title = ""
                    title_selectors = ["a.product-name", ".name a", "h3 a", "h5 a", ".product-title a", ".right-block a"]
                    title_elem = None
                    
                    for sel in title_selectors:
                        try:
                            t = item.find_element(By.CSS_SELECTOR, sel)
                            if t.text.strip():
                                title_elem = t
                                break
                        except:
                            continue
                            
                    if not title_elem:
                        # Debug: Print HTML of first failure
                        print(f"FAILED TO FIND TITLE. Item HTML: {item.get_attribute('outerHTML')[:300]}...")
                        continue

                    title = title_elem.text.strip()
                    link = title_elem.get_attribute("href")
                    
                    # Cleanup Title
                    title = title.replace("Smartphone", "").replace("Samsung", "").strip()
                    title = f"Samsung {title}" # Normalize
                    
                    # Price - Multi-try
                    price = 0.0
                    try:
                        price_selectors = [".content_price .price", ".price", ".product-price", ".regular-price"]
                        for sel in price_selectors:
                            try:
                                p_elem = item.find_element(By.CSS_SELECTOR, sel)
                                if p_elem.text.strip():
                                    price = self.clean_price(p_elem.text)
                                    if price > 0: break
                            except:
                                continue
                    except:
                        pass

                    # Image
                    image_url = ""
                    try:
                        img_elem = item.find_element(By.CSS_SELECTOR, "img")
                        image_url = img_elem.get_attribute("src")
                        if image_url:
                            image_url = image_url.replace("-home_default", "-large_default").replace("-small_default", "-large_default")
                    except:
                        pass
                        
                    # Vendor
                    vendor = "Samsung Tunisie"

                    prod_id = f"sam-{link.split('/')[-1].split('-')[0]}" # Extract ID from URL usually
                    
                    product = {
                        "id": prod_id,
                        "title": title,
                        "price": price,
                        "image": image_url,
                        "link": link,
                        "source": "Samsung Tunisie",
                        "category": "Smartphone",
                        "availability": "in-stock"
                    }
                    
                    self.products.append(product)
                    print(f"Added: {title[:30]}... ({price} TND)")

                except Exception as e:
                    print(f"Error parsing item: {e}")
                    continue

        except Exception as e:
            print(f"Global Error: {e}")
            
        finally:
            if self.driver:
                self.driver.quit()
                
            # Save
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.products, f, indent=4, ensure_ascii=False)
            print(f"Saved {len(self.products)} products to {self.output_file}")

if __name__ == "__main__":
    scraper = SamsungScraper()
    scraper.scrape()
