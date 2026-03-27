import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

def debug_spacenet():
    options = uc.ChromeOptions()
    # options.add_argument('--headless') 
    driver = uc.Chrome(options=options, version_main=143)
    
    url = "https://spacenet.tn/20-processeur"
    print(f"Navigating to {url}")
    driver.get(url)
    time.sleep(5)
    
    try:
        cards = driver.find_elements(By.CSS_SELECTOR, ".product-miniature")
        if cards:
            print(f"Found {len(cards)} cards.")
            first_card = cards[0]
            print("--- First Card Text ---")
            print(first_card.text)
            print("--- First Card HTML ---")
            print(first_card.get_attribute('outerHTML'))
        else:
            print("No cards found.")
            print("Page Source Preview:")
            print(driver.page_source[:2000])

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_spacenet()
