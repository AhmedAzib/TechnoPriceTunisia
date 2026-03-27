import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import json
import time

def scrape_tdiscount():
    print("Initializing Tdiscount Scraper (Visible Mode for Cloudflare Bypass)...")
    options = uc.ChromeOptions()
    # options.add_argument('--headless=new') # Disabled - Cloudflare blocks this aggressively
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-popup-blocking')
    
    # Initialize driver
    driver = uc.Chrome(options=options)
    driver.set_window_size(1280, 800)
    
    all_products = []
    
    try:
        # 1. Navigate
        url = "https://tdiscount.tn/informatique/ordinateur-portable"
        print(f"Navigating to {url}...")
        driver.get(url)
        
        # 2. Robust Cloudflare Wait
        print("Waiting for Cloudflare check (approx 15-30s)...")
        time.sleep(10)
        
        retries = 0
        while "Just a moment" in driver.title and retries < 6:
            print(f"Still checking... ({retries+1}/6)")
            time.sleep(5)
            retries += 1
            
        print(f"Page Title: {driver.title}")
        
        if "Just a moment" in driver.title:
            print("FAILED: Stuck on Cloudflare even in visible mode.")
            print("Please manually click the challenge checkbox if visible.")
            # Give user 10s to click manually if needed
            time.sleep(10)
            if "Just a moment" in driver.title:
                driver.save_screenshot("tdiscount_cloudflare_stuck.png")
                return

        # 2b. Handle Cookie Consent
        try:
            print("Looking for cookie consent...")
            # Common selectors for "Accept" buttons
            cookie_selectors = [
                 "button#btn-cookie-allow", 
                 "a#btn-cookie-allow",
                 ".cc-btn.cc-allow", 
                 "button.accept-cookies", 
                 ".cookie-consent-allow",
                 "button.action.primary.accept", # Magento common
                 "button[aria-label='Accept']",
                 "#notice-cookie-block button" # Often used in Magento 2
            ]
            
            for sel in cookie_selectors:
                try:
                    cookie_btns = driver.find_elements(By.CSS_SELECTOR, sel)
                    if cookie_btns:
                        for btn in cookie_btns:
                            if btn.is_displayed():
                                print(f"Found cookie button: {sel}. Clicking...")
                                btn.click()
                                time.sleep(2)
                                break
                        break
                except:
                    pass
        except Exception as e:
            print(f"Cookie check warning: {e}")

        # 3. Scraping Loop
        page_num = 1
        max_pages = 10
        
        while page_num <= max_pages:
            print(f"Processing Page {page_num}...")
            
            # Scroll handling
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Selectors
            product_selectors = [
                 ".product-item-info", 
                 ".item-product",
                 "li.product-item",
                 ".products.list.items .item"
            ]
            
            product_containers = []
            for sel in product_selectors:
                product_containers = driver.find_elements(By.CSS_SELECTOR, sel)
                if product_containers:
                    break
            
            print(f"Found {len(product_containers)} products.")
            
            if not product_containers:
                 print("No products found on this page. Dumping source...")
                 # with open(f"tdiscount_debug_p{page_num}.html", "w", encoding="utf-8") as f:
                 #     f.write(driver.page_source)
                 break
            
            count = 0
            for p in product_containers:
                try:
                    # Logic to extract data
                    try:
                        name_el = p.find_element(By.CSS_SELECTOR, ".product-item-link")
                        name = name_el.text.strip()
                        link = name_el.get_attribute("href")
                    except:
                        continue
                    
                    try:
                        price_el = p.find_element(By.CSS_SELECTOR, "[data-price-amount]")
                        price_val = float(price_el.get_attribute('data-price-amount'))
                        price = f"{price_val:.3f} TND"
                    except:
                        try:
                            # Fallback text extraction
                            price_text = p.find_element(By.CSS_SELECTOR, ".price").text.strip()
                            # Clean: "1 249,000 DT" -> 1249.000
                            clean_p = price_text.replace('DT','').replace('TND','').replace(' ','').replace(',', '.').strip()
                            # Handle non-breaking spaces if present (keeping only digits and dot)
                            clean_p = "".join([c for c in clean_p if c.isdigit() or c == '.'])
                            if clean_p:
                                price = f"{float(clean_p):.3f} TND"
                            else:
                                price = "N/A"
                        except:
                            price = "N/A"
                    
                    try:
                        img_el = p.find_element(By.CSS_SELECTOR, ".product-image-photo")
                        img = img_el.get_attribute("src")
                    except:
                        img = ""
                        
                    if name and link:
                        all_products.append({
                            "name": name,
                            "price": price,
                            "link": link,
                            "image": img,
                            "source": "Tdiscount"
                        })
                        count += 1
                except:
                    continue
            
            print(f"Extracted {count} items.")
            
            # Next Page
            try:
                # Try finding 'Next' button
                # Usually .action.next
                next_btn = driver.find_element(By.CSS_SELECTOR, "a.action.next")
                if "disabled" in next_btn.get_attribute("class"):
                    break
                    
                next_url = next_btn.get_attribute("href")
                print(f"Next URL: {next_url}")
                driver.get(next_url)
                time.sleep(5)
                page_num += 1
            except:
                print("No next page link found.")
                break
                
        # 4. Save
        if all_products:
            print(f"Scraping complete. Total: {len(all_products)}")
            # Saving to both locations for safety
            with open("src/data/tdiscount_products.json", "w", encoding="utf-8") as f:
                json.dump(all_products, f, indent=4, ensure_ascii=False)
            print("SUCCESS: Data saved to src/data/tdiscount_products.json")
        else:
            print("No products scraped.")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_tdiscount()
