from .base_scraper import BaseScraper
from .utils import clean_price, clean_text
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

class TdiscountScraper(BaseScraper):
    def __init__(self):
        super().__init__("Tdiscount", "frontend/src/data/tdiscount_products.json")
        self.url = "https://tdiscount.tn/categorie-produit/informatique/pc-portable/"
        self.target_count = 50 
        self.driver = None

    def setup_driver(self):
        options = Options()
        options.add_argument("--headless") # User hates freezing, headless is smoother
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)

    def scrape(self):
        self.setup_driver()
        self.logger.info(f"Connecting to {self.url}")
        self.driver.get(self.url)
        
        products_collected = []
        page = 1
        
        while len(products_collected) < self.target_count:
            self.logger.info(f"Scraping page {page}...")
            
            # Wait for content
            try:
                # Wait for body first to ensure page load
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                # Check for cloudflare or captcha
                title = self.driver.title
                self.logger.info(f"Page Title: {title}")
                if "Just a moment" in title or "Attention" in title:
                    self.logger.warning("Blocked by anti-bot protection.")
                    break

                # Specific wait
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "li.product"))
                )
            except:
                self.logger.warning("Timeout waiting for specific product selector, attempting to parse anyway...")
                # Continue and see if find_elements picks up anything


            # Scroll to trigger lazy loading of images
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
            time.sleep(0.5)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 1.5);")
            time.sleep(0.5)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            # Find product items
            product_items = self.driver.find_elements(By.CSS_SELECTOR, "li.product")
            self.logger.info(f"Found {len(product_items)} items on page {page}")

            if not product_items:
                break

            for el in product_items:
                if len(products_collected) >= self.target_count:
                    break

                try:
                    # check for class 'instock' on the li element
                    classes = el.get_attribute("class")
                    if "instock" not in classes:
                        # User explicitly asked for "on stock computers", so we skip outofstock/backorder
                        self.logger.info("Skipping product -> Not in stock (class check)")
                        continue

                    # Title
                    title_elem = el.find_element(By.CSS_SELECTOR, ".woo-loop-product__title a")
                    title = title_elem.text.strip()
                    link = title_elem.get_attribute("href")
                    
                    # Image
                    image = ""
                    try:
                        img_elem = el.find_element(By.CSS_SELECTOR, ".mf-product-thumbnail img")
                        image = img_elem.get_attribute("data-lazy-src")
                        if not image:
                            image = img_elem.get_attribute("src")
                        # Filter placeholder
                        if "svg+xml" in image or "placeholder" in image:
                            # Try finding another source if possible, or skip
                            pass
                    except:
                        pass

                    # Price
                    # <span class="price"><span class="woocommerce-Price-amount amount"><bdi>2 999.0 ...
                    # Sometimes there is <ins> for sale price
                    try:
                        price_elem = el.find_element(By.CSS_SELECTOR, ".price")
                        # Prefer <ins> if exists
                        ins_prices = price_elem.find_elements(By.CSS_SELECTOR, "ins .woocommerce-Price-amount bdi")
                        if ins_prices:
                            price_text = ins_prices[0].text
                        else:
                            # Standard price
                            price_text = price_elem.find_element(By.CSS_SELECTOR, ".woocommerce-Price-amount bdi").text
                        
                        price = clean_price(price_text)
                    except:
                        self.logger.warning(f"Could not parse price for {title}")
                        continue

                    if price < 400: # Accessory filter
                        continue

                    product = {
                        "title": clean_text(title),
                        "price": price,
                        "link": link,
                        "image": image,
                        "source": "Tdiscount",
                        "category": "Laptops"
                    }

                    if product not in products_collected:
                        products_collected.append(product)
                        self.add_product(product)
                        self.logger.info(f"Added: {title[:30]}... ({price} TND)")

                except Exception as e:
                    # self.logger.warning(f"Error extracting item: {e}")
                    pass
            
            if len(products_collected) >= self.target_count:
                break

            # Pagination: "next" button
            # Usually: <a class="next page-numbers" href="...">
            try:
                next_btn = self.driver.find_elements(By.CSS_SELECTOR, "a.next.page-numbers")
                if next_btn:
                    url_next = next_btn[0].get_attribute("href")
                    self.logger.info(f"Navigating to next page: {url_next}")
                    self.driver.get(url_next)
                    page += 1
                    time.sleep(2)
                else:
                    self.logger.info("No next page found or end of list.")
                    break
            except:
                break

        self.save_data()
        self.driver.quit()
