
import json
import time
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class WikiMobileScraper:
    def __init__(self):
        self.base_url = "https://wiki.tn/smartphones"
        self.output_file = "../src/data/wiki_mobiles.json"
        self.driver = None
        self.products = []
        self.max_pages = 12

    def setup_driver(self):
        options = Options()
        # options.add_argument("--headless") # Comment out for debugging if needed, but user wants result. 
        # Headless is safer for anti-bot sometimes, but real browser is better for cloudflare. 
        # Tdiscount required non-headless or undetectable. Wiki likely similar. 
        # Let's try standard headless first, if it fails we show window.
        options.add_argument("--headless=new") 
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)

    def clean_price(self, price_str):
        if not price_str:
            return 0.0
        # Remove TND, spaces, non-breaking spaces
        clean_str = price_str.lower().replace('tnd', '').replace('dt', '').replace(' ', '').replace('\xa0', '').strip()
        # Replace comma with dot
        clean_str = clean_str.replace(',', '.')
        # Remove any other non-numeric chars except dot
        clean_str = re.sub(r'[^\d.]', '', clean_str)
        try:
            return float(clean_str)
        except ValueError:
            return 0.0

    def clean_text(self, text):
        if not text:
            return ""
        # Remove strict non-ascii if needed, but French accents are important.
        # Just strip extra spaces.
        return re.sub(r'\s+', ' ', text).strip()

    def scrape(self):
        self.setup_driver()
        print(f"Connecting to {self.base_url}")
        
        try:
            for page in range(1, self.max_pages + 1):
                url = f"{self.base_url}/page/{page}/" if page > 1 else self.base_url
                print(f"Scraping Page {page}: {url}")
                
                self.driver.get(url)
                
                # Check for 403 or Cloudflare
                if "Just a moment" in self.driver.title:
                    print("Cloudflare detected! Waiting...")
                    time.sleep(10) # Simple wait
                
                # Wait for grid
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".product-card--grid, .products"))
                    )
                except:
                    print(f"Timeout waiting for products on page {page}")
                    break

                # Scroll for lazy load
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(1)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                # Selectors: Wiki seems to use Bricks builder or customized WC.
                # Based on wiki.py: .product-card--grid
                cards = self.driver.find_elements(By.CSS_SELECTOR, ".product-card--grid")
                
                if not cards:
                    print("No product cards found.")
                    # Debug: print page source subset
                    # print(self.driver.page_source[:500])
                    break
                
                page_added = 0
                for card in cards:
                    try:
                        # Stock Check - Strict "En Stock"
                        # Badges often: .stock-status-badge
                        # Text: "En stock"
                        
                        html_content = card.get_attribute('innerHTML').lower()
                        
                        # Check for specific "hors stock" class or text
                        if "hors stock" in html_content or "out of stock" in html_content:
                            continue

                        # Strict: Must have "en stock" or "instock"
                        if "en stock" not in html_content and "instock" not in html_content:
                            continue

                        # Extract Title
                        try:
                            title_elem = card.find_element(By.CSS_SELECTOR, ".product-card__title a")
                            title = self.clean_text(title_elem.text)
                            link = title_elem.get_attribute('href')
                        except:
                            continue # Skip if no title
                            
                        # Extract Price
                        try:
                            # Try sale price first, then regular
                            price_elem = card.find_element(By.CSS_SELECTOR, ".woocommerce-Price-amount")
                            # If multiple prices (sale), usually the last one is the current price? 
                            # Or check for 'ins' tag.
                            prices = card.find_elements(By.CSS_SELECTOR, ".woocommerce-Price-amount")
                            if prices:
                                # Usually the last price displayed is the effective one
                                price_text = prices[-1].text
                                price = self.clean_price(price_text)
                            else:
                                price = 0.0
                        except:
                            price = 0.0

                        # Extract Image
                        try:
                            img_elem = card.find_element(By.CSS_SELECTOR, ".product-card__image img")
                            
                            # Priority list for lazy loading attributes
                            candidates = [
                                img_elem.get_attribute('data-lazy-src'),
                                img_elem.get_attribute('data-lazy-srcset'),
                                img_elem.get_attribute('data-srcset'),
                                img_elem.get_attribute('srcset'),
                                img_elem.get_attribute('src')
                            ]
                            
                            image_url = ""
                            for cand in candidates:
                                if cand and "data:image" not in cand and "placeholder" not in cand:
                                    # If it's a srcset, take the last one (largest)
                                    if "," in cand:
                                        # srcset format: url width, url width
                                        # Split by comma
                                        parts = cand.split(',')
                                        # Take last part, strip, then take first part (url)
                                        image_url = parts[-1].strip().split(' ')[0]
                                    else:
                                        image_url = cand
                                    
                                    # Double check we didn't just extract a data URI from a broken srcset
                                    if "data:image" not in image_url:
                                        break
                                    else:
                                        image_url = "" # Reset if bad
                            
                            # Final fallback check
                            if not image_url or "data:image" in image_url:
                                # Try one more time with `src` but only if it's not data:
                                src_attr = img_elem.get_attribute('src')
                                if src_attr and "data:image" not in src_attr:
                                    image_url = src_attr
                                else:
                                    # If all else fails, leave empty or use a default placeholder if you want
                                    # But better empty than a huge SVG string
                                    image_url = ""
                                
                        except:
                            image_url = ""

                        # ID cleaning
                        # If post-id class missing, use slug from URL
                        classes = card.get_attribute('class')
                        match = re.search(r'post-(\d+)', classes)
                        if match:
                             prod_id = f"wk-{match.group(1)}"
                        else:
                             # Use slug from link
                             slug = link.strip('/').split('/')[-1]
                             prod_id = f"wk-{slug}"

                        product = {
                            "id": prod_id,
                            "title": title,
                            "price": price,
                            "image": image_url,
                            "link": link,
                            "source": "Wiki",
                            "category": "Smartphone",
                            "specs": {
                                "raw": title
                            }
                        }
                        
                        self.products.append(product)
                        page_added += 1

                    except Exception as e:
                        # print(f"Error card: {e}")
                        continue
                
                print(f"  -> Added {page_added} products from page {page}")
                self.save_data()
                
            print(f"Scraping completed. Total: {len(self.products)}")
            
        except Exception as e:
            print(f"Global Error: {e}")
        finally:
            if self.driver:
                self.driver.quit()

    def save_data(self):
        # Read existing to append or overwrite? User implies full scrape "page 1 to 12".
        # We will overwrite the file initially, then append in memory.
        # But here we just dump self.products which accumulates.
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    scraper = WikiMobileScraper()
    scraper.scrape()
