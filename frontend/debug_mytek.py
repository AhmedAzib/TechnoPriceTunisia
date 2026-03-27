
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def debug():
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://www.mytek.tn/smartphone")
        time.sleep(5)
        with open("mytek_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Dumped HTML to mytek_debug.html")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug()
