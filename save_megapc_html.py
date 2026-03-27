import undetected_chromedriver as uc
import time

url = "https://megapc.tn/shop/PC%20PORTABLE/PC%20PORTABLE%20GAMER"
options = uc.ChromeOptions()
options.add_argument("--disable-gpu")
# options.add_argument("--headless=new") 
driver = uc.Chrome(options=options)

try:
    print(f"Opening {url}...")
    driver.get(url)
    time.sleep(10) # wait for load/cloudflare
    
    with open("megapc_debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved megapc_debug.html")
    
finally:
    driver.quit()
