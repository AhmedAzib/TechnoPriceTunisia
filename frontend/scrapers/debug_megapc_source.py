from selenium import webdriver
import time

options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

try:
    url = "https://megapc.tn/shop/search?q=pc%20portable"
    print(f"Getting {url}...")
    driver.get(url)
    time.sleep(5)
    
    with open("megapc_search_debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved megapc_search_debug.html")

finally:
    driver.quit()
