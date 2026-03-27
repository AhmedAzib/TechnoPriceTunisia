
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import json

def test_access():
    print("Initializing Undetected ChromeDriver (Auto Version)...")
    options = uc.ChromeOptions()
    # options.add_argument('--headless=new') # Headless often detected, let's try standard first to debug if needed, or stick to headless if user insists.
    # The user insists on "automatic" and "no clicking". Headless is best for "no clicking" visibility.
    options.add_argument('--headless=new')
    
    try:
        # Remove version_main to let it auto-find
        driver = uc.Chrome(options=options) 
        print("Driver launched successfully.")
        
        driver.get("https://tdiscount.tn/")
        print("Navigating...")
        
        time.sleep(15) # Generous wait for Cloudflare
        
        print(f"Title: {driver.title}")
        
        if "Just a moment" in driver.title:
            print("Status: BLOCKED (Cloudflare Challenge)")
        else:
            print("Status: SUCCESS (Page accessed)")
            
            # Save cookies
            cookies = driver.get_cookies()
            with open("tdiscount_cookies.json", "w") as f:
                json.dump(cookies, f)
            print(f"Cookies saved: {len(cookies)}")
            
            # Additional Challenge: Check sitemap in footer?
            # Or try to get category URL
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    test_access()
