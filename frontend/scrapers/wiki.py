from .base_scraper import BaseScraper
from .utils import clean_price, clean_text
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

class WikiScraper(BaseScraper):
    def __init__(self):
        super().__init__("Wiki", "frontend/src/data/wiki_products.json")
        self.url = "https://wiki.tn/pc-portables"
        self.target_count = 30
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
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".product-card--grid"))
                )
            except:
                self.logger.error("Timeout waiting for products")
                break

            # Scroll to trigger lazy loading
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            product_elements = self.driver.find_elements(By.CSS_SELECTOR, ".product-card--grid")
            self.logger.info(f"Found {len(product_elements)} products on page {page}")

            if not product_elements:
                break

            for el in product_elements:
                if len(products_collected) >= self.target_count:
                    break
                
                try:
                    # Check stock/availability
                    # Based on snippet: <div class="brxe-doahjr brxe-shortcode stock-status-badge badge--small" ...>En Stock</div>
                    # Or: <div class="brxe-hphxjx brxe-shortcode brxe-shortcode-dispo" data-stock-status="instock">En Stock</div>
                    is_available = False
                    
                    try:
                        badges = el.find_elements(By.CSS_SELECTOR, ".stock-status-badge, .brxe-shortcode-dispo")
                        for badge in badges:
                            text = badge.text.strip().lower()
                            if "en stock" in text:
                                is_available = True
                                break
                            # specific check for data-stock-status
                            if badge.get_attribute("data-stock-status") == "instock":
                                is_available = True
                                break
                    except:
                        pass
                    
                    # Also check for "Out of stock" indicators if "En Stock" wasn't explicit
                    # Sometimes only "Out of stock" is explicitly marked
                    
                    if not is_available:
                        # Fallback: check if we can find any class saying 'instock'
                        if "instock" in el.get_attribute("innerHTML"):
                             is_available = True

                    if not is_available:
                        self.logger.info("Skipping product -> Not in stock")
                        continue

                    # Title
                    title_elem = el.find_element(By.CSS_SELECTOR, ".product-card__title a")
                    title = title_elem.text.strip()
                    link = title_elem.get_attribute("href")
                    
                    # Validate Laptop
                    title_lower = title.lower()
                    excluded_keywords = ["souris", "clavier", "tapis", "sac", "housse", "refroidisseur", "support", "manette", "casque", "ecran", "imprimante"]
                    if any(kw in title_lower for kw in excluded_keywords):
                        continue

                    # Price
                    price_elem = el.find_element(By.CSS_SELECTOR, ".product-card__price .woocommerce-Price-amount")
                    price_text = price_elem.text.strip()
                    price = clean_price(price_text)
                    
                    if price < 400: # Heuristic for accessories
                        continue

                    # Image
                    try:
                        img_elem = el.find_element(By.CSS_SELECTOR, ".product-card__image img")
                        image = img_elem.get_attribute("src")
                        # Try srcset/data-original if src is placeholder (often base64 or placeholder)
                        if "data:image" in image or "placeholder" in image:
                             srcset = img_elem.get_attribute("srcset")
                             if srcset:
                                 # Take the largest one (usually last)
                                 image = srcset.split(",")[-1].strip().split(" ")[0]
                    except:
                        image = ""

                    product = {
                        "title": clean_text(title),
                        "price": price,
                        "link": link,
                        "image": image,
                        "source": "Wiki",
                        "category": "Laptops"
                    }
                    
                    if product not in products_collected:
                        products_collected.append(product)
                        self.add_product(product)
                        self.logger.info(f"Added: {title[:30]}... ({price} TND)")

                except Exception as e:
                    self.logger.warning(f"Error extracting product: {e}")
                    continue
            
            if len(products_collected) >= self.target_count:
                break

            # Pagination
            # Try to find a 'next' button. 
            # Bricks builder often uses standard WP pagination
            try:
                next_btn = self.driver.find_elements(By.CSS_SELECTOR, "a.next, .pagination .next, a.page-numbers.next")
                if next_btn:
                    self.logger.info("Navigating to next page...")
                    self.driver.execute_script("arguments[0].click();", next_btn[0])
                    time.sleep(5)
                    page += 1
                else:
                    self.logger.info("No next page found.")
                    break
            except Exception as e:
                self.logger.info(f"Pagination error: {e}")
                break

        self.save_data()
        self.driver.quit()
