from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--headless=new")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)
try:
    url = "https://www.mytek.tn/telephonie-tunisie/smartphone-mobile-tunisie/iphone.html"
    print(f"Loading {url}...")
    driver.get(url)
    time.sleep(5)
    
    with open("mytek_iphone_v2.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved mytek_iphone_v2.html")
    
    # Try the JS extraction logic
    items = driver.execute_script("""
        var results = [];
        var boxes = document.querySelectorAll('li.product-item, div.product-item');
        
        boxes.forEach(box => {
            try {
                var nameEl = box.querySelector('a.product-item-link');
                if (nameEl) {
                     results.push(nameEl.innerText.trim());
                }
            } catch(e) {}
        });
        return results;
    """)
    
    print(f"Found {len(items)} items:")
    for i in items[:5]:
        print(f" - {i}")

except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()
