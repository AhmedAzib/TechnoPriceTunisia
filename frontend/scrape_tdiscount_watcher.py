import time
import json
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def scrape_tdiscount_ultimate():
    print("🚀 Launching Tdiscount Ultimate Watcher...")
    print("   This script will visit multiple sections to find laptops.")
    
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--start-maximized')
    
    # Keep browser open is handled by the script not quitting immediately
    driver = uc.Chrome(options=options, use_subprocess=True)
    
    # List of URLs to scrape
    target_urls = [
         "https://tdiscount.tn/store/tdiscount/section/375", # Main Laptops
         "https://tdiscount.tn/store/tdiscount/section/269", # Other models
         "https://tdiscount.tn/informatique/ordinateur-portable" # General Category
    ]
    
    all_products = []
    
    for url in target_urls:
        print(f"\n   🌐 Navigating to: {url}")
        try:
            driver.get(url)
        except:
            print("   (Navigation glitch, continuing)")

        print("   👀 Waiting for products (solve Cloudflare if needed)...")
        
        # Wait loop
        found_products = False
        max_wait = 30 # seconds
        for i in range(max_wait):
            val = driver.execute_script("return document.querySelectorAll('li.product, .product-item').length")
            if val > 0:
                found_products = True
                break
            time.sleep(1)
            
        if not found_products:
            print("   ⚠️ No products found here after 30s. Moving to next URL.")
            continue
            
        print("   ✅ Products detected! Scraping...")
        
        # Pagination Loop for this URL
        page = 1
        while True:
            print(f"     Processing Page {page}...")
            # Scroll
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Extract
            items = driver.execute_script("""
                var results = [];
                var boxes = document.querySelectorAll('li.product, .product-item, .product-inner');
                
                boxes.forEach(box => {
                    try {
                        var nameEl = box.querySelector('.woocommerce-loop-product__title, h2, h3, a.product-item-link');
                        var name = nameEl ? nameEl.innerText.trim() : "";
                        
                        var linkEl = box.querySelector('a.woocommerce-loop-product__link, a.product-item-link') || box.querySelector('a');
                        var link = linkEl ? linkEl.href : "";
                        
                        // Price often has duplicated text for sales (old new). 
                        // We grab the INS HTML to get the sale price if exists, or just innerText
                        var priceEl = box.querySelector('.price');
                        var priceText = priceEl ? priceEl.innerText : "0";
                        
                        // Try to find specific <ins> tag for sale price
                        var insPrice = box.querySelector('ins .amount');
                        if (insPrice) priceText = insPrice.innerText;
                        
                        // Or <span class="amount">
                        else {
                             var amount = box.querySelector('.amount');
                             if(amount) priceText = amount.innerText;
                        }

                        var imgEl = box.querySelector('img');
                        var imgSrc = imgEl ? (imgEl.getAttribute('data-src') || imgEl.src) : "";

                        if (name && link) {
                            results.push({
                                name: name,
                                link: link,
                                price_raw: priceText,
                                image: imgSrc,
                                vendor: "Tdiscount"
                            });
                        }
                    } catch(e) {}
                });
                return results;
            """)
            
            for item in items:
                # Deduplicate
                if not any(p['link'] == item['link'] for p in all_products):
                    # Clean Price Logic
                    raw = item['price_raw']
                    # Keep digits and dot, but watch out for thousands separators
                    # "2 999.000 TND" -> 2999.000
                    clean = raw.replace(' ', '').replace('TND', '').replace('DT', '').replace('&nbsp;', '')
                    # Replace comma with dot if it acts as decimal, or remove if thousand
                    # Tunisian: 1.200,000 or 1 200.000 -> usually 3 decimals
                    # Simple regex for first float ref
                    match = re.search(r'[\d\s\.,]+', raw)
                    if match:
                        # Normalize: remove spaces, replace comma with dot
                        val_str = match.group(0).replace(' ', '').replace(',', '.')
                        # If multiple points, keep last one? 
                        # 2.999.000 -> 2999.000
                        if val_str.count('.') > 1:
                            val_str = val_str.replace('.', '', val_str.count('.') - 1)
                        
                        final_price = val_str + " TND"
                    else:
                        final_price = "N/A"

                    all_products.append({
                        "name": item['name'],
                        "price": final_price,
                        "image": item['image'],
                        "link": item['link'],
                        "vendor": "Tdiscount",
                        "source": "Tdiscount"
                    })
            
            print(f"     found {len(items)} items. Total unique: {len(all_products)}")
            
            # Next Page?
            has_next = driver.execute_script("""
                var next = document.querySelector('a.next, a.next.page-numbers');
                if (next) { next.click(); return true; }
                return false;
            """)
            if has_next:
                print("     ➡️ Moving to next page...")
                time.sleep(4)
                page += 1
            else:
                break
                
    # Save
    if all_products:
        print(f"\n💾 SAVING {len(all_products)} PRODUCTS...")
        with open("src/data/tdiscount_products.json", "w", encoding="utf-8") as f:
            json.dump(all_products, f, indent=4, ensure_ascii=False)
        print("✅ DONE.")
    else:
        print("⚠️ No products found in any section.")

    print("\n" + "="*40)
    print("   ✅ SCRAPING COMPLETED.")
    print("   The browser will remain open for you to verify.")
    print("   Press ENTER in this terminal to close it.")
    print("="*40 + "\n")
    
    input()
    driver.quit()

if __name__ == "__main__":
    scrape_tdiscount_ultimate()
