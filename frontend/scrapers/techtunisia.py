
from .base_scraper import BaseScraper
from .utils import clean_price, clean_text
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

class TechTunisiaScraper(BaseScraper):
    def __init__(self):
        super().__init__("TechTunisia", "frontend/src/data/techtunisia_products.json")
        self.url = "https://tunisiatech.tn/57-pc-portable"
        self.target_count = 25
        self.driver = None

    def setup_driver(self):
        options = Options()
        options.add_argument("--headless")
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
            
            # Wait for products to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".product-miniature"))
                )
            except:
                self.logger.error("Timeout waiting for products")
                break

            # Scroll to load images
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            product_elements = self.driver.find_elements(By.CSS_SELECTOR, ".product-miniature")
            self.logger.info(f"Found {len(product_elements)} products on page {page}")

            if not product_elements:
                break

            for el in product_elements:
                if len(products_collected) >= self.target_count:
                    break
                
                try:
                    # Check stock/availability
                    is_available = False
                    try:
                        # Check for .available class existence first
                        avail_elem = el.find_elements(By.CSS_SELECTOR, ".product-availability .available")
                        if avail_elem:
                            is_available = True
                            # Optional: check text content
                            text = avail_elem[0].get_attribute("textContent").strip().lower()
                            if "non" in text or "rupture" in text:
                                is_available = False
                    except:
                        pass

                    self.logger.info(f"Availability check: {is_available}")

                    if not is_available:
                        self.logger.info("Skipping product -> Not in stock")
                        continue

                    # Title
                    title_elem = el.find_element(By.CSS_SELECTOR, ".product-name a")
                    title = title_elem.text.strip()
                    link = title_elem.get_attribute("href")
                    
                    # Validate if it is a laptop
                    title_lower = title.lower()
                    excluded_keywords = ["souris", "clavier", "tapis", "sac", "housse", "refroidisseur", "support", "manette", "casque", "ecran", "imprimante"]
                    if any(kw in title_lower for kw in excluded_keywords):
                        self.logger.info(f"Skipping non-laptop: {title}")
                        continue
                        
                    # Price
                    price_elem = el.find_element(By.CSS_SELECTOR, ".product-price")
                    price_text = price_elem.text.strip()
                    price = clean_price(price_text)
                    
                    # Heuristic: Laptops usually > 300 TND
                    if price < 300:
                        self.logger.info(f"Skipping low price item (likely accessory): {title} ({price} TND)")
                        continue

                    # Image
                    try:
                        img_elem = el.find_element(By.CSS_SELECTOR, ".product-thumbnail img")
                        image = img_elem.get_attribute("data-original")
                        if not image:
                            image = img_elem.get_attribute("src")
                    except:
                        image = ""

                    product = {
                        "title": clean_text(title),
                        "price": price,
                        "link": link,
                        "image": image,
                        "source": "TunisiaTech",
                        "category": "Laptops"
                    }
                    
                    products_collected.append(product)
                    self.add_product(product)
                    self.logger.info(f"Added: {title[:30]}... ({price} TND)")

                except Exception as e:
                    self.logger.warning(f"Error extracting product: {e}")
                    continue
            
            if len(products_collected) >= self.target_count:
                break

            # Next Page
            try:
                next_btn = self.driver.find_element(By.CSS_SELECTOR, "a.next.js-search-link")
                if next_btn:
                    url_next = next_btn.get_attribute("href")
                    self.driver.get(url_next)
                    page += 1
                    time.sleep(2)
                else:
                    self.logger.info("No next page found.")
                    break
            except:
                self.logger.info("End of pages or next button not found.")
                break

        self.save_data()
        self.driver.quit()
