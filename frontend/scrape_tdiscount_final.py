import time
import re
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def scrape_tdiscount_final():
    print("Launching Tdiscount Final Scraper (Auto-Proceed)...")
    
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-popup-blocking')
    
    driver = uc.Chrome(options=options, use_subprocess=True)

    # DIRECT NAVIGATION
    start_url = "https://tdiscount.tn/store/tdiscount/section/375"
    print(f"   🌐 Navigating to: {start_url}")
    try:
        driver.get(start_url)
    except:
        pass
        
    print("\n" + "!"*30)
    print("   WAITING 30 SECONDS FOR MANUAL CLOUDFLARE CLEARING")
    print("   Please ensure you verify you are human if asked.")
    print("   The script will AUTOMATICALLY proceed after 30s.")
    print("!"*30 + "\n")
    
    for i in range(30, 0, -5):
        print(f"   Resuming in {i} seconds...")
        time.sleep(5)
        
    print("   🚀 STARTING EXTRACTION NOW...")
    
    all_products = []
    page_number = 1
    max_pages = 10
    
    while page_number <= max_pages:
        print(f"\n   📄 Scraping Page {page_number}...")
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # WooCommerce Selectors
        items = driver.execute_script("""
            var results = [];
            var boxes = document.querySelectorAll('li.product, div.product-inner, .product-item, .type-product');
            
            boxes.forEach(box => {
                try {
                    var nameEl = box.querySelector('.woocommerce-loop-product__title, .product-title a, h2 a');
                    var name = nameEl ? nameEl.innerText.trim() : "";
                    var link = nameEl ? (nameEl.href || nameEl.parentNode.href) : "";
                    
                    var priceEl = box.querySelector('.price');
                    var priceText = priceEl ? priceEl.innerText : "0";
                    
                    var imgEl = box.querySelector('img.attachment-woocommerce_thumbnail, img.product-image-photo, .product-thumbnail img');
                    var imgSrc = imgEl ? (imgEl.getAttribute('data-src') || imgEl.src) : "";
                    
                    var vendorEl = box.querySelector('.sold-by-meta a, .vendor-name a, .seller-name a');
                    var vendor = vendorEl ? vendorEl.innerText.trim() : "Tdiscount";

                    if (name) {
                        results.push({
                            name: name,
                            link: link,
                            price_raw: priceText,
                            image: imgSrc,
                            vendor: vendor
                        });
                    }
                } catch(e) {}
            });
            return results;
        """)
        
        print(f"     Page Title: {driver.title}")
        
        if not items:
            print("     ⚠️ No items found. Checking one more time with diverse selectors...")
            # Fallback for "Section" pages which might just be list items
            items = driver.execute_script("""
                var results = [];
                var boxes = document.querySelectorAll('li.product-item'); // Fallback to Magento-ish just in case
                boxes.forEach(box => {
                     // ... simple extraction ...
                     var nameEl = box.querySelector('a.product-item-link');
                     if(nameEl) {
                         results.push({
                             name: nameEl.innerText, 
                             link: nameEl.href, 
                             price_raw: box.innerText, 
                             image: "", 
                             vendor: "Tdiscount"
                         });
                     }
                });
                return results;
            """)
            
        if not items:
            print("     ❌ Still no items. Dumping HTML to debug_final.html and stopping.")
            with open("debug_final.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            break
        
        print(f"     🎯 Found {len(items)} items. Parsing...")
        
        count_saved = 0
        for item in items:
            try:
                name = item['name']
                link = item['link']
                raw_price = item['price_raw']
                img = item['image']
                vendor = item['vendor']
                
                clean_p = raw_price.upper().replace('TND','').replace('DT','').replace('&NBSP;','').replace(' ','').replace(',', '.').strip()
                clean_p = "".join([c for c in clean_p if c.isdigit() or c == '.'])
                try:
                    price_val = float(clean_p)
                    price_str = f"{price_val:.3f} TND"
                except:
                   price_str = "N/A"

                all_products.append({
                    "name": name,
                    "price": price_str,
                    "image": img,
                    "link": link,
                    "vendor": vendor,
                    "source": "Tdiscount"
                })
                count_saved += 1
            except:
                pass
        
        print(f"     ✅ Extracted {count_saved} products.")
        
        # Pagination
        try:
            print("     👀 Checking for next page...")
            has_next = driver.execute_script("""
                var nextBtn = document.querySelector('a.next.page-numbers, .pagination .next, a.next');
                if (nextBtn) {
                    nextBtn.click();
                    return true;
                }
                return false;
            """)
            
            if has_next:
                print(f"     ➡️  Moving to next page...")
                time.sleep(5)
                page_number += 1
            else:
                print("     🛑 No next page.")
                break
        except:
             break

    if all_products:
        print(f"\n🎉 Finished. Total: {len(all_products)}")
        with open("src/data/tdiscount_products.json", "w", encoding="utf-8") as f:
            json.dump(all_products, f, indent=4, ensure_ascii=False)
        print("📁 Saved to src/data/tdiscount_products.json")
    else:
        print("⚠️ No data obtained.")

    driver.quit()

if __name__ == "__main__":
    scrape_tdiscount_final()
