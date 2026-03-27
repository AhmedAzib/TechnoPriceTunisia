
import time
import undetected_chromedriver as uc

def diagnose():
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-popup-blocking')
    
    print("Launching Diagnostic Browser...")
    driver = uc.Chrome(options=options, use_subprocess=True)
    
    try:
        driver.get("https://www.mytek.tn")
        url = "https://www.mytek.tn/informatique/ordinateurs-portables/pc-portable.html?p=1" # This line remains as per the instruction's implicit scope
        print(f"Navigating to {url}...")
        driver.get(url)
        
        print("Waiting 10s for load...")
        time.sleep(10)
        
        title = driver.title
        print(f"Page Title: {title}")
        
        driver.save_screenshot("mytek_diag.png")
        print("Saved screenshot to mytek_diag.png")
        
        with open("mytek_diag.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved HTML to mytek_diag.html")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    diagnose()
