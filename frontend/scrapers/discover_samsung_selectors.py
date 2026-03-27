from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

def discover():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    try:
        url = "https://www.samsungtunisie.tn/fr/14-smartphone-samsung-tunisie"
        print(f"visiting {url}")
        driver.get(url)
        time.sleep(5) # wait for render
        
        # Dump full page source to analyze
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Try to find product blocks
        # Common PrestaShop selectors
        candidates = [
            ".product-container",
            ".ajax_block_product",
            "li.product",
            ".item-product",
            "article.product-miniature"
        ]
        
        found_block = None
        for sel in candidates:
            blocks = soup.select(sel)
            if blocks:
                print(f"Found {len(blocks)} items using selector: {sel}")
                found_block = blocks[0]
                break
        
        if found_block:
            print("\n--- SAMPLE PRODUCT HTML ---")
            try:
                print(found_block.prettify().encode('utf-8', errors='ignore').decode('utf-8'))
            except:
                print("Could not print HTML block due to encoding.")
            print("---------------------------\n")
            
            # Analyze specific fields in the found block
            print("Potential Title:")
            print(found_block.select_one("a.product-name, h3.h3.product-title a, .name a"))
            
            print("\nPotential Price:")
            print(found_block.select_one(".price, .product-price, .content_price"))
            
            print("\nPotential Image:")
            print(found_block.select_one("img"))
            
            print("\nPotential Stock:")
            print(found_block.select_one(".availability, .stock, .allow-oosp"))
            
        else:
            print("No obvious product blocks found. Dumping first 5000 chars of body for review.")
            print(soup.body.prettify()[:5000])

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    discover()
