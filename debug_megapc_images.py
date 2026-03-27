from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

URL = "https://megapc.tn/shop/COMPOSANTS/PROCESSEUR"

def debug_images():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        print(f"Navigating to {URL}...")
        driver.get(URL)
        time.sleep(5) # Wait for JS to load
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        products = soup.select("article.product-card")
        
        print(f"Found {len(products)} products.")
        
        # Check specific items mentioned by user
        targets = ["i3-10105F", "5500GT", "5600 Tray", "5600GT", "5700", "5700X"]
        
        for p in products:
            headers = p.select("h2, h3, .product-title, a")
            title = ""
            for h in headers:
                if len(h.get_text(strip=True)) > 5:
                    title = h.get_text(strip=True)
                    break
            
            # Check if this is a target
            is_target = False
            for t in targets:
                if t.upper() in title.upper():
                    is_target = True
                    break
            
            if is_target:
                print(f"\n--- DEBUG PRODUCT: {title} ---")
                print("HTML snippet of image area:")
                # Print the first few img tags
                imgs = p.find_all("img")
                for i, img in enumerate(imgs):
                    print(f"  Img {i}: src='{img.get('src')}', data-src='{img.get('data-src')}', class='{img.get('class')}'")
                
                # Check what our logic would do
                image = ""
                img_tag = p.select_one(".product-thumbnail img")
                if not img_tag: img_tag = p.select_one(".product-image img")
                if not img_tag: img_tag = p.select_one("a.product-loop-title + div img")
                if not img_tag: img_tag = p.select_one("img")
                
                print(f"  Selected Tag: {img_tag}")
                if img_tag:
                     src = img_tag.get("data-src") or img_tag.get("src") or ""
                     print(f"  Raw Src: {src}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_images()
