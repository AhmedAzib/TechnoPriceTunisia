import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

class MegaPCMotherboardScraper:
    def __init__(self):
        self.base_url = "https://megapc.tn/shop/COMPOSANTS/CARTE%20M%C3%88RE"
        self.output_file = r"C:\Users\USER\Documents\programmation\frontend\src\data\megapc_motherboards.json"
        
    def clean_price(self, price_str):
        if not price_str: return 0.0
        clean = price_str.upper().replace('DT', '').replace('TND', '').replace(' ', '').replace(',', '.')
        clean = "".join([c for c in clean if c.isdigit() or c == '.'])
        try:
            return float(clean)
        except:
            return 0.0

    def parse_specs(self, soup):
        specs = {
            "chipset": "",
            "socket": "",
            "memory": "",
            "format": "",
            "model_ref": ""
        }
        
        content_div = soup.select_one(".pro-details") or soup.select_one("#product-details") or soup.select_one("div.description")
        if not content_div: content_div = soup.body
            
        full_text = content_div.get_text("\n", strip=True)
        lines = full_text.split("\n")
        
        for line in lines:
            line_lower = line.lower()
            if "chipset" in line_lower:
                specs["chipset"] = line.split(":", 1)[-1].strip().replace("⚙️", "").strip()
            elif "socket" in line_lower:
                specs["socket"] = line.split(":", 1)[-1].strip().replace("🧠", "").strip()
            elif "mémoire" in line_lower or "memoire" in line_lower:
                specs["memory"] = line.split(":", 1)[-1].strip().replace("💾", "").strip()
            elif "format" in line_lower:
                specs["format"] = line.split(":", 1)[-1].strip().replace("🖥️", "").strip()
            elif "référence" in line_lower:
                 if ":" in line:
                    specs["model_ref"] = line.split(":", 1)[-1].strip()
        return specs

    def infer_brand(self, title):
        t = title.upper()
        if "ASUS" in t: return "ASUS"
        if "MSI" in t: return "MSI"
        if "GIGABYTE" in t: return "GIGABYTE"
        if "ASROCK" in t: return "ASRock"
        if "BIOSTAR" in t: return "Biostar"
        if "NZXT" in t: return "NZXT"
        return "Unknown"

    def scrape(self):
        print("Starting MegaPC Motherboard Scraper (Selenium Click Logic)...")
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless=new") 
        options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=options)
        
        all_products = []
        page = 1
        max_pages = 8
        
        try:
            # Initial Load
            driver.get(self.base_url)
            time.sleep(2)
            
            while page <= max_pages:
                print(f"\nProcessing Page {page}...")
                
                # Wait for content
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "article.product-card"))
                    )
                except:
                    print(f"No products found on page {page} (timeout). Checking if empty...")
                    break
                
                # Scroll
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(1)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                articles = soup.select("article.product-card")
                
                if not articles:
                    print("No articles found.")
                    break
                
                print(f"Found {len(articles)} products. Extracting details...")
                
                current_page_items = []
                
                # Extract Links First
                for art in articles:
                    try:
                        title_el = art.select_one("p.text-skin-base") or art.select_one("a[title]")
                        title = title_el.get_text(strip=True) if title_el else "Unknown"
                        
                        # Dedupe global
                        if any(p['title'] == title for p in all_products):
                            continue

                        price_el = art.select_one("span.text-skin-primary")
                        price = self.clean_price(price_el.get_text(strip=True)) if price_el else 0.0
                        
                        link_el = art.select_one("a")
                        link = link_el.get('href') if link_el else ""
                        if not link: continue
                        if not link.startswith("http"): link = "https://megapc.tn" + link
                        
                        img_el = art.select_one("img")
                        img = ""
                        if img_el:
                            img = img_el.get('src') or img_el.get('data-src') or img_el.get("srcset", "").split(" ")[0] or ""
                            if img.startswith("/"): img = "https://megapc.tn" + img
                        
                        stock_status = "En Stock"
                        card_text = art.get_text(" ", strip=True).lower()
                        if "rupture" in card_text or "hors stock" in card_text:
                            stock_status = "Hors Stock"
                            
                        current_page_items.append({
                            "title": title,
                            "price": price,
                            "link": link,
                            "image": img,
                            "stock": stock_status
                        })
                    except: pass
                
                if not current_page_items:
                    print("No new unique items found on this page.")
                    # Fallthrough to pagination try, maybe page 2 has unique items?
                
                # Visit Details
                original_handle = driver.current_window_handle
                
                for i, item in enumerate(current_page_items):
                    print(f"  [{i+1}/{len(current_page_items)}] Details: {item['title'][:40]}...")
                    try:
                        driver.switch_to.new_window('tab')
                        driver.get(item['link'])
                        # Wait for details
                        time.sleep(1.0) # Safety
                        
                        pd_source = driver.page_source
                        pd_soup = BeautifulSoup(pd_source, 'html.parser')
                        specs = self.parse_specs(pd_soup)
                        
                        og_img = pd_soup.find("meta", property="og:image")
                        if og_img and og_img.get("content"):
                             item['image'] = og_img.get("content")
                             
                        final_item = {
                            **item,
                            "chipset": specs.get("chipset", ""),
                            "socket": specs.get("socket", ""),
                            "memory": specs.get("memory", ""),
                            "format": specs.get("format", ""),
                            "model_ref": specs.get("model_ref", ""),
                            "brand": self.infer_brand(item['title']),
                            "category": "Motherboard"
                        }
                        
                        all_products.append(final_item)
                        driver.close()
                        driver.switch_to.window(original_handle)
                        
                    except Exception as e:
                        print(f"    Failed details: {e}")
                        try:
                            if len(driver.window_handles) > 1:
                                driver.close()
                                driver.switch_to.window(original_handle)
                        except: pass
                        
                        # Fallback add
                        final_item = {
                            **item,
                            "chipset": "", "socket": "", "memory": "", "format": "", "model_ref": "",
                            "brand": self.infer_brand(item['title']),
                            "category": "Motherboard"
                        }
                        all_products.append(final_item)

                # Click Next Page
                try:
                    next_page_num = page + 1
                    print(f"Attempting to click Page {next_page_num}...")
                    
                    found_next = False
                    
                    # Strategy 1: Find button with text '2', '3' etc
                    try:
                        xpath = f"//button[normalize-space()='{next_page_num}']"
                        btn = driver.find_element(By.XPATH, xpath)
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", btn)
                        found_next = True
                    except:
                        pass
                        
                    # Strategy 2: Find active button and click sibling
                    if not found_next:
                        try:
                            active = driver.find_element(By.CSS_SELECTOR, "button.bg-skin-primary") # Usually active page has primary color
                            sibling = active.find_element(By.XPATH, "following-sibling::button[1]")
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sibling)
                            time.sleep(0.5)
                            driver.execute_script("arguments[0].click();", sibling)
                            found_next = True
                        except:
                            pass
                            
                    if found_next:
                        print(f"Clicked next. Waiting for Page {next_page_num}...")
                        time.sleep(4) # Wait for reload
                        page += 1
                    else:
                        print("No next button found. Reached end.")
                        break
                        
                except Exception as e:
                    print(f"Pagination Error: {e}")
                    break
                    
        except Exception as e:
            print(f"Global Error: {e}")
            
        finally:
            driver.quit()
            
        print(f"\nSaving {len(all_products)} motherboards to {self.output_file}...")
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        print("Done!")

if __name__ == "__main__":
    S = MegaPCMotherboardScraper()
    S.scrape()
