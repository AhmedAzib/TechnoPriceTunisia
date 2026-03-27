from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from .base_scraper import BaseScraper
from .utils import clean_price, clean_text

class MytekScraper(BaseScraper):
    def __init__(self):
        super().__init__("Mytek", "frontend/src/data/mytek_new.json")
        self.urls = [
            "https://www.mytek.tn/informatique/ordinateurs-portables/pc-portable.html",
            "https://www.mytek.tn/informatique/ordinateurs-portables/pc-gamer.html",
            "https://www.mytek.tn/informatique/ordinateurs-portables/pc-portable-pro.html",
            "https://www.mytek.tn/informatique/ordinateurs-portables/mac.html",
            "https://www.mytek.tn/informatique/ordinateurs-portables/ultrabook.html",
            "https://www.mytek.tn/telephonie-mobile/smartphone-mobile/smartphone.html" 
        ]
        self.driver = None

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless=new')  # Disabled for Captcha solving
        options.add_argument('--start-maximized')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.page_load_strategy = 'eager'
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=options)

    def scrape(self):
        self.setup_driver()
        try:
            for base_url in self.urls:
                self.logger.info(f"Scraping Category: {base_url}")
                page = 1
                while True:
                    url = f"{base_url}?p={page}"
                    self.logger.info(f"Navigating to {url}")
                    try:
                        self.driver.get(url)
                    except TimeoutException:
                        self.logger.info("Page load timeout, stopping load...")
                        self.driver.execute_script("window.stop();")

                    try:
                        # Wait for the actual product links to appear, indicating the JS has populated the data
                        WebDriverWait(self.driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item-link"))
                        )
                        time.sleep(2) # Short sleep for DOM stability
                        
                        # User provided selector: "d-flex justify-content-center col-lg-3 col-md-4 col-sm-6 col-12 mb-4"
                        # We will use a CSS selector that matches this composite class string.
                        # Since class order might vary or have extra spaces, we can simply target elements that contain *all* these classes
                        # or just the most specific/unique combination.
                        # "col-lg-3.col-md-4.col-sm-6.col-12.mb-4" seems robust enough for a grid item.
                        # Let's try the full string literal if possible, or a robust CSS selector.
                        
                        # Constructing a safer CSS selector:
                        products = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'd-flex') and contains(@class, 'justify-content-center') and contains(@class, 'col-lg-3') and contains(@class, 'col-md-4') and contains(@class, 'col-sm-6') and contains(@class, 'col-12') and contains(@class, 'mb-4')]")
                        
                        if not products:
                             # Fallback to the user's exact string if the split approach fails for some reason, though XPath is safer.
                             self.logger.info("Retrying with exact class string match...")
                             products = self.driver.find_elements(By.CLASS_NAME, "d-flex.justify-content-center.col-lg-3.col-md-4.col-sm-6.col-12.mb-4".replace(" ", "."))
                        if not products:
                            self.logger.info("No products found (selector .product-item).")
                            break

                        self.logger.info(f"Found {len(products)} products on page {page}")
                        if len(products) > 0:
                            self.logger.info(f"First product HTML: {products[0].get_attribute('outerHTML')}")
                        
                        found_count = 0
                        for prod in products:
                            try:
                                title_elem = prod.find_element(By.CSS_SELECTOR, ".product-item-link")
                                price_elem = prod.find_element(By.CSS_SELECTOR, ".price")
                                
                                title = clean_text(title_elem.text)
                                link = title_elem.get_attribute("href")
                                price = clean_price(price_elem.text)
                                
                                image = ""
                                try:
                                    img_elem = prod.find_element(By.CSS_SELECTOR, ".product-image-photo")
                                    image = img_elem.get_attribute("src")
                                except: pass
                                
                                category = "Laptops"
                                if "smartphone" in base_url:
                                    category = "Smartphones"
                                elif "gamer" in base_url:
                                    category = "Laptops (Gamer)"
                                elif "mac" in base_url:
                                    category = "Laptops (Mac)"
                                
                                self.add_product({
                                    "title": title,
                                    "price": price,
                                    "link": link,
                                    "image": image,
                                    "source": "Mytek",
                                    "category": category
                                })
                                found_count += 1
                            except NoSuchElementException:
                                continue 
                            except Exception as e:
                                pass
                        
                        if found_count == 0:
                            self.logger.warning("Found elements but failed to extract data.")
                            with open("mytek_extraction_fail.html", "w", encoding="utf-8") as f:
                                f.write(self.driver.page_source)
                            break

                        # Check for next page
                        try:
                            # Mytek often hides 'next' in a list item
                            next_btn = self.driver.find_elements(By.CSS_SELECTOR, "li.pages-item-next")
                            if not next_btn:
                                 self.logger.info("No next button found.")
                                 break
                        except:
                             break
                        
                        page += 1
                        time.sleep(2) 

                    except TimeoutException:
                        self.logger.info("Timeout waiting for page to load.")
                        # Save debug HTML
                        try:
                            with open(f"mytek_debug_page_{page}.html", "w", encoding="utf-8") as f:
                                f.write(self.driver.page_source)
                            self.logger.info(f"Saved debug HTML to mytek_debug_page_{page}.html")
                        except Exception as e:
                            self.logger.error(f"Failed to save debug HTML: {e}")
                        break
                    except Exception as e:
                        self.logger.error(f"Error scraping Mytek page {page}: {e}")
                        break
        finally:
            if self.driver:
                self.driver.quit()
        
        self.save_data()

if __name__ == "__main__":
    scraper = MytekScraper()
    scraper.scrape()
