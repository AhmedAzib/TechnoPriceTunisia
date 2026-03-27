
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

options = uc.ChromeOptions()
options.add_argument("--headless=new")
driver = uc.Chrome(options=options)

try:
    driver.get("https://tunisiatech.tn/57-pc-portable?page=1")
    time.sleep(5)
    
    # Try finding the product container
    products = driver.find_elements(By.CSS_SELECTOR, ".product-miniature")
    if products:
        p = products[0]
        html = p.get_attribute('outerHTML')
        with open("debug_product.txt", "w", encoding="utf-8") as f:
            f.write(html)
        print("Dumped product HTML to debug_product.txt")
    else:
        print("No .product-miniature found")
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

finally:
    driver.quit()
