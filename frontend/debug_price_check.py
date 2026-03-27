import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

URLS = [
    ("MegaPC", "https://megapc.tn/shop/product/PC%20PORTABLE/PC%20PORTABLE%20GAMER/Lenovo-LOQ-15IAX9E-15-6-FHD-IPS-i5-12450HX-RTX-2050-32Go-RAM-512Go-SSD"),
    ("Skymil", "https://skymil-informatique.com/pc-portable-gamer/12169-asus-16x-i5-13420h-rtx-3050-8gb-512go-ssd-silver.html")
]

def check():
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    print("Checking Real Prices...")
    
    driver = uc.Chrome(options=options)
    
    for source, url in URLS:
        try:
            driver.get(url)
            time.sleep(5)
            
            price_text = "Not Found"
            if source == "MegaPC":
                # MegaPC selector? Inspecting from memory of similar sites or generic approach
                # usually .price or h2 or .current-price
                try:
                    els = driver.find_elements(By.CSS_SELECTOR, ".price, .final-price, .product-price, h2.price")
                    texts = [e.text for e in els if e.text.strip()]
                    price_text = texts[0] if texts else "No Text"
                except: pass
            elif source == "Skymil":
                try:
                    price_text = driver.find_element(By.CSS_SELECTOR, ".current-price span[content], .price").text
                except: pass
                
            print(f"[{source}] URL: {url}")
            print(f"    Real Price Text: {price_text}")
            
        except Exception as e:
            print(f"Error on {source}: {e}")

    driver.quit()

if __name__ == "__main__":
    check()
