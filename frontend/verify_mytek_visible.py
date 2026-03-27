from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
# options.add_argument("--headless=new") # DISABLED HEADLESS
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

print("Launching Visible Chrome...")
driver = webdriver.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

try:
    url = "https://www.mytek.tn/telephonie-tunisie/smartphone-mobile-tunisie/smartphone.html"
    print(f"Loading {url}...")
    driver.get(url)
    time.sleep(10) # Give it time to load visually
    
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
