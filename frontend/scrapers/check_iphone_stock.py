from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)

try:
    url = "https://wiki.tn/iphone"
    print(f"Connecting to {url}...")
    driver.get(url)
    
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
    time.sleep(1)
    
    cards = driver.find_elements(By.CSS_SELECTOR, ".product-card")
    print(f"Found {len(cards)} cards on Page 1.")
    
    counts = {}
    
    for i, card in enumerate(cards):
        try:
            title = card.find_element(By.CSS_SELECTOR, ".product-card__title a").text
            
            # Try badge
            try:
                stock_text = card.find_element(By.CSS_SELECTOR, ".stock-status-badge").text
            except:
                try:
                    stock_text = card.find_element(By.CSS_SELECTOR, ".stock").text
                except:
                    stock_text = "Unknown Status"
            
            status = stock_text.strip()
            counts[status] = counts.get(status, 0) + 1
            print(f"  {i+1}. {title[:30]}... -> [{status}]")
            
        except Exception as e:
            print(f"  Error reading card {i}: {e}")

    print("\nSummary of Statuses:")
    for k, v in counts.items():
        print(f"  {k}: {v}")

except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()
