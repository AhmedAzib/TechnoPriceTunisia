
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def dump_source():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    try:
        url = "https://tunisiatech.tn/57-pc-portable"
        print(f"Navigating to {url}...")
        driver.get(url)
        time.sleep(5)  # Wait for load
        
        with open("techtunisia_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Drafted source to techtunisia_debug.html")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    dump_source()
