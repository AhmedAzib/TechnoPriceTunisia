from selenium import webdriver
from selenium.webdriver.common.by import By
import time

options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

try:
    # Go to the main category page again
    url = "https://megapc.tn/shop/Nos-Categories/PC%20PORTABLE"
    print(f"Visiting {url}")
    driver.get(url)
    time.sleep(5)
    
    print("Links on Main PC Portable Page:")
    links = driver.find_elements(By.TAG_NAME, "a")
    for link in links:
        href = link.get_attribute("href")
        text = link.text.strip()
        if href and ("portable" in href.lower() or "macbook" in href.lower() or "laptop" in href.lower()):
            print(f"POSSIBLE: {text} -> {href}")

    # Also check the Sidebar if it exists
    print("\nChecking Sidebar / Brands...")
    # Hypothetical sidebar Check
    # We'll just look for everything
    
    # Try direct access to MacBook
    mac_url = "https://megapc.tn/shop/PC%20PORTABLE/MACBOOK"
    print(f"\nChecking Direct: {mac_url}")
    driver.get(mac_url)
    time.sleep(3)
    if "404" not in driver.title and len(driver.find_elements(By.TAG_NAME, "img")) > 5:
        print("MACBOOK PAGE EXISTS and has images")
    else:
        print("MACBOOK Page might be empty or 404")

finally:
    driver.quit()
