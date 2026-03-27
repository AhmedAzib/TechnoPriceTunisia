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

class SkymilRealScraper:
    def __init__(self):
        self.start_urls = [
            "https://skymil-informatique.com/pc-portable-gamer",
            "https://skymil-informatique.com/pc-portable-pro"
        ]
        self.output_file = "frontend/src/data/skymil_new.json"
        self.image_dir = "frontend/public/images/skymil"
        self.web_path_prefix = "/images/skymil"
        
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
        # "2 590,000 DT"
        clean = price_str.replace(' ', '').replace('DT', '').replace('TND', '').replace('dt', '')
        clean = clean.replace(',', '.')
        clean = re.sub(r'[^\d.]', '', clean)
        try:
            return float(clean)
        except:
            return 0.0

    def download_image(self, url, title):
        if not url or 'http' not in url: return ""
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
                print(f"Scraping category: {url}")
                self.driver.get(url)
                time.sleep(5)
                
                while True:
                    # Scroll
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                    time.sleep(2)
                    
                    # Skymil uses PrestaShop structure typically
                    # valid selectors: .product-miniature, .js-product-miniature
                    items = self.driver.find_elements(By.CSS_SELECTOR, ".product-miniature, .js-product-miniature")
                    print(f"Found {len(items)} items on page")
                    
                    for el in items:
                        try:
                            # Stock check
                            # Usually a badge .product-flag.out_of_stock or label
                            # "Rupture de stock"
                            text_all = el.text.lower()
                            if "rupture" in text_all:
                                continue
                                
                            # Title
                            title_el = el.find_element(By.CSS_SELECTOR, "h3.product-title a, .product-title a")
                            title = title_el.text.strip()
                            link = title_el.get_attribute("href")
                            
                            if link in self.seen_links: continue
                            
                            # Price
                            price_el = el.find_element(By.CSS_SELECTOR, ".price, .product-price")
                            price = self.clean_price(price_el.text)
                            
                            if price < 400: continue
                            
                            # Image
                            img_el = el.find_element(By.CSS_SELECTOR, "img")
                            img_url = img_el.get_attribute("data-full-size-image-url") or img_el.get_attribute("src")

                            local_img = self.download_image(img_url, title)
                            
                            p = {
                                "title": title,
                                "price": price,
                                "link": link,
                                "image": local_img,
                                "source": "Skymil",
                                "category": "Laptops"
                            }
                            self.products.append(p)
                            self.seen_links.add(link)
                            print(f" + {title[:20]}... {price} TND")

                        except Exception as e:
                            pass
                            
                    # Next Page
                    try:
                        next_btn = self.driver.find_element(By.CSS_SELECTOR, "a.next")
                        if next_btn:
                            href = next_btn.get_attribute("href")
                            self.driver.get(href)
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
    s = SkymilRealScraper()
    s.scrape()
