import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import json
import time

class DesktopRestorerExtended:
    def __init__(self):
        self.output_tn = "frontend/src/data/tunisianet_new.json"
        
    def clean_price(self, price_str):
        if not price_str: return 0.0
        clean = price_str.replace(',', '.').replace(' ', '').replace('DT', '').replace('TND', '')
        clean = "".join([c for c in clean if c.isdigit() or c == '.'])
        try:
            return float(clean)
        except:
            return 0.0

    def scrape_tunisianet(self):
        print("Scraping Tunisianet Desktops (Extended)...")
        options = uc.ChromeOptions()
        options.add_argument("--disable-gpu")
        # options.add_argument("--headless=new")
        driver = uc.Chrome(options=options)
        
        # Ranges: 
        # PC Bureau: 2 to 12
        # Gamer: 3 to 8
        base_urls = []
        for i in range(2, 13):
            base_urls.append(f"https://www.tunisianet.com.tn/301-pc-de-bureau?page={i}")
        for i in range(3, 9):
            base_urls.append(f"https://www.tunisianet.com.tn/373-pc-de-bureau-gamer?page={i}")
            
        new_items = []
        
        try:
            for url in base_urls:
                print(f"Visiting {url}...")
                driver.get(url)
                time.sleep(2) # Faster
                
                products = driver.find_elements(By.CSS_SELECTOR, ".product-miniature")
                print(f"Found {len(products)} products.")
                
                if len(products) == 0:
                    print("No products found, stopping category loop.")
                    # continue or break? Tunisianet might return empty page.
                    # if page 12 is empty it's fine.
                    pass
                
                for p in products:
                    try:
                        title_el = p.find_element(By.CSS_SELECTOR, ".product-title a")
                        title = title_el.text.strip()
                        link = title_el.get_attribute("href")
                        
                        price = 0.0
                        try:
                            price_el = p.find_element(By.CSS_SELECTOR, ".price")
                            price = self.clean_price(price_el.text)
                        except: pass
                        
                        img = ""
                        try:
                            img_el = p.find_element(By.CSS_SELECTOR, "img")
                            img = img_el.get_attribute("src")
                        except: pass

                        item = {
                            "title": title,
                            "price": price,
                            "image": img,
                            "link": link,
                            "brand": "Unknown",
                            "stock": "En Stock"
                        }
                        new_items.append(item)
                        
                    except Exception as e:
                        pass
                        
        finally:
            driver.quit()
            
        print(f"Scraped {len(new_items)} desktops from Extended run.")
        return new_items

    def restore(self):
        tn_desktops = self.scrape_tunisianet()
        
        if tn_desktops:
            try:
                with open(self.output_tn, 'r', encoding='utf-8') as f:
                    current_data = json.load(f)
                    
                existing_links = set(p.get('link') for p in current_data)
                added_count = 0
                
                for item in tn_desktops:
                    if item['link'] not in existing_links:
                        current_data.append(item)
                        added_count += 1
                        
                with open(self.output_tn, 'w', encoding='utf-8') as f:
                    json.dump(current_data, f, indent=2, ensure_ascii=False)
                    
                print(f"Added {added_count} new desktops to {self.output_tn}")
                
            except Exception as e:
                print(f"Error updating file: {e}")

if __name__ == "__main__":
    R = DesktopRestorerExtended()
    R.restore()
