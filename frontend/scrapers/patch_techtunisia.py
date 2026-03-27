import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import json
import time
import re

class TunisiaTechPatcher:
    def __init__(self):
        self.output_file = "frontend/src/data/techtunisia_products.json"
        
    def setup_driver(self):
        options = uc.ChromeOptions()
        options.add_argument("--disable-gpu")
        # options.add_argument("--headless=new")
        self.driver = uc.Chrome(options=options)

    def clean_price(self, price_str):
        if not price_str: return 0.0
        # "1 250,000 DT"
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
            
        targets = []
        for i, p in enumerate(data):
            val = float(p.get('price', 0))
            # Target 1000, 2000, 3000...
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
                        # TunisiaTech selectors
                        # Usually .current-price span or .product-price
                        # Inspecting valid pages or guessing standard Prestashop/custom
                        # Try multiple
                        price_el = None
                        selectors = [
                            ".current-price span[itemprop='price']",
                            ".current-price",
                            ".product-price", 
                            "#our_price_display"
                        ]
                        
                        for sel in selectors:
                            try:
                                els = self.driver.find_elements(By.CSS_SELECTOR, sel)
                                if els:
                                    price_el = els[0]
                                    break
                            except:
                                pass
                                
                        if price_el:
                            real_price = self.clean_price(price_el.text)
                            if real_price > 0 and real_price != product['price']:
                                print(f"  Update: {product['price']} -> {real_price}")
                                data[idx]['price'] = real_price
                                data[idx]['price_fixed'] = True
                        else:
                            print("  Price element not found")
                            
                    except Exception as e:
                        print(f"  Price extract failed: {e}")
                        
                except Exception as e:
                    print(f"  Load failed: {e}")
                    
                if idx % 5 == 0:
                    with open(self.output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                        
        finally:
            self.driver.quit()
            
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    Patcher = TunisiaTechPatcher()
    Patcher.patch()
