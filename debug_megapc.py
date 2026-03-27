import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

def debug_megapc():
    options = uc.ChromeOptions()
    options.add_argument("--disable-gpu")
    driver = uc.Chrome(options=options)
    
    # Try probable laptop URL
    url = "https://megapc.tn/shop/category/ordinateur-portable"
    
    try:
        driver.get(url)
        time.sleep(5)
        print(f"Title: {driver.title}")
        print(f"URL: {driver.current_url}")
        
        products = driver.find_elements(By.CSS_SELECTOR, ".product-card, .product-item")
        print(f"Found {len(products)} products.")
        
        if products:
            p = products[0]
            print(p.get_attribute("outerHTML"))
        else:
            print("No products found with common selectors.")
            # Dump body to see structure
            body = driver.find_element(By.TAG_NAME, "body")
            print(body.get_attribute("outerHTML")[:2000]) # First 2000 chars checking for classes
            
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_megapc()
