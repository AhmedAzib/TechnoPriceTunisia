import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def debug_wiki():
    print("Launching Undetected Selenium for Wiki...", flush=True)
    options = uc.ChromeOptions()
    # options.add_argument("--headless=new") # Try non-headless first to be safe, or headless if confident
    # Often UC works best non-headless initially or with specific headless flags. 
    # Let's try headless first but UC sometimes struggles with headless on some systems.
    # Given the user environment, I will try headless but standard UC.
    # options.add_argument("--headless=new")
    
    driver = uc.Chrome(options=options, version_main=143)
    
    try:
        url = "https://wiki.tn/processeur/"
        print(f"Navigating to {url}...", flush=True)
        driver.get(url)
        
        # Wait a bit longer for CF challenge to pass
        time.sleep(10)
        
        print(f"Title: {driver.title}")
        
        # Dump source just in case
        with open("debug_dump_uc.txt", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"Total links found: {len(links)}")
        
        prod_links = []
        for l in links:
            href = l.get_attribute('href')
            if href and ("/produit/" in href or "/processeur/" in href) and href not in prod_links:
                prod_links.append(href)
                
        print(f"Found {len(prod_links)} potential product links.")
        for l in prod_links[:10]:
            print(f" - {l}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_wiki()
