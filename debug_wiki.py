from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def debug_wiki():
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    
    # URL provided by user for context, picking a specific PDP if possible or listing
    # User gave examples: 4600G, 7950X
    # Let's try to list page first to get a link, then visit it.
    url = "https://wiki.tn/processeur/"
    print(f"Visiting {url}...")
    driver.get(url)
    time.sleep(5)
    
    try:
        with open("debug_dump.txt", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Dumped page source to debug_dump.txt")
        
        # Try finding ANY link with href
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"Total links found: {len(links)}")
        for i, l in enumerate(links[:20]):
            print(f"Link {i}: {l.get_attribute('href')}")
            print(f"Found Product: {pdp_url}")
            driver.get(pdp_url)
            time.sleep(5)
            
            # Inspect Specs
            print("\n--- PDP Body Text (First 1000 items) ---")
            print(driver.find_element(By.TAG_NAME, "body").text[:1000])
            
            print("\n--- Spec Elements search ---")
            # Look for specific keys mentioned by user to find container
            keys = ["Socket", "Nombre de cœurs", "Cache", "Horloge", "TDP"]
            found = False
            for k in keys:
                 try:
                     elem = driver.find_element(By.XPATH, f"//*[contains(text(), '{k}')]")
                     print(f"Found Key '{k}' in tag <{elem.tag_name}> class='{elem.get_attribute('class')}' parent=<{elem.find_element(By.XPATH, '..').tag_name}>")
                     found = True
                 except:
                     print(f"Key '{k}' not found via simple text search.")
            
        else:
            print("No products found on listing page.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_wiki()
