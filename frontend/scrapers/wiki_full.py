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

class WikiRedux:
    def __init__(self):
        self.url = "https://wiki.tn/pc-portables/"
        self.output_file = "frontend/src/data/wiki_products.json"
        self.image_dir = "frontend/public/images/wiki"
        self.web_path_prefix = "/images/wiki"
        self.target_count = 100 # Adjust target as needed
        
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
            
        self.setup_driver()
        self.products = []

    def setup_driver(self):
        options = uc.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        # options.add_argument("--headless=new")
        self.driver = uc.Chrome(options=options)

    def clean_price(self, price_str):
        if not price_str: return 0.0
        # Format: "1 259,000 TND" or "999,000 DT"
        # 1. Replace comma with dot
        clean = price_str.replace(',', '.')
        # 2. Keep only digits and dot
        clean = re.sub(r'[^\d.]', '', clean)
        try:
            val = float(clean)
            # If 1259.000 -> 1259.0
            # If scraped as 1259000 (because dot was ignored), fix it
            # But here we kept the dot.
            return val
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

            # Download
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
                # Fallback to requests
                headers = { "User-Agent": "Mozilla/5.0" }
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(resp.content)
                    return f"{self.web_path_prefix}/{filename}"
                print(f"Image download failed for {url}")
                return ""
                
        except Exception as e:
            print(f"Error downloading image: {e}")
            return ""

    def scrape(self):
        try:
            print("Connecting to Wiki.tn...")
            self.driver.get(self.url)
            time.sleep(5)
            
            page = 1
            while len(self.products) < self.target_count:
                print(f"Scraping Page {page}...")
                
                # Check for product grid
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "li.product")) # WooCommerce standard
                    )
                except:
                    # Try alternative selector if standard fails
                    print("Waiting for products...")
                
                # Scroll
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
                time.sleep(2)
                
                # Wiki typically involves "li.product" or similar
                items = self.driver.find_elements(By.CSS_SELECTOR, "li.product")
                print(f"Found {len(items)} items on page {page}")
                
                if not items:
                    print("No products found.")
                    # Try bricks builder selector fallback
                    items = self.driver.find_elements(By.CSS_SELECTOR, ".product-card--grid")
                    print(f"Retrying with Bricks selector: {len(items)} items")

                if not items:
                    print("Still no items. Exiting.")
                    break

                for el in items:
                    try:
                        # 1. Availability Check
                        # Check usually visually "En stock" badge or absence of "Rupture"
                        text_content = el.text.lower()
                        
                        is_out_of_stock = "rupture" in text_content or "hors stock" in text_content or "out of stock" in text_content
                        is_instock = "en stock" in text_content or "instock" in el.get_attribute("class")
                        
                        # Some sites don't say "En stock" explicitly but only mark "Rupture".
                        # However user wants strict check.
                        
                        if is_out_of_stock:
                            continue
                        
                        # If strict 'En stock' is required:
                        # if not is_instock and not is_out_of_stock: 
                        #    # ambiguous case
                        #    pass
                        
                        # 2. Extract Data
                        # 2. Extract Data
                        try:
                            # Try Standard WooCommerce
                            title_el = el.find_element(By.CSS_SELECTOR, ".product-title a, .woocommerce-loop-product__title a")
                            title = title_el.text.strip()
                            link = title_el.get_attribute("href")
                        except:
                            try:
                                # Try Bricks specific
                                title_el = el.find_element(By.CSS_SELECTOR, "h3.brxe-heading a")
                                title = title_el.text.strip()
                                link = title_el.get_attribute("href")
                            except:
                                # Final fallback
                                link_el = el.find_element(By.TAG_NAME, "a")
                                link = link_el.get_attribute("href")
                                # Use accessible name or text content
                                title = link_el.get_attribute("aria-label") or link_el.text.strip()
                                if not title:
                                    # Try finding any heading inside
                                    try:
                                        h_el = el.find_element(By.TAG_NAME, "h3")
                                        title = h_el.text.strip()
                                    except:
                                        pass
                        
                        if not title:
                            # Skip if no title found
                            print("Skipping item with no title")
                            continue

                        try:
                            price_el = el.find_element(By.CSS_SELECTOR, ".price")
                            price = self.clean_price(price_el.text)
                        except:
                            price = 0.0

                        # 3. Filter
                        if price < 400: continue
                        if "imprimante" in title.lower(): continue # basic filter

                        # 4. Image
                        try:
                            img_el = el.find_element(By.CSS_SELECTOR, "img")
                            img_url = img_el.get_attribute("data-lazy-src") or img_el.get_attribute("src")
                        except:
                            img_url = ""

                        # Download
                        local_image = self.download_image(img_url, title)

                        product = {
                            "title": title,
                            "price": price,
                            "link": link,
                            "image": local_image,
                            "source": "Wiki",
                            "category": "Laptops"
                        }

                        # Uniqueness check
                        if not any(p['link'] == link for p in self.products):
                            self.products.append(product)
                            print(f"  + {title[:30]}... ({price} TND)")

                    except Exception as e:
                        # print(f"Error item: {e}")
                        continue
                
                # Save Periodically
                self.save()

                if len(self.products) >= self.target_count:
                    break

                # Next Page
                try:
                    next_btn = self.driver.find_element(By.CSS_SELECTOR, "a.next.page-numbers")
                    url = next_btn.get_attribute("href")
                    self.driver.get(url)
                    page += 1
                    time.sleep(5)
                except:
                   print("No next page button.")
                   break

        except Exception as e:
            print(f"Fatal: {e}")
        finally:
            self.driver.quit()

    def save(self):
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    scraper = WikiRedux()
    scraper.scrape()
