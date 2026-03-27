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

class MegaPCRealScraper:
    def __init__(self):
        self.start_urls = [
            "https://megapc.tn/shop/category/ordinateur-portable"
        ]
        self.output_file = "frontend/src/data/megapc_new.json"
        self.image_dir = "frontend/public/images/megapc"
        self.web_path_prefix = "/images/megapc"
        self.target_count = 100
        
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
            
        self.products = []
        self.seen_links = set()
        self.setup_driver()

    def setup_driver(self):
        options = uc.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        # options.add_argument("--headless=new") 
        self.driver = uc.Chrome(options=options)

    def clean_price(self, price_str):
        if not price_str: return 0.0
        # Format: "2 149,000 DT" or "2149 DT"
        clean = price_str.replace(' ', '').replace('DT', '').replace('TND', '').replace('dt', '')
        # Replace comma with dot
        clean = clean.replace(',', '.')
        # Remove any other non-digit char except dot
        clean = re.sub(r'[^\d.]', '', clean)
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
            path = urlparse(url).path
            ext = os.path.splitext(path)[1]
            if not ext or len(ext) > 5: ext = '.jpg'
            
            slug = re.sub(r'[^\w\s-]', '', title.lower())
            slug = re.sub(r'[\s_-]+', '-', slug)[:60]
            filename = f"{slug}{ext}"
            filepath = os.path.join(self.image_dir, filename)
            
            if os.path.exists(filepath):
                return f"{self.web_path_prefix}/{filename}"

            # Try Base64 first (better for protected images)
            b64 = self.get_base64_image(url)
            if b64 and ',' in b64:
                header, encoded = b64.split(',', 1)
                import base64
                data = base64.b64decode(encoded)
                with open(filepath, 'wb') as f:
                    f.write(data)
                return f"{self.web_path_prefix}/{filename}"
            
            # Fallback
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
                return f"{self.web_path_prefix}/{filename}"
            return ""
        except:
            return ""

    def scrape(self):
        try:
            for url in self.start_urls:
                print(f"Scraping {url}...")
                self.driver.get(url)
                time.sleep(5)
                
                while True:
                    # Scroll
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                    time.sleep(2)
                    
                    # Correct selectors from HTML analysis
                    # Container: article.product-card
                    items = self.driver.find_elements(By.CSS_SELECTOR, "article.product-card")
                    
                    print(f"Found {len(items)} items on page.")
                    
                    for el in items:
                        try:
                            # Title
                            title = el.get_attribute("title")
                            if not title:
                                title = el.find_element(By.CSS_SELECTOR, "p.text-skin-base").text.strip()
                            
                            # Link
                            link_el = el.find_element(By.TAG_NAME, "a")
                            link = link_el.get_attribute("href")
                            
                            if link in self.seen_links: continue
                            
                            # Price
                            # <span class="... text-skin-primary">2 099 DT</span>
                            try:
                                price_el = el.find_element(By.CSS_SELECTOR, "span.text-skin-primary")
                                price = self.clean_price(price_el.text)
                            except:
                                price = 0.0
                                
                            if price < 400: continue
                            
                            # Image
                            try:
                                img_el = el.find_element(By.TAG_NAME, "img")
                                img_url = img_el.get_attribute("src")
                                # If it's a data url or placeholder, try srcset or look for real one
                                if "placeholder" in img_url or "data:image" in img_url:
                                     # Try extracting from srcset if available
                                     srcset = img_el.get_attribute("srcset")
                                     if srcset:
                                         # Take the largest (last one)
                                         img_url = srcset.split(",")[-1].strip().split(" ")[0]
                            except:
                                img_url = ""

                            # Download
                            local_img = self.download_image(img_url, title)
                            
                            p = {
                                "title": title,
                                "price": price,
                                "link": link,
                                "image": local_img,
                                "source": "MegaPC",
                                "category": "Laptops"
                            }
                            self.products.append(p)
                            self.seen_links.add(link)
                            print(f" + {title[:20]} - {price} DT")
                            
                            if len(self.products) >= self.target_count:
                                return

                        except Exception as e:
                            continue
                            
                    # Next Page
                    try:
                        next_btn = self.driver.find_element(By.CSS_SELECTOR, "ul.pagination li.active + li a")
                        if next_btn:
                            url = next_btn.get_attribute("href")
                            self.driver.get(url)
                            time.sleep(5)
                        else:
                            break
                    except:
                        break
                        
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.products, f, indent=2, ensure_ascii=False)
                
        finally:
            self.driver.quit()

if __name__ == "__main__":
    s = MegaPCRealScraper()
    s.scrape()
