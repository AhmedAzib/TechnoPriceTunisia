import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MegaPCGamerScraper:
    def __init__(self):
        self.start_url = "https://megapc.tn/shop/PC%20PORTABLE/PC%20PORTABLE%20GAMER"
        self.output_file = "frontend/src/data/megapc_gamer.json"
    
    def clean_price(self, price_str):
        if not price_str: return 0.0
        clean = price_str.replace(' ', '').replace('DT', '').replace('TND', '').replace('dt', '').replace(',', '.')
        clean = "".join([c for c in clean if c.isdigit() or c == '.'])
        try:
            return float(clean)
        except:
            return 0.0

    def scrape(self):
        print("Scraping MegaPC Gamer Laptops (Standard Robust)...")
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--disable-extensions")
        options.add_argument("--window-size=1920,1080")
        # options.add_argument("--remote-debugging-port=9222") # Caused crash on restart?
        # options.add_argument("--headless=new") 
        
        driver = webdriver.Chrome(options=options)
        
        all_laptops = []
        page = 1
        url = f"{self.start_url}?page={page}"
        
        try:
            while True:
                print(f"Visiting Page {page} (URL: {url})...")
                driver.get(url)
                
                # Wait for products
                try:
                    WebDriverWait(driver, 25).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "article.product-card"))
                    )
                except:
                    print("Timeout waiting for products or end of list.")
                    # Check if empty grid?
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
                    try:
                        # Stock check
                        full_text = art.text.lower()
                        if "rupture" in full_text or "hors stock" in full_text:
                            # print("Skipping Out of Stock")
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
                        
                        # Image Extraction (Enhanced for Next.js Lazy Loading)
                        img = ""
                        try:
                            img_el = art.find_element(By.TAG_NAME, "img")
                            
                            # Scroll into view to trigger lazy load
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", img_el)
                            time.sleep(0.2) 

                            src = img_el.get_attribute("src") or ""
                            srcset = img_el.get_attribute("srcset") or ""
                            
                            # Primary: Use srcset if available (highest res usually last)
                            # Next.js often puts the real image in srcset even if src is a placeholder
                            if srcset:
                                # "url 1x, url 2x" -> take last
                                candidate = srcset.split(",")[-1].strip().split(" ")[0]
                                if candidate.startswith("/"):
                                    img = f"https://megapc.tn{candidate}"
                                else:
                                    img = candidate
                            elif src and "data:image" not in src:
                                img = src
                            else:
                                # Fallback if src is data:image and no srcset
                                img = src 
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
                
                # Click-based Pagination (Reliable for Next.js/React hydration)
                try:
                    # Scroll to bottom
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                    
                    # Try finding the stored 'next page' number
                    next_page_num = page + 1
                    
                    # Look for a link with exact text matching the next page number
                    # Or the ">" icon button if we can identify it.
                    # Let's try locating the specific number first as user suggested "buttons from 1 to 6"
                    
                    # Try generic list of pagination items first to debug if needed
                    # pagination_items = driver.find_elements(By.CSS_SELECTOR, "ul.pagination li")
                    
                    # Try finding link by text (e.g. "2", "3")
                    # XPath is good for text match
                    next_btn = None
                    
                    # Attempt 1: Exact Number Button (e.g. <button>2</button>)
                    # From debug: <button ... data-page="1">2</button>
                    try:
                         # XPath to find a button with exact text equal to next_page_num
                         xpath = f"//button[normalize-space()='{next_page_num}']"
                         candidates = driver.find_elements(By.XPATH, xpath)
                         for cand in candidates:
                             if cand.text.strip() == str(next_page_num):
                                 next_btn = cand
                                 break
                    except: pass
                    
                    # Attempt 2: "Next" arrow button
                    # It's the last button in the flex container
                    if not next_btn:
                        try:
                             # Find the active button (has bg-skin-primary)
                             # Then find the next button sibling
                             active_btn = driver.find_element(By.CSS_SELECTOR, "button.bg-skin-primary")
                             # Use xpath to get following sibling button
                             next_btn = active_btn.find_element(By.XPATH, "following-sibling::button[1]")
                        except: pass

                    if next_btn:
                        print(f"Clicking pagination button for Page {next_page_num}...")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", next_btn)
                        
                        time.sleep(5) # Wait for reload
                        page += 1
                        url = driver.current_url
                    else:
                        print("No next page button found.")
                        # Check if we reached the max?
                        break

                        
                except Exception as e:
                    print(f"Pagination error: {e}")
                    with open("debug_pagination.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
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
    S = MegaPCGamerScraper()
    S.scrape()
