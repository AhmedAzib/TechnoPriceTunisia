from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
# options.add_argument("--headless=new") # Run visible to be sure (if compatible with environment?)
# User environment is windows, likely can run headless or not. Safe to run headless usually.
options.add_argument("--headless=new") 
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)
try:
    print("Navigating...")
    driver.get("https://www.mytek.tn/smartphone.html")
    time.sleep(10) # Wait 10s for everything
    
    print("Taking screenshot...")
    driver.save_screenshot("debug_screenshot.png")
    
    print("Saving HTML...")
    with open("debug_selenium.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
        
    print("Done.")
except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()
