import time
import re
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def scrape_tdiscount_v2():
    print("Launching Tdiscount Scraper V2 (MyTek Strategy)...")
    
    # 1. INIT DRIVER WITH STABILITY OPTIONS (Copied from MyTek Scraper)
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-popup-blocking')
    
    # use_subprocess=True is the key stability factor from the MyTek script
    driver = uc.Chrome(options=options, use_subprocess=True)
    
    print("   🌐 Navigating to Tdiscount Homepage...")
    try:
        driver.get("https://tdiscount.tn/")
    except Exception as e:
        print(f"   ⚠️ Initial Navigation Error: {e}")
        # Retry once
        time.sleep(2)
        try:
            driver.get("https://tdiscount.tn/")
        except:
            pass

    time.sleep(3)
    
    # 2. MANUAL NAVIGATION PROMPT (Crucial for bypassing Cloudflare Loop)
    print("\n" + "!"*20)
    print("ACTION REQUIRED: Please Navigate to the Laptops Page")
    print("1. Go to 'Informatique' -> 'Ordinateur Portable' (or your target category).")
    print("2. If Cloudflare ('Just a moment') appears, please solve the captcha.")
    print("3. Wait until you see the list of products.")
    print("!"*20 + "\n")
    
    # We will wait for user input, just like the MyTek scraper
    # However, to be "smoother" as requested, we can also poll the URL to see if it looks right, 
    # but the manual confirmation is the safest "MyTek way".
    input("Press ENTER here -> IN THIS TERMINAL <- when the Product List is visible on screen...")
    
    all_products = []
    page_number = 1
    # Limit pages (adjust as needed)
    max_pages = 10 
    
    while page_number <= max_pages:
        print(f"\n   📄 Scraping Page {page_number}...")
        
        # Scroll reasonably to trigger lazy loads if any
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # 3. JS INJECTION (Robust extraction - Adapted from MyTek)
        # Tdiscount uses similar Magento structure: .product-item-info, .product-item-link, [data-price-amount]
        items = driver.execute_script("""
            var results = [];
            // Selectors for Tdiscount (Standard Magento 2)
            var boxes = document.querySelectorAll('li.product-item, .product-item-info');
            
            boxes.forEach(box => {
                try {
                    // Name & Link
                    var nameEl = box.querySelector('a.product-item-link');
                    
                    // Price
                    var priceText = "0";
                    // Try data attribute first (most accurate)
                    var priceEl = box.querySelector('[data-price-amount]'); 
                    if (priceEl) {
                        priceText = priceEl.getAttribute('data-price-amount');
                    } else {
                        // Fallback to text
                        var visualPrice = box.querySelector('.price');
                        if (visualPrice) priceText = visualPrice.innerText;
                    }
                    
                    // Image
                    var imgEl = box.querySelector('img.product-image-photo');
                    var imgSrc = imgEl ? imgEl.src : "";

                    if (nameEl) {
                        results.push({
                            name: nameEl.innerText.trim(),
                            link: nameEl.href,
                            price_raw: priceText,
                            image: imgSrc
                        });
                    }
                } catch(e) {}
            });
            return results;
        """)
        
        if not items:
            print("     ⚠️ No items found on this page via JS.")
            # Maybe we are stuck?
            input("     Press ENTER to try scraping this page again (maybe it didn't load), or Ctrl+C to quit...")
            continue
        
        print(f"     🎯 Found {len(items)} items. Processing...")
        
        count_saved = 0
        for item in items:
            try:
                name = item['name']
                link = item['link']
                raw_price = str(item['price_raw'])
                img = item['image']
                
                # Cleaning Price
                # Remove TND, DT, spaces, replace comma with dot
                clean_p = raw_price.upper().replace('TND','').replace('DT','').replace(' ','').replace(',', '.').strip()
                # Remove non-numeric except dot
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
                    "source": "Tdiscount"
                })
                count_saved += 1
            except:
                pass
                
        print(f"     ✅ Extracted {count_saved} products.")
        
        # 4. Pagination (MyTek Style)
        # Find 'Next' button
        # Tdiscount usually has 'a.action.next'
        
        try:
            print("     👀 Looking for Next Page...")
            # We use JS to find and click to avoid interception
            has_next = driver.execute_script("""
                var nextBtn = document.querySelector('a.action.next');
                if (nextBtn && !nextBtn.classList.contains('disabled')) {
                    nextBtn.click();
                    return true;
                }
                return false;
            """)
            
            if has_next:
                print(f"     ➡️  Moving to Page {page_number + 1}...")
                time.sleep(5) # Wait for load
                page_number += 1
            else:
                print("     🛑 No 'Next' button found. Stopping.")
                break
        except Exception as e:
            print(f"     ⚠️ Pagination Error: {e}")
            break

    # 5. Save Results
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
    scrape_tdiscount_v2()
