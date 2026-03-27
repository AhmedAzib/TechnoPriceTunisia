import time
import re
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def scrape_tdiscount_woo():
    print("Launching Tdiscount WooCommerce Scraper...")
    
    # 1. INIT DRIVER
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-popup-blocking')
    
    driver = uc.Chrome(options=options, use_subprocess=True)

    print("   🌐 Navigating to Tdiscount...")
    try:
        driver.get("https://tdiscount.tn/")
    except:
        pass
        
    time.sleep(3)

    # 2. MANUAL NAVIGATION PROMPT
    print("\n" + "!"*20)
    print("ACTION REQUIRED: Navigate to the desired Product Section")
    print("1. Please navigate manually in the browser to the page with Laptops.")
    print("   (Use the links you trust: e.g. store/tdiscount/section/375)")
    print("2. If Cloudflare appears, solve it.")
    print("3. Wait until products are visible on the screen.")
    print("!"*20 + "\n")
    
    input("Press ENTER here -> IN THIS TERMINAL <- once you see the products...")
    
    all_products = []
    
    # We will scrape the CURRENT page, and potentially next pages if pagination exists
    page_number = 1
    max_pages = 10
    
    while page_number <= max_pages:
        print(f"\n   📄 Scraping Page {page_number}...")
        
        # Scroll
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # 3. JS INJECTION - WOOCOMMERCE SELECTORS
        items = driver.execute_script("""
            var results = [];
            
            // WooCommerce generic product items
            // Martfury theme often uses .product element
            var boxes = document.querySelectorAll('li.product, div.product-inner, .product-item');
            
            if (boxes.length === 0) {
                // Try broader selector
                boxes = document.querySelectorAll('.type-product');
            }

            boxes.forEach(box => {
                try {
                    // Title
                    var nameEl = box.querySelector('.woocommerce-loop-product__title, .product-title a, h2 a');
                    var name = nameEl ? nameEl.innerText.trim() : "";
                    var link = nameEl ? (nameEl.href || nameEl.parentNode.href) : "";
                    
                    // Price
                    var priceEl = box.querySelector('.price');
                    var priceText = priceEl ? priceEl.innerText : "0";
                    
                    // Image
                    var imgEl = box.querySelector('img.attachment-woocommerce_thumbnail, img.product-image-photo, .product-thumbnail img');
                    var imgSrc = imgEl ? (imgEl.getAttribute('data-src') || imgEl.src) : "";
                    
                    // Vendor (Dokan)
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
            print("     ⚠️ No items found on this page.")
            print("     (Saving Html dump just in case)")
            with open("debug_tdiscount_woo.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            
            # Retry mechanism? Or just ask user?
            retry = input("     Retry scraping this page? (y/n): ")
            if retry.lower() == 'y':
                continue
            else:
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
                
                # Clean Price
                # Usually "1 200,000 TND"
                clean_p = raw_price.upper().replace('TND','').replace('DT','').replace('&NBSP;','').replace(' ','').replace(',', '.').strip()
                # Keep digits and dot
                clean_p = "".join([c for c in clean_p if c.isdigit() or c == '.'])
                
                try:
                    price_val = float(clean_p)
                    price_str = f"{price_val:.3f} TND"
                except:
                   # Sometimes price is a range or empty
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
        
        # 4. Pagination
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
                print("     🛑 No next page found. Finishing.")
                break
        except:
             break

    # Save
    if all_products:
        print(f"\n🎉 Scraper Finished. Total Items: {len(all_products)}")
        with open("src/data/tdiscount_products.json", "w", encoding="utf-8") as f:
            json.dump(all_products, f, indent=4, ensure_ascii=False)
        print("📁 Data saved to: src/data/tdiscount_products.json")
    else:
        print("⚠️ No products obtained.")

    print("Closing browser...")
    driver.quit()

if __name__ == "__main__":
    scrape_tdiscount_woo()
