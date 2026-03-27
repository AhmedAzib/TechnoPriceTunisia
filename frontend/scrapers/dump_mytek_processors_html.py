from selenium import webdriver
from selenium.webdriver.common.by import By
import time

options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--start-maximized')

driver = webdriver.Chrome(options=options)

try:
    url = "https://www.mytek.tn/informatique/composants-informatique/processeur.html"
    print(f"Navigating to {url}...")
    driver.get(url)
    time.sleep(5) # Wait for JS to load
    
    # Scroll a bit
    driver.execute_script("window.scrollTo(0, 300);")
    time.sleep(2)

    with open("mytek_processors_debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved HTML to mytek_processors_debug.html")

except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()
