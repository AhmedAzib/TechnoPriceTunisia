import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

options = uc.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = uc.Chrome(options=options)
try:
    url = "https://megapc.tn/shop/COMPOSANTS/BARETTE%20M%C3%89MOIRE"
    driver.get(url)
    time.sleep(3)
    
    items = driver.find_elements(By.CSS_SELECTOR, ".border-gray-100")
    for el in items[:5]:
        try:
            img = el.find_element(By.TAG_NAME, "img")
            print("IMG HTML:", img.get_attribute('outerHTML'))
        except Exception as e:
            print(e)
finally:
    driver.quit()
