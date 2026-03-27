import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import re

def clean_price(price_str):
    if not price_str: return 0.0
    # Normalize spaces
    s = price_str.replace(' ', '').replace(u'\xa0', '')
    
    # Regex to find the first valid price-like number
    # Supports: 123,456 or 123.456 or 123
    match = re.search(r'(\d+(?:[.,]\d+)?)', s)
    if match:
        val_str = match.group(1)
        # Fix comma to dot
        val_str = val_str.replace(',', '.')
        try:
            return float(val_str)
        except:
             return 0.0
    return 0.0

def get_driver():
    try:
        options = uc.ChromeOptions()
        driver = uc.Chrome(options=options)
    except:
        options = uc.ChromeOptions()
        driver = uc.Chrome(options=options, version_main=143)
    return driver

def debug():
    driver = get_driver()
    try:
        # Check specific high-value items
        urls = [
            "https://spacenet.tn/cartes-meres/94389-carte-mere-asus-rog-strix-b850-f-gaming-wifi-am5.html", # ~1039 DT
            "https://spacenet.tn/carte-mere/56413-carte-mere-asus-rog-maximus-z790-hero-ddr4-lga-1700.html" # ~2289 DT
        ]
        
        for url in urls:
            print(f"\nChecking: {url}")
            driver.get(url)
            time.sleep(3)
            
            try:
                price_el = driver.find_element(By.CSS_SELECTOR, ".current-price")
                print(f"Price Element Text: '{price_el.text}'")
                print(f"Price Element HTML: '{price_el.get_attribute('outerHTML')}'")
                
                try:
                    meta_price = price_el.find_element(By.CSS_SELECTOR, "[itemprop='price']")
                    print(f"Meta Price Content: '{meta_price.get_attribute('content')}'")
                except:
                    print("Meta price not found")
                    
                cleaned = clean_price(price_el.text)
                print(f"Cleaned Price: {cleaned}")
                
            except Exception as e:
                print(f"Error extracting price: {e}")
                
    finally:
        driver.quit()

if __name__ == "__main__":
    debug()
