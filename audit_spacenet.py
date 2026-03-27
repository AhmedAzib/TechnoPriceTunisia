import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import random

BASE_URL = "https://spacenet.tn/20-processeur"

def log(msg):
    print(msg, flush=True)

def audit():
    log("Initializing Audit (Safety Mode)...")
    options = uc.ChromeOptions()
    # options.add_argument('--headless')
    driver = uc.Chrome(options=options, version_main=143)
    
    total_found = 0
    total_in_stock = 0
    total_out_stock = 0
    
    try:
        for page in range(1, 10):
            url = f"{BASE_URL}?page={page}"
            log(f"Checking Page {page}...")
            driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            cards = driver.find_elements(By.CSS_SELECTOR, ".product-miniature")
            if not cards:
                log("No cards found. End of list.")
                break
                
            page_stock = 0
            page_out = 0
            
            for card in cards:
                stock_stat = "Unknown"
                # Check flags
                try:
                    flags = card.find_elements(By.CSS_SELECTOR, ".product-flags li")
                    is_stock = False
                    is_rupture = False
                    
                    for flag in flags:
                        txt = flag.text.lower()
                        if "stock" in txt: is_stock = True
                        if "rupture" in txt or "épuisé" in txt: is_rupture = True
                    
                    if is_stock: stock_stat = "In Stock"
                    elif is_rupture: stock_stat = "Out of Stock"
                    
                    # Fallback to qty
                    if stock_stat == "Unknown":
                        try:
                            q = card.find_element(By.CSS_SELECTOR, ".product-quantities").text.lower()
                            if "stock" in q: stock_stat = "In Stock"
                            else: stock_stat = "Out of Stock" # Assumption if no stock text
                        except:
                             stock_stat = "Out of Stock"
                    
                    if stock_stat == "In Stock":
                        page_stock += 1
                        # log(f"  + Found Stock: {card.find_element(By.CSS_SELECTOR, '.product-title').text[:30]}")
                    else:
                        page_out += 1
                        
                except:
                    page_out += 1
                    
            log(f"Page {page}: Total {len(cards)} | In Stock: {page_stock} | Out of Stock: {page_out}")
            total_found += len(cards)
            total_in_stock += page_stock
            total_out_stock += page_out
            
        log("--- AUDIT RESULTS ---")
        log(f"Total Products Scanned: {total_found}")
        log(f"Total In Stock: {total_in_stock}")
        log(f"Total Out of Stock: {total_out_stock}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    audit()
