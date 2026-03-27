import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os
import re
import requests
from urllib.parse import urlparse

class TdiscountRedux:
    def __init__(self):
        self.url = "https://tdiscount.tn/categorie-produit/informatique/pc-portable/"
        self.output_file = "frontend/src/data/tdiscount_products.json"
        self.image_dir = "frontend/public/images/tdiscount"
        self.web_path_prefix = "/images/tdiscount"
        
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
            
        self.setup_driver()
        self.products = []

    def setup_driver(self):
        options = uc.ChromeOptions()
        # options.add_argument('--headless=new') # Headless might trigger CF more often, allow visible
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        
        self.driver = uc.Chrome(options=options)

    def clean_price(self, price_str):
        if not price_str: return 0.0
        # 1 409.0 DT
        clean = re.sub(r'[^\d.]', '', price_str.replace(' ', '').replace(',', '.'))
        try:
            return float(clean)
        except:
            return 0.0

    def get_base64_image(self, url):
        script = """
        var uri = arguments[0];
        var callback = arguments[1];
        var xhr = new XMLHttpRequest();
        xhr.responseType = 'blob';
        xhr.onload = function() {
          var reader = new FileReader();
          reader.onloadend = function() {
            callback(reader.result);
          }
          reader.readAsDataURL(xhr.response);
        };
        xhr.onerror = function() {
          callback(null);
        };
        xhr.open('GET', uri);
        xhr.send();
        """
        return self.driver.execute_async_script(script, url)

    def download_image(self, url, title):
        if not url or 'http' not in url:
            return ""
            
        try:
            # Generate filename
            path = urlparse(url).path
            ext = os.path.splitext(path)[1]
            if not ext or len(ext) > 5: ext = '.jpg'
            
            slug = re.sub(r'[^\w\s-]', '', title.lower())
            slug = re.sub(r'[\s_-]+', '-', slug)[:60]
            filename = f"{slug}{ext}"
            filepath = os.path.join(self.image_dir, filename)
            
            # Check if exists
            if os.path.exists(filepath):
                return f"{self.web_path_prefix}/{filename}"

            # Download via Selenium (Base64)
            print(f"Downloading {url} ...")
            base64_data = self.get_base64_image(url)
            
            if base64_data and ',' in base64_data:
                header, encoded = base64_data.split(',', 1)
                import base64
                data = base64.b64decode(encoded)
                with open(filepath, 'wb') as f:
                    f.write(data)
                return f"{self.web_path_prefix}/{filename}"
            else:
                print(f"Image download failed for {url}")
                return ""
                
        except Exception as e:
            print(f"Error downloading image: {e}")
            return ""

    def scrape(self):
        try:
            print("Connecting to Tdiscount...")
            self.driver.get(self.url)
            time.sleep(10) # Wait for Cloudflare
            
            # Check title
            if "Just a moment" in self.driver.title:
                print("Blocked by Cloudflare! Please solve CAPTCHA manually if visible.")
                time.sleep(10)
                
            page = 1
            while True:
                print(f"Scraping Page {page}...")
                
                # Wait for products
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "li.product"))
                    )
                except:
                    print("No products found or timeout.")
                    break
                
                # Scroll a bit
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
                time.sleep(2)
                
                items = self.driver.find_elements(By.CSS_SELECTOR, "li.product")
                print(f"Found {len(items)} items on page {page}")
                
                added_count = 0
                for el in items:
                    try:
                        # 1. Check Availability STRICTLY
                        # Class 'instock' is usually reliable in WooCommerce
                        classes = el.get_attribute("class")
                        if "instock" not in classes:
                            # Double check text just in case
                            if "Hors stock" in el.text:
                                continue
                            # If not explicitly instock, skip
                            continue
                            
                        # 2. Extract Data
                        title_el = el.find_element(By.CSS_SELECTOR, ".woo-loop-product__title a")
                        title = title_el.text.strip()
                        link = title_el.get_attribute("href")
                        
                        price_el = el.find_element(By.CSS_SELECTOR, ".price")
                        price = self.clean_price(price_el.text)
                        
                        # 3. Filter
                        if price < 400: # Skip accessories
                            continue

                        # 4. Image
                        try:
                            img_el = el.find_element(By.CSS_SELECTOR, ".mf-product-thumbnail img")
                            img_url = img_el.get_attribute("data-lazy-src")
                            if not img_url:
                                img_url = img_el.get_attribute("src")
                        except:
                            img_url = ""
                            
                        # Download Image
                        local_image = self.download_image(img_url, title)
                        
                        product = {
                            "title": title,
                            "price": price,
                            "link": link,
                            "image": local_image,
                            "source": "Tdiscount",
                            "category": "Laptops"
                        }
                        
                        self.products.append(product)
                        added_count += 1
                        print(f"  + {title[:30]}... ({price} TND)")
                        
                    except Exception as e:
                        # print(f"Error parsing item: {e}")
                        continue
                        
                print(f"Added {added_count} valid products from page {page}")
                
                # Save progress
                self.save()
                
                # Next Page
                try:
                    next_btn = self.driver.find_element(By.CSS_SELECTOR, "a.next.page-numbers")
                    url = next_btn.get_attribute("href")
                    self.driver.get(url)
                    page += 1
                    time.sleep(5)
                except:
                    print("No next page. Finished.")
                    break
                    
        except Exception as e:
            print(f"Fatal error: {e}")
        finally:
            self.driver.quit()

    def save(self):
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    scraper = TdiscountRedux()
    scraper.scrape()
