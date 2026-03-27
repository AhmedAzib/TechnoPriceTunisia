import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import json
import time
import re

class SkymilPatcher:
    def __init__(self):
        self.output_file = "frontend/src/data/skymil_new.json"
        
    def setup_driver(self):
        options = uc.ChromeOptions()
        options.add_argument("--disable-gpu")
        # options.add_argument("--headless=new")
        self.driver = uc.Chrome(options=options)

    def clean_price(self, price_str):
        if not price_str: return 0.0
        clean = price_str.replace(' ', '').replace('DT', '').replace('TND', '').replace('dt', '')
        clean = clean.replace(',', '.')
        clean = re.sub(r'[^\d.]', '', clean)
        try:
            return float(clean)
        except:
            return 0.0

    def patch(self):
        with open(self.output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Filter for suspicious items
        targets = []
        for i, p in enumerate(data):
            val = float(p.get('price', 0))
            if val > 0 and val % 1000 == 0:
                targets.append(i)
                
        if not targets:
            print("No suspicious items found.")
            return

        print(f"Found {len(targets)} items to patch.")
        self.setup_driver()
        
        try:
            for idx in targets:
                product = data[idx]
                url = product['link']
                print(f"Visiting [{idx}] {url} ...")
                
                try:
                    self.driver.get(url)
                    time.sleep(3)
                    
                    try:
                        price_el = self.driver.find_element(By.CSS_SELECTOR, ".price, .product-price, .current-price-value")
                        real_price = self.clean_price(price_el.text)
                        
                        if real_price > 0 and real_price != product['price']:
                            print(f"  Update: {product['price']} -> {real_price}")
                            data[idx]['price'] = real_price
                            data[idx]['price_fixed'] = True # Marker
                        else:
                            print(f"  Price matched or invalid: {real_price}")
                            
                    except Exception as e:
                        print(f"  Price extract failed: {e}")
                        
                except Exception as e:
                    print(f"  Load failed: {e}")
                    
                # Save progressively
                if idx % 5 == 0:
                    with open(self.output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                        
        finally:
            self.driver.quit()
            
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    Patcher = SkymilPatcher()
    Patcher.patch()
