import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import re
import sys

def clean_price(price_str):
    if not price_str: return 0.0
    clean = re.sub(r'[^\d,]', '', price_str).replace(',', '.')
    try: return float(clean)
    except: return 0.0

def debug():
    print("Starting debug script...", flush=True)
    options = uc.ChromeOptions()
    # options.add_argument('--headless')
    try:
        # Auto detect version
        driver = uc.Chrome(options=options)
    except Exception as e:
        print(f"Error initializing driver: {e}", flush=True)
        return

    try:
        url = "https://spacenet.tn/22-carte-mere"
        print(f"Visiting {url}...", flush=True)
        driver.get(url)
        time.sleep(5)
        
        links = driver.find_elements(By.CSS_SELECTOR, ".product-title a")
        print(f"Found {len(links)} products on page 1. Checking first 5...", flush=True)
        
        for i, l in enumerate(links[:5]):
            try:
                href = l.get_attribute("href")
                title = l.text
                print(f"\n--- Checking Product {i+1}: {title} ---", flush=True)
                print(f"URL: {href}", flush=True)
                
                # Open in new tab
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(href)
                time.sleep(3)
                
                try:
                    price_els = driver.find_elements(By.CSS_SELECTOR, ".current-price")
                    if price_els:
                        price_el = price_els[0]
                        print(f"Outer HTML: {price_el.get_attribute('outerHTML')}", flush=True)
                        print(f"Text Content: {price_el.text}", flush=True)
                        
                        try:
                            meta_price = price_el.find_element(By.CSS_SELECTOR, "[itemprop='price']")
                            print(f"Meta content: {meta_price.get_attribute('content')}", flush=True)
                        except:
                            print("Meta price [itemprop='price'] NOT FOUND", flush=True)
                            
                        # Test clean functions
                        p1 = clean_price(price_el.text)
                        print(f"Cleaned Text Price: {p1}", flush=True)
                    else:
                        print("No .current-price element found", flush=True)
                        
                except Exception as e:
                    print(f"Error finding price element: {e}", flush=True)
                    
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                
            except Exception as e:
                print(f"Error processing product {i}: {e}", flush=True)

    except Exception as e:
        print(f"Main error: {e}", flush=True)
    finally:
        driver.quit()

if __name__ == "__main__":
    debug()
