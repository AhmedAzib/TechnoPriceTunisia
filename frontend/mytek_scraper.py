
import time
import json
import os
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# Correct URLs based on mytek_debug.html inspection
CATEGORIES = [
    {"name": "Consumer", "url": "https://www.mytek.tn/informatique/ordinateurs-portables/pc-portable.html"},
    {"name": "Gamer", "url": "https://www.mytek.tn/informatique/ordinateurs-portables/pc-gamer.html"},
    {"name": "Professional", "url": "https://www.mytek.tn/informatique/ordinateurs-portables/pc-portable-pro.html"},
    {"name": "MacBook", "url": "https://www.mytek.tn/informatique/ordinateurs-portables/mac.html"} 
]

def scrape_mytek():
    print("Launching MyTek Deep Scraper...")
    
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-popup-blocking')
    
    driver = uc.Chrome(options=options, use_subprocess=True)
    
    all_products = []
    seen_links = set()

    try:
        for cat in CATEGORIES:
            print(f"--- Scraping Category: {cat['name']} ---")
            driver.get(cat['url'])
            time.sleep(10) # Generous wait for simple bot checks
            
            # Check for 404
            if "404" in driver.title:
                print(f" [!] 404 Error for {cat['name']}. Skipping...")
                continue
            
            page_num = 1
            while True:
                print(f"  Scanning Page {page_num}...")
                
                # Scroll Logic
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(2)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(4)
                
                # Capture Source if debug needed
                if page_num == 1:
                    with open(f"mytek_debug_{cat['name']}_latest.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)

                items = driver.execute_script("""
                    var results = [];
                    // Broad selector strategy
                    var boxes = document.querySelectorAll('li.product-item, div.product-item, li.item.product');
                    
                    if (boxes.length === 0) {
                        // Fallback: looking for any list item with a price
                         boxes = document.querySelectorAll('li'); 
                    }

                    boxes.forEach(box => {
                        try {
                            // Name
                            var nameEl = box.querySelector('a.product-item-link') || box.querySelector('strong.product-item-name a');
                            
                            // Image
                            var imgEl = box.querySelector('img.product-image-photo');
                            var img = imgEl ? (imgEl.src || imgEl.getAttribute('data-src')) : "";
                            
                            // Price
                            var priceEl = box.querySelector('[data-price-amount]');
                            var priceText = priceEl ? priceEl.getAttribute('data-price-amount') : "";
                            
                            if (!priceText) {
                                var p = box.querySelector('.price');
                                if (p) priceText = p.innerText;
                            }

                            // Stock
                            var stockText = "Unknown";
                            var stockSpan = box.querySelector('.stock span') || box.querySelector('.stock');
                            if (stockSpan) stockText = stockSpan.innerText.trim();
                            if (box.querySelector('.unavailable')) stockText += " Epuisé";
                            if (box.querySelector('.available')) stockText += " En stock";

                            if (nameEl && priceText) {
                                // Filter out tiny prices (accessories usually < 100) or check title
                                if (nameEl.innerText.length > 5) {
                                    results.push({
                                        title: nameEl.innerText.trim(),
                                        link: nameEl.href,
                                        image: img,
                                        price: priceText,
                                        stock: stockText
                                    });
                                }
                            }
                        } catch(e) {}
                    });
                    return results;
                """)
                
                if not items:
                    print("    [!] No items found. Checking fallback...")
                    # If page 1 fails, real issue.
                    if page_num == 1: 
                        print("    [!] Aborting this category.")
                        break
                    else:
                        break 
                else:
                    new_count = 0
                    for item in items:
                        if item['link'] not in seen_links:
                            item['category'] = cat['name']
                            all_products.append(item)
                            seen_links.add(item['link'])
                            new_count += 1
                    print(f"    Found {len(items)} items. New: {new_count}. Total Collections: {len(all_products)}")

                # Next Page
                try:
                    next_btn = driver.find_elements(By.CSS_SELECTOR, "a.action.next")
                    if next_btn and next_btn[0].is_displayed():
                        driver.execute_script("arguments[0].click();", next_btn[0])
                        time.sleep(8)
                        page_num += 1
                    else:
                        print("    [!] No 'Next' button found (CSS).")
                        # Try JS fallback
                        found_next = driver.execute_script("""
                            var next = document.querySelector('a.action.next');
                            if (next) { next.click(); return true; }
                            return false;
                        """)
                        if found_next:
                            time.sleep(8)
                            page_num += 1
                        else:
                            break
                except Exception as e:
                    print(f"    [!] Pagination Error: {e}")
                    break

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

    finally:
        driver.quit()
        
    output_file = 'src/data/mytek_raw.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    print(f"Done. Saved {len(all_products)} items.")

if __name__ == "__main__":
    scrape_mytek()
