import os
import json
import re
import undetected_chromedriver as uc

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'src', 'data', 'mytek_laptops.json')

def scrape_and_check():
    print("Debug: Checking Mac Consistency...")
    
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    existing_links = {item['link'] for item in data}
    
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = uc.Chrome(options=options)
    
    url = "https://www.mytek.tn/informatique/ordinateurs-portables/mac.html?p=1"
    driver.get(url)
    import time
    time.sleep(5)
    
    products = driver.execute_script("""
        const items = [];
        document.querySelectorAll('div.product-container').forEach((el) => {
            const nameEl = el.querySelector('.product-item-name a');
            if (nameEl) {
                items.push({
                    title: nameEl.innerText.trim(),
                    link: nameEl.href
                });
            }
        });
        return items;
    """)
    
    driver.quit()
    
    print(f"Web Page has {len(products)} MacBooks.")
    
    found_count = 0
    missing_count = 0
    
    for p in products:
        if p['link'] in existing_links:
            print(f"[OK] In Database: {p['title']}")
            found_count += 1
        else:
            print(f"[MISSING] NOT in Database: {p['title']} ({p['link']})")
            missing_count += 1
            
    print(f"\nSummary: Found {found_count} matching items. Missing {missing_count} items.")

if __name__ == "__main__":
    scrape_and_check()
