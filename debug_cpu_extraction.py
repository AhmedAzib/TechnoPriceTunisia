from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Use a URL that definitely exists in the JSON
URL = "https://www.mytek.tn/smartphone-xiaomi-redmi-13-8go-256go-noir.html" 
# Alternative: "https://www.mytek.tn/smartphone-samsung-galaxy-a16-12go-128go-gris.html"

def debug_cpu():
    print("Launching Selenium for CPU Debug...", flush=True)
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        print(f"Navigating to {URL}", flush=True)
        driver.get(URL)
        time.sleep(5)
        
        # Check title to verify 404
        print(f"Page Title: {driver.title}", flush=True)
        
        source = driver.page_source
        if "404 Not Found" in source or "Whoops, our bad" in source:
             print("ERROR: 404 Not Found encountered.", flush=True)
        else:
             print("Page loaded successfully.", flush=True)
             with open("debug_product.html", "w", encoding="utf-8") as f:
                 f.write(source)
             print("Saved debug_product.html", flush=True)
             
    except Exception as e:
        print(f"Error: {e}", flush=True)
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_cpu()
