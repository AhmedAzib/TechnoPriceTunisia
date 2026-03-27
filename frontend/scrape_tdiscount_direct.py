import time
import re
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def scrape_tdiscount_direct():
    print("Launching Tdiscount Direct Scraper...")
    
    # 1. INIT DRIVER
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-popup-blocking')
    
    # use_subprocess=True for stability
    driver = uc.Chrome(options=options, use_subprocess=True)

    # USER PROVIDED URLs
    target_urls = [
        "https://tdiscount.tn/store/tdiscount/section/375", # Main laptops
        "https://tdiscount.tn/store/tdiscount/section/269"  # More models
    ]
    
    all_products = []
    
    for i, url in enumerate(target_urls):
        print(f"\n   🌐 Navigating to URL {i+1}: {url}")
        try:
            driver.get(url)
        except Exception as e:
            print(f"   ⚠️ Navigation Error: {e}")
            continue

        time.sleep(5)
        
        # 2. MANUAL CHECK (Only needed mainly for first URL or if Cloudflare appears)
        if i == 0:
            print("\n" + "!"*20)
            print("ACTION REQUIRED: Check the Browser Window")
            print("1. If you see 'Just a moment...' (Cloudflare), please click the checkbox.")
            print("2. Wait until you see the products.")
            print("!"*20 + "\n")
            input("Press ENTER here -> IN THIS TERMINAL <- once products are visible...")
        else:
            print("   Assuming Cloudflare is passed. Waiting 5s...")
            time.sleep(5)

        # 3. SCRAPE LOOP FOR THIS URL (Pagination support)
        # These section pages might have pagination. Let's try to handle it.
        page_number = 1
        max_pages_per_url = 5 # Safety limit
        
        while page_number <= max_pages_per_url:
            print(f"   📄 Scraping Page {page_number} of current section...")
            
            # Scroll to trigger lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 3. JS INJECTION TO EXTRACT DATA + VENDU PAR
            items = driver.execute_script("""
                var results = [];
                // Selectors suitable for generic lists
                var boxes = document.querySelectorAll('li.product-item, .product-item-info');
                
                boxes.forEach(box => {
                    try {
                        // Name & Link
                        var nameEl = box.querySelector('a.product-item-link');
                        
                        // Price
                        var priceText = "0";
                        var priceEl = box.querySelector('[data-price-amount]'); 
                        if (priceEl) {
                            priceText = priceEl.getAttribute('data-price-amount');
                        } else {
                            var visualPrice = box.querySelector('.price');
                            if (visualPrice) priceText = visualPrice.innerText;
                        }
                        
                        // Image
                        var imgEl = box.querySelector('img.product-image-photo');
                        var imgSrc = imgEl ? imgEl.src : "";
                        
                        // Vendu Par Extraction
                        // Often inside some text like "Vendu par :"
                        var soldBy = "Tdiscount"; // Default
                        // Look for any element containing "Vendu par"
                        // This selector is a guess, usually it's in .product-item-details
                        var details = box.querySelector('.product-item-details');
                        if (details) {
                             var text = details.innerText;
                             // Regex in JS? Or just let Python handle it.
                             // Let's try to find a specific element if possible, or just grab all text
                        }
                        // We will return the whole innerText of details to parse in Python for "Vendu par"
                        var detailsText = details ? details.innerText : "";

                        if (nameEl) {
                            results.push({
                                name: nameEl.innerText.trim(),
                                link: nameEl.href,
                                price_raw: priceText,
                                image: imgSrc,
                                details_text: detailsText
                            });
                        }
                    } catch(e) {}
                });
                return results;
            """)
            
            print(f"     Page Title: {driver.title}")
            
            if not items:
                print("     ⚠️ No items found on this page.")
                print("     📸 Saving page source to 'debug_tdiscount.html' for inspection...")
                with open("debug_tdiscount.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print("     Moving to next URL or stopping.")
                break
            
            print(f"     🎯 Found {len(items)} items. Parsing...")
            
            count_saved = 0
            for item in items:
                try:
                    name = item['name']
                    link = item['link']
                    raw_price = str(item['price_raw'])
                    img = item['image']
                    details_text = item['details_text']
                    
                    # Clean Price
                    clean_p = raw_price.upper().replace('TND','').replace('DT','').replace(' ','').replace(',', '.').strip()
                    clean_p = "".join([c for c in clean_p if c.isdigit() or c == '.'])
                    try:
                        price_val = float(clean_p)
                        price_str = f"{price_val:.3f} TND"
                    except:
                        price_str = "N/A"
                    
                    # Vendu Par Logic
                    vendor = "Tdiscount" # Default
                    # Look for "Vendu par" in details_text
                    # Case insensitive search
                    v_match = re.search(r'Vendu par\s*:?\s*(.*?)(?:\n|$)', details_text, re.IGNORECASE)
                    if v_match:
                        vendor = v_match.group(1).strip()
                    
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
            
            # Pagination Logic for these specific pages
            # Attempt to find next button
            try:
                print("     👀 Checking for next page...")
                has_next = driver.execute_script("""
                    var nextBtn = document.querySelector('a.action.next, .pages-item-next a');
                    if (nextBtn && !nextBtn.classList.contains('disabled')) {
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

    # Save Results
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
    scrape_tdiscount_direct()
