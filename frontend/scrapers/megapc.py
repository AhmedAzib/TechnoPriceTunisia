from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
from .base_scraper import BaseScraper
from .utils import clean_price, clean_text

class MegaPCScraper(BaseScraper):
    def __init__(self):
        super().__init__("MegaPC", "frontend/src/data/megapc_new.json")
        self.urls = [
            "https://megapc.tn/shop/PC%20PORTABLE/MACBOOK",
            "https://megapc.tn/shop/PC%20PORTABLE/PC%20PORTABLE%20GAMER",
            "https://megapc.tn/shop/PC%20PORTABLE/PC%20PORTABLE%20PRO",
            "https://megapc.tn/shop/PC%20PORTABLE/FULL%20SETUP%20PC%20PORTABLE",
            "https://megapc.tn/shop/search?q=pc%20portable",
            "https://megapc.tn/shop/search?q=laptop",
            "https://megapc.tn/shop/search?q=msi",
            "https://megapc.tn/shop/search?q=asus",
            "https://megapc.tn/shop/search?q=lenovo",
            "https://megapc.tn/shop/search?q=hp",
            "https://megapc.tn/shop/search?q=dell",
            "https://megapc.tn/shop/quoi-de-neuf"
        ]
        self.driver = None
        self.seen_urls = set()

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new') 
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        self.driver = webdriver.Chrome(options=options)

    def is_valid_product(self, title, price):
        title_lower = title.lower()
        
        # 1. Price Check (Avoid cheap accessories)
        if price < 400:
            self.logger.warning(f"REJECTED (Price {price}): {title}")
            return False

        # 2. Hard Negative Keywords
        negative_keywords = [
            "smartphone", "téléphone", "telephone", "mobile", 
            "tablette", "tablet", "ipad", "hms", "android", "ios",
            "pc de bureau", "desktop", "all in one", "aio", "unité centrale",
            "imprimante", "printer", "serveur", "server", "projecteur",
            "playstation", "xbox", "console", "manette", "cartable", "souris"
        ]
        
        for bad_word in negative_keywords:
            if bad_word in title_lower:
                if "galaxy book" in title_lower:
                    pass
                else:
                    self.logger.warning(f"REJECTED (Keyword '{bad_word}'): {title}")
                    return False

        # 3. Positive Keywords
        positive_keywords = [
            "intel", "amd", "core", "ryzen", "celeron", "pentium", "athlon", 
            "apple m", "m1", "m2", "m3", "macbook", 
            "pc portable", "laptop", "notebook",
            "dell", "hp", "lenovo", "asus", "acer", "msi", "gigabyte", "samsung",
            "huawei", "infinix", "victus", "tuf", "rog", "ideapad", "thinkpad", "vostro", "latitude", "probook", "elitebook"
        ]
        
        has_positive = any(kw in title_lower for kw in positive_keywords)
        
        if not has_positive:
            if "ecran" in title_lower or "moniteur" in title_lower:
                self.logger.warning(f"REJECTED (Monitor presumed): {title}")
                return False
            # If high price but no positive keywords?
            if price > 1000:
                self.logger.warning(f"ACCEPTED (High Price Weak Keyword): {title}")
                return True
                
            self.logger.warning(f"REJECTED (No Positive Keyword): {title}")
            return False

        return True

    def scrape(self):
        self.setup_driver()
        try:
            for base_url in self.urls:
                self.logger.info(f"Scraping Category: {base_url}")
                self.driver.get(base_url)
                
                # Scroll to trigger lazy loading
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
                time.sleep(1)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                category = "Laptops"
                if "GAMER" in base_url:
                    category = "Laptops (Gamer)"
                elif "PRO" in base_url:
                    category = "Laptops (Pro)"

                page_count = 1
                while True:
                    self.logger.info(f"Processing page {page_count} of {category}")
                    
                    try:
                        # Improved Wait: Check for any images or product cards
                        WebDriverWait(self.driver, 15).until(
                            lambda d: len(d.find_elements(By.TAG_NAME, "img")) > 5
                        )
                        time.sleep(2) # Extra stability
                    except TimeoutException:
                        self.logger.info("Timeout waiting for content.")
                        pass # Continue anyway, maybe some loaded
                    
                    # 1. Find Products
                    products = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'group') and .//img]") 
                    if not products:
                         products = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/product/')]")
                         # If found as anchors, get parent if needed or use anchor itself
                    
                    self.logger.info(f"Found {len(products)} potential products on page")

                    found_on_page = 0
                    for prod in products:
                        try:
                            text_content = prod.text
                            if not text_content: continue

                            # Title Extraction
                            lines = text_content.split('\n')
                            badges = ["New", "Hors Stock", "Promo", "Rupture", "Commandez"]
                            title = "Unknown"
                            for line in lines:
                                if line.strip() not in badges and len(line) > 3:
                                    title = line
                                    break
                            
                            # Price Extraction
                            price_str = next((l for l in lines if 'DT' in l), "0")
                            price = clean_price(price_str)
                            
                            # Link Extraction
                            try:
                                link_elem = prod 
                                if prod.tag_name != 'a':
                                    link_elem = prod.find_element(By.TAG_NAME, "a")
                                link = link_elem.get_attribute("href")
                            except: link = ""
                            
                            # Image Extraction
                            try:
                                img_elem = prod.find_element(By.TAG_NAME, "img")
                                image = img_elem.get_attribute("src")
                            except: image = ""

                            if "data:image" in image:
                                continue

                            # VALIDATION
                            if not title or title == "Unknown": continue
                            if not link: continue
                            
                            # Deduplication check
                            if link in self.seen_urls:
                                continue
                            
                            if self.is_valid_product(title, price):
                                self.add_product({
                                    "title": clean_text(title),
                                    "price": price,
                                    "link": link,
                                    "image": image,
                                    "source": "MegaPC",
                                    "category": category
                                })
                                self.seen_urls.add(link)
                                found_on_page += 1
                        except Exception as e:
                            pass 
                    
                    self.logger.info(f"Successfully added {found_on_page} products from page {page_count}")

                    # Pagination
                    try:
                        # Try finding a next button (standard numeric or arrow)
                        # Specific to MegaPC: Button with aria-label or just Next
                        # Only click if we haven't seen "No next button"
                        
                        # Find all buttons
                        all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        next_btn = None
                        
                        for btn in all_buttons:
                            try:
                                txt = btn.text.strip()
                                # Check for "Next" or ">" or sequential number
                                if txt == str(page_count + 1) or ">" in txt or "Next" in btn.get_attribute("aria-label") or "Next" in btn.get_attribute("title"):
                                     next_btn = btn
                                     break
                                # Also check list items
                            except: continue

                        if not next_btn:
                             # Try li structure
                             next_btn_li = self.driver.find_elements(By.XPATH, "//li[contains(@title, 'Next Page')]/button")
                             if next_btn_li: next_btn = next_btn_li[0]

                        if next_btn and next_btn.is_enabled():
                            self.driver.execute_script("arguments[0].click();", next_btn)
                            page_count += 1
                            time.sleep(5)
                        else:
                            self.logger.info("No next button found (end of pages).")
                            break
                            
                    except Exception as e:
                        self.logger.info(f"Pagination error or end: {e}")
                        break
        finally:
            if self.driver:
                self.driver.quit()
        
        self.save_data()

if __name__ == "__main__":
    scraper = MegaPCScraper()
    scraper.scrape()
