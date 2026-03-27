
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_one_product():
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Try using a real User-Agent just in case
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')

    driver = uc.Chrome(options=options)
    
    url = "https://www.mytek.tn/gigabyte-g6-kf-pc-portable-gamer-i7.html"
    print(f"Navigating to {url}")
    
    try:
        driver.get(url)
        
        # Wait for price
        print("Waiting for price element...")
        try:
             # Try standard Magento/MyTek price selector
             # Look for 'price-final_price' or 'price-wrapper' inside 'product-info-price'
             element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".product-info-price .price"))
             )
             print("Price element found!")
        except Exception as e:
             print("Timeout waiting for price.")
             with open("selenium_product_debug.html", "w", encoding="utf-8") as f:
                 f.write(driver.page_source)
             print("Saved debug HTML.")
        
        # Extract Data
        try:
            title = driver.find_element(By.CSS_SELECTOR, "h1.page-title").text.strip()
            price = driver.find_element(By.CSS_SELECTOR, ".product-info-price .price").text.strip()
            # Image: usually .gallery-placeholder__image or .fotorama__img
            # But let's just get the main one
            
            print(f"Title: {title}")
            print(f"Price: {price}")
            
        except Exception as e:
            print(f"Extraction Error: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_one_product()
