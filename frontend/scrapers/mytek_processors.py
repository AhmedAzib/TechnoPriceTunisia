from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from .base_scraper import BaseScraper
from .utils import clean_price, clean_text

class MytekProcessorsScraper(BaseScraper):
    def __init__(self):
        super().__init__("MytekProcessors", "frontend/src/data/mytek_processors.json")
        self.url = "https://www.mytek.tn/informatique/composants-informatique/processeur.html"
        self.driver = None

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.page_load_strategy = 'eager'
        # Disable images to speed up
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=options)

    def scrape(self):
        self.setup_driver()
        try:
            self.logger.info(f"Navigating to {self.url}")
            page = 1
            while True:
                url = f"{self.url}?p={page}"
                self.logger.info(f"Navigating to {url}")
                try:
                    self.driver.get(url)
                except TimeoutException:
                    self.logger.info("Page load timeout, stopping load...")
                    self.driver.execute_script("window.stop();")

                try:
                    # Wait for product links
                    WebDriverWait(self.driver, 25).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item-link"))
                    )
                    time.sleep(3) # Wait for text updates
                    
                    # Robust selector from mytek.py
                    products = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'd-flex') and contains(@class, 'justify-content-center') and contains(@class, 'col-lg-3') and contains(@class, 'col-md-4') and contains(@class, 'col-sm-6') and contains(@class, 'col-12') and contains(@class, 'mb-4')]")
                    
                    if not products:
                         self.logger.info("Retrying with exact class string match...")
                         products = self.driver.find_elements(By.CLASS_NAME, "d-flex.justify-content-center.col-lg-3.col-md-4.col-sm-6.col-12.mb-4".replace(" ", "."))
                    
                    if not products:
                        self.logger.info("No products found.")
                        break

                    self.logger.info(f"Found {len(products)} products on page {page}")
                    if len(products) > 0:
                        self.logger.info(f"First product HTML: {products[0].get_attribute('outerHTML')}")
                        self.logger.info(f"First product TEXT: {products[0].text}")

                    found_count = 0
                    for prod in products:
                        try:
                            title_elem = prod.find_element(By.CSS_SELECTOR, ".product-item-link")
                            price_elem = prod.find_element(By.CSS_SELECTOR, ".price")
                            title = clean_text(title_elem.text)
                            
                            # Stock Check Debugging
                            card_text = prod.text
                            # self.logger.info(f"Checking product: {title} - Text: {card_text[:50]}...") 
                            
                            is_in_stock = False
                            if "En stock" in card_text or "Disponible" in card_text:
                                is_in_stock = True
                            
                            # Log discarded items for debug if needed
                            if not is_in_stock:
                                # self.logger.info(f"Skipping out of stock item: {title}")
                                continue
                            
                            self.logger.info(f"Processing IN STOCK item: {title}")
                            link = title_elem.get_attribute("href")
                            price = clean_price(price_elem.text)
                            
                            image = ""
                            try:
                                img_elem = prod.find_element(By.CSS_SELECTOR, ".product-image-photo")
                                image = img_elem.get_attribute("src")
                            except: pass
                            
                            self.add_product({
                                "title": title,
                                "price": price,
                                "link": link,
                                "image": image,
                                "source": "Mytek",
                                "category": "Processors", 
                                "stock": "En stock"
                            })
                            found_count += 1
                        except Exception as e:
                            self.logger.error(f"Error extracting product '{title}' (Stock: {is_in_stock}): {e}")
                            pass
                    
                    self.logger.info(f"Extracted {found_count} 'En stock' items from page {page}")

                    if found_count == 0 and len(products) > 0:
                         self.logger.warning("Found products but none matched 'En stock' criteria.")

                    # Next page
                    next_btn = self.driver.find_elements(By.CSS_SELECTOR, "li.pages-item-next")
                    if not next_btn:
                        self.logger.info("No next button found.")
                        break
                    
                    page += 1
                    time.sleep(2)

                except TimeoutException:
                    self.logger.info("Timeout waiting for page content.")
                    break
                except Exception as e:
                    self.logger.error(f"Error scraping page {page}: {e}")
                    break
        finally:
            if self.driver:
                self.driver.quit()
        
        self.save_data()

if __name__ == "__main__":
    scraper = MytekProcessorsScraper()
    scraper.scrape()
