from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

URL = "https://megapc.tn/shop/COMPOSANTS/PROCESSEUR"

def debug_specific_item():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        print(f"Navigating to {URL}...")
        driver.get(URL)
        time.sleep(15) # Long wait to ensure full loading
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        products = soup.select("article.product-card")
        
        target_title_part = "10105F"
        
        found = False
        for p in products:
            headers = p.select("h2, h3, .product-title, a")
            title = ""
            for h in headers:
                if len(h.get_text(strip=True)) > 5:
                    title = h.get_text(strip=True)
                    break
            
            if target_title_part in title:
                found = True
                print(f"\n--- FOUND TARGET: {title} ---")
                print("HTML Dumping:")
                print(p.prettify())
                break
        
        if not found:
            print(f"Target {target_title_part} not found on page.")

    finally:
        driver.quit()

if __name__ == "__main__":
    debug_specific_item()
