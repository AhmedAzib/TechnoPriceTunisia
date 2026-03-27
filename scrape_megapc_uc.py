import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

class MegaPCLaptopScraper:
    def __init__(self):
        self.base_url = "https://megapc.tn/shop/category/ordinateur-portable"
        self.output_file = "frontend/src/data/megapc_new.json"
        self.target_count = 100
    
    def clean_price(self, price_str):
        if not price_str: return 0.0
        clean = price_str.replace(' ', '').replace('DT', '').replace('TND', '').replace('dt', '').replace(',', '.')
        clean = "".join([c for c in clean if c.isdigit() or c == '.'])
        try:
            return float(clean)
        except:
            return 0.0

    def scrape(self):
        print("Scraping MegaPC Laptops (UC Subprocess, Target: 100)...")
        options = uc.ChromeOptions()
        options.add_argument("--disable-gpu")
        # options.add_argument("--no-sandbox") # Sometimes causes issues with uc
        
        # use_subprocess=True helps with some environment crashes
        driver = uc.Chrome(options=options, use_subprocess=True)
        
        all_laptops = []
        page = 1
        url = f"{self.base_url}?page={page}"
        
        try:
            while len(all_laptops) < self.target_count:
                print(f"Visiting Page {page} (URL: {url})...")
                driver.get(url)
                
                # Wait for Title (text-skin-base)
                try:
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "article.product-card p.text-skin-base"))
                    )
                except:
                    print("Timeout waiting for products.")
                    # Dump source just in case
                    # with open("debug_uc_fail.html", "w", encoding="utf-8") as f:
                    #     f.write(driver.page_source)
                    break
                
                # Scroll
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(2)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                articles = driver.find_elements(By.CSS_SELECTOR, "article.product-card")
                print(f"Found {len(articles)} cards on page {page}.")
                
                if not articles:
                    print("No articles found.")
                    break
                    
                added_on_page = 0
                for art in articles:
                    if len(all_laptops) >= self.target_count: break
                    
                    try:
                        # Stock check including badge
                        full_text = art.text.lower()
                        if "rupture" in full_text or "hors stock" in full_text:
                            continue
                            
                        # Title
                        try:
                            title_el = art.find_element(By.CSS_SELECTOR, "p.text-skin-base")
                            title = title_el.text.strip()
                        except:
                            title_el = art.find_element(By.TAG_NAME, "a")
                            title = title_el.get_attribute("title")
                        if not title: continue
                        
                        # Price
                        price = 0.0
                        try:
                            price_el = art.find_element(By.CSS_SELECTOR, "span.text-skin-primary")
                            price = self.clean_price(price_el.text)
                        except: pass
                        
                        # Link
                        try:
                            link_el = art.find_element(By.TAG_NAME, "a")
                            link = link_el.get_attribute("href")
                        except: link = ""
                        
                        # Image
                        img = ""
                        try:
                            img_el = art.find_element(By.TAG_NAME, "img")
                            img = img_el.get_attribute("src")
                            if "data:image" in img or "placeholder" in img:
                                srcset = img_el.get_attribute("srcset")
                                if srcset:
                                    img = srcset.split(",")[-1].strip().split(" ")[0]
                        except: pass
                        
                        if any(x['link'] == link for x in all_laptops):
                            continue
                            
                        item = {
                            "title": title,
                            "price": price,
                            "image": img,
                            "link": link,
                            "brand": "Unknown",
                            "stock": "En Stock"
                        }
                        all_laptops.append(item)
                        added_on_page += 1
                        
                    except Exception as e:
                        pass
                
                print(f"Added {added_on_page} valid items from page {page}. Total: {len(all_laptops)}")
                page += 1
                
                # Pagination URL update
                try:
                    next_btn = driver.find_element(By.CSS_SELECTOR, "ul.pagination li.active + li a")
                    next_url = next_btn.get_attribute("href")
                    if next_url:
                        url = next_url
                    else:
                        print("No next URL found.")
                        break
                except:
                     print("Pagination end.")
                     break
                
        except Exception as e:
            print(f"Global Error: {e}")
            
        finally:
            try:
                driver.quit()
            except: pass
            
        print(f"Scraped {len(all_laptops)} items.")
        if len(all_laptops) > 0:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(all_laptops, f, indent=2, ensure_ascii=False)
            print(f"Saved to {self.output_file}")

if __name__ == "__main__":
    S = MegaPCLaptopScraper()
    S.scrape()
