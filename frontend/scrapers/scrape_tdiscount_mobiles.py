import json
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TdiscountMobileScraper:
    def __init__(self):
        self.base_url = "https://tdiscount.tn/categorie-produit/telephonie-tablette/smartphone-tunisie/"
        self.output_file = "../src/data/tdiscount_mobiles.json"
        self.min_page = 1
        self.max_page = 90
        # self.max_page = 2 # debug
        self.driver = None
        self.products = []

    def setup_driver(self):
        options = Options()
        options.add_argument("--headless=new") 
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)

    def clean_text(self, text):
        if not text: return ""
        return re.sub(r'\s+', ' ', text).strip()

    def clean_price(self, price_str):
        if not price_str: return 0.0
        # Remove TND, DT, spaces, non-breaking spaces
        clean_str = price_str.lower().replace('tnd', '').replace('dt', '').replace(' ', '').replace('\xa0', '').strip()
        # Replace comma with dot
        clean_str = clean_str.replace(',', '.')
        # Remove non-numeric chars except dot
        clean_str = re.sub(r'[^\d.]', '', clean_str)
        try:
            return float(clean_str)
        except:
            return 0.0

    def scrape(self):
        self.setup_driver()
        print(f"Starting Tdiscount Mobile Scraper (Pages {self.min_page}-{self.max_page})")
        
        try:
            for page in range(self.min_page, self.max_page + 1):
                url = f"{self.base_url}page/{page}/" if page > 1 else self.base_url
                print(f"Scraping Page {page}: {url}")
                
                try:
                    self.driver.get(url)
                    
                    # Cloudflare/Bot check
                    if "Just a moment" in self.driver.title:
                        print("Cloudflare detected! Waiting 10s...")
                        time.sleep(10)

                    # Scroll to trigger lazy loading
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
                    time.sleep(0.5)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/1.5);")
                    time.sleep(0.5)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)

                    # Check for products
                    cards = self.driver.find_elements(By.CSS_SELECTOR, "li.product")
                    
                    if not cards:
                        print(f"No products found on page {page}. Stopping.")
                        break

                    page_added = 0
                    for card in cards:
                        try:
                            # 1. STOCK CHECK - "only en stock ones"
                            # The 'li' class contains 'instock' or 'outofstock'
                            classes = card.get_attribute("class")
                            if "instock" not in classes:
                                # Skip if not strictly instock
                                continue 
                            
                            # 2. TITLE & LINK
                            title_elem = card.find_element(By.CSS_SELECTOR, ".woo-loop-product__title a")
                            title = self.clean_text(title_elem.text)
                            link = title_elem.get_attribute('href')
                            
                            # 3. PRICE
                            # Snippet: .price > ins > .amount OR .price > .amount
                            try:
                                # Try sale price first
                                ins_price = card.find_elements(By.CSS_SELECTOR, "ins .amount bdi")
                                if ins_price:
                                    price_text = ins_price[0].text
                                else:
                                    # Regular price
                                    price_text = card.find_element(By.CSS_SELECTOR, ".price .amount bdi").text
                                price = self.clean_price(price_text)
                            except:
                                price = 0.0
                                
                            # 4. IMAGE - BEST RESOLUTION
                            # Snippet: .mf-product-thumbnail img
                            # Attributes: src, data-lazy-src, data-lazy-srcset, srcset
                            # data-lazy-srcset="...img-300x300.jpg 300w, ...img.jpg 700w"
                            # We want the last one in srcset (usually highest res)
                            image_url = ""
                            try:
                                img_elem = card.find_element(By.CSS_SELECTOR, ".mf-product-thumbnail img")
                                
                                # Try srcset variants
                                srcset = img_elem.get_attribute('data-lazy-srcset') or img_elem.get_attribute('srcset')
                                
                                if srcset:
                                    # Parse srcset: "url1 size1, url2 size2"
                                    # Split by comma
                                    candidates = srcset.split(',')
                                    # Get the last candidate (usually biggest)
                                    best_cand = candidates[-1].strip()
                                    # Split "url size" -> get url
                                    image_url = best_cand.split(' ')[0]
                                else:
                                    # Fallback
                                    image_url = img_elem.get_attribute('data-lazy-src') or img_elem.get_attribute('src')

                                # Clean standard suffix just in case it picked a thumbnail
                                # e.g. name-300x300.jpg -> name.jpg
                                if image_url:
                                    image_url = re.sub(r'-\d+x\d+(\.\w+)$', r'\1', image_url)
                                    
                            except:
                                image_url = ""

                            # 5. ID (from link)
                            slug = link.strip('/').split('/')[-1]
                            prod_id = f"td-{slug}"

                            # 6. DETAILS (from snippet short description if available or title)
                            # User snippet shows short description is hidden in grid view usually? 
                            # Actually in the snippet: <div class="woocommerce-product-details__short-description">...</div>
                            # It might be visible.
                            description = ""
                            try:
                                desc_elem = card.find_element(By.CSS_SELECTOR, ".woocommerce-product-details__short-description")
                                description = self.clean_text(desc_elem.text)
                            except:
                                pass
                                
                            # REFERENCE? "Vendu par" is vendor.
                            vendor = "Tdiscount"
                            try:
                                vendor_elem = card.find_element(By.CSS_SELECTOR, ".sold-by-label + a")
                                vendor = vendor_elem.text.strip()
                            except:
                                pass

                            product = {
                                "id": prod_id,
                                "title": title,
                                "price": price,
                                "image": image_url,
                                "link": link,
                                "source": "Tdiscount", # Display name
                                "vendor": vendor,
                                "category": "Smartphone",
                                "description": description,
                                "specs": {
                                    "raw": f"{title} {description}"
                                }
                            }
                            
                            self.products.append(product)
                            page_added += 1

                        except Exception as e:
                            # print(f"Error extracting card: {e}")
                            continue
                            
                    print(f"  -> Added {page_added} items from page {page}")
                    
                    # Incremental Save
                    with open(self.output_file, 'w', encoding='utf-8') as f:
                        json.dump(self.products, f, indent=4, ensure_ascii=False)
                    # print(f"Saved progress ({len(self.products)} total) to {self.output_file}")
                    
                except Exception as e:
                    print(f"Error on page {page}: {e}")
                    
        finally:
            if self.driver:
                self.driver.quit()
            
            # Final Save
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.products, f, indent=4, ensure_ascii=False)
            print(f"Final Save: {len(self.products)} products to {self.output_file}")

if __name__ == "__main__":
    scraper = TdiscountMobileScraper()
    scraper.scrape()
