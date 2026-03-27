
import undetected_chromedriver as uc
import time
import json
import os

def fetch_sitemap():
    print("Launching Driver for Sitemap...")
    options = uc.ChromeOptions()
    options.add_argument('--headless=new')
    
    driver = uc.Chrome(options=options)
    
    try:
        # 1. Init Session
        driver.get("https://tdiscount.tn/")
        time.sleep(10)
        
        # 2. Try Sitemaps
        candidates = [
            "https://tdiscount.tn/sitemap.xml",
            "https://tdiscount.tn/1_index_sitemap.xml",
            "https://tdiscount.tn/index_sitemap.xml"
        ]
        
        success = False
        for url in candidates:
            print(f"Trying {url}...")
            driver.get(url)
            time.sleep(5)
            
            content = driver.page_source
            if "urlset" in content or "sitemapindex" in content:
                print("SUCCESS: Sitemap found!")
                filename = "tdiscount_" + url.split("/")[-1]
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
                success = True
                break
            else:
                print("Not a valid sitemap.")
                
        if not success:
            print("FAILED to find sitemap. Page source dump:")
            print(driver.page_source[:500])
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_sitemap()
