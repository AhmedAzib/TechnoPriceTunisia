
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--headless=new") 
options.add_argument("--window-size=1920,1080")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
driver = webdriver.Chrome(options=options)

try:
    url = "https://wiki.tn/smartphones"
    print(f"Connecting to {url}")
    driver.get(url)
    time.sleep(5)
    
    cards = driver.find_elements(By.CSS_SELECTOR, ".product-card--grid")
    if cards:
        print("Found cards. HTML of first card:")
        print(cards[0].get_attribute('innerHTML'))
        print("-" * 50)
        try:
            img = cards[0].find_element(By.CSS_SELECTOR, ".product-card__image img")
            print("Image Outer HTML:")
            print(img.get_attribute('outerHTML'))
        except:
             print("No image tag found in card.")
    else:
        print("No cards found.")

except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()
