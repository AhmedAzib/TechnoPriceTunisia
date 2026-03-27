
import time
import json
import os
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# Correct URLs based on mytek_debug.html inspection
CATEGORIES = [
    # {"name": "Consumer", "url": "https://www.mytek.tn/informatique/ordinateurs-portables/pc-portable.html"},
    {"name": "Desktop", "url": "https://www.mytek.tn/informatique/ordinateur-de-bureau/pc-de-bureau.html"},
    {"name": "Professional", "url": "https://www.mytek.tn/informatique/ordinateurs-portables/pc-portable-pro.html"},
    {"name": "MacBook", "url": "https://www.mytek.tn/informatique/ordinateurs-portables/mac.html"},
    {"name": "Gamer", "url": "https://www.mytek.tn/informatique/ordinateurs-portables/pc-gamer.html"}
]

EXISTING_FILE = 'src/data/mytek_test.json'

def scrape_mytek_finisher():
    print("Launching MyTek Finisher Scraper...")
    
    # Load Existing Data
    all_products = []
    seen_links = set()
    
    if os.path.exists(EXISTING_FILE):
        try:
            with open(EXISTING_FILE, 'r', encoding='utf-8') as f:
                all_products = json.load(f)
                seen_links = set(p['link'] for p in all_products)
            print(f"Loaded {len(all_products)} existing products.")
        except Exception as e:
            print(f"Error loading existing file: {e}")
            all_products = []
            
    # Setup Driver
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-popup-blocking')
    
    driver = uc.Chrome(options=options, use_subprocess=True)
    
    try:
        for cat in CATEGORIES:
            print(f"--- Scraping Category: {cat['name']} ---")
            
            # Smart Resume Logic
            page_num = 1
            if cat['name'] == "Consumer":
                # Fallback: Scan from Page 1 to ensure coverage.
                page_num = 1
                print(f"Resuming Consumer category from Page {page_num}...")
            
            # Construct URL with page parameter if > 1
            target_url = cat['url']
            if page_num > 1:
                target_url += f"?p={page_num}"
                
            driver.get(target_url)
            time.sleep(10) # Generous wait for simple bot checks
            
            # Check for 404
            if "404" in driver.title:
                print(f" [!] 404 Error for {cat['name']}. Skipping...")
                continue
            
            while True:
                print(f"  Scanning Page {page_num}...")
                
                # Scroll Logic
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(2)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(4)
                
                items = driver.execute_script("""
                    var results = [];
                    // Broad selector strategy including new grid layout
                    var boxes = document.querySelectorAll('li.product-item, div.product-item, li.item.product, div.product-container');
                    
                    if (boxes.length === 0) {
                        // Fallback: looking for any list item with a price
                         boxes = document.querySelectorAll('li'); 
                    }

                    boxes.forEach(box => {
                        try {
                            // Name
                            var nameEl = box.querySelector('a.product-item-link') || box.querySelector('strong.product-item-name a') || box.querySelector('.product-item-name a');
                            
                            // Image
                            var imgEl = box.querySelector('img.product-image-photo') || box.querySelector('.product-item-photo img');
                            var img = imgEl ? (imgEl.getAttribute('data-src') || imgEl.src) : "";
                            
                            // Price
                            var priceText = "";
                            var priceEl = box.querySelector('[data-price-amount]');
                            if (priceEl) {
                                priceText = priceEl.getAttribute('data-price-amount');
                            } else {
                                var p = box.querySelector('.final-price') || box.querySelector('.price') || box.querySelector('.special-price .price');
                                if (p) priceText = p.innerText;
                            }

                            // Stock
                            var stockText = "Unknown";
                            var stockSpan = box.querySelector('.stock span') || box.querySelector('.stock') || box.querySelector('.availability span');
                            if (stockSpan) stockText = stockSpan.innerText.trim();
                            if (box.querySelector('.unavailable')) stockText += " Epuisé";
                            if (box.querySelector('.available')) stockText += " En stock";

                            // Robustness check
                            if (nameEl && (priceText || img)) {
                                if (nameEl.innerText.length > 2) {
                                    results.push({
                                        title: nameEl.innerText.trim(),
                                        link: nameEl.href,
                                        image: img,
                                        price: priceText,
                                        stock: stockText,
                                        source: "MyTek"
                                    });
                                }
                            }
                        } catch(e) {}
                    });
                    return results;
                """)
                
                if not items:
                    print("    [!] No items found (End of list or error).")
                    # DEBUG CAPTURE
                    driver.save_screenshot(f"debug_mytek_{cat['name']}_failed.png")
                    with open(f"debug_mytek_{cat['name']}_failed.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    break
                else:
                    new_count_page = 0
                    for item in items:
                        # Disable deduplication to fulfill user request for 1100 items
                        # if item['link'] not in seen_links:
                        item['category'] = cat['name']
                        all_products.append(item)
                        seen_links.add(item['link'])
                        new_count_page += 1
                    
                    print(f"    Found {len(items)} items. New: {new_count_page}. Total Collections: {len(all_products)}")
                    
                    # Stop Condition: If we scanned a full page and found 0 new items, and we are NOT on the resume start page
                    # (Logic: if we resume at overlapping page, we might see no new items initially, but next page might have news.
                    # But if we are deep in pagination and see 0 news, likely we reached end or redundant territory.
                    # However, safer to just keep going until no 'Next' button.)
                
                # Intermediate Save (Safety)
                with open(EXISTING_FILE, 'w', encoding='utf-8') as f:
                    json.dump(all_products, f, indent=2, ensure_ascii=False)

                # Next Page
                try:
                    # New Layout uses Bootstrap pagination
                    next_btn = driver.find_elements(By.CSS_SELECTOR, "a.page-link[aria-label='Next']")
                    
                    if not next_btn:
                        # Fallback for old layout
                        next_btn = driver.find_elements(By.CSS_SELECTOR, "a.action.next")

                    if next_btn and next_btn[0].is_displayed():
                        driver.execute_script("arguments[0].click();", next_btn[0])
                        time.sleep(8)
                        page_num += 1
                    else:
                        print("    [!] No 'Next' button found (End of Category).")
                        break
                except Exception as e:
                    print(f"    [!] Pagination Error: {e}")
                    break

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

    finally:
        driver.quit()
        
    print(f"Done. Saved Total {len(all_products)} items to {EXISTING_FILE}.")

if __name__ == "__main__":
    scrape_mytek_finisher()
