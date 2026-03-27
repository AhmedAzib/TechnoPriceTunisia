from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--headless=new")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)
try:
    url = "https://www.mytek.tn/telephonie-tunisie/tablette-tactile.html"
    print(f"Loading {url}...")
    driver.get(url)
    time.sleep(5)
    
    with open("mytek_tablet_debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved mytek_tablet_debug.html")
    
    # Check selectors
    items = driver.find_elements("css selector", "li.product-item")
    print(f"Found {len(items)} items using li.product-item")
    
    items2 = driver.find_elements("css selector", "div.product-item")
    print(f"Found {len(items2)} items using div.product-item")

except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()
