import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import os

def diagnose():
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    driver = uc.Chrome(options=options, version_main=143)
    
    try:
        url = "https://spacenet.tn/20-processeur"
        print(f"Opening {url}...")
        driver.get(url)
        time.sleep(10) # Give it plenty of time to load
        
        cards = driver.find_elements(By.CSS_SELECTOR, "article.product-miniature")
        if not cards:
            # Try a broader selector if article.product-miniature fails
            cards = driver.find_elements(By.CSS_SELECTOR, ".product-miniature")
            
        if cards:
            print(f"Found {len(cards)} cards.")
            html_content = cards[0].get_attribute('outerHTML')
            with open("spacenet_sample.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("Successfully saved spacenet_sample.html")
        else:
            print("No product cards found. Saving full page source to debug_page.html")
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
                
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    diagnose()
