from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def debug_standard():
    print("Debugging Standard Selenium...")
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    # options.add_argument("--headless=new")
    
    try:
        driver = webdriver.Chrome(options=options)
        
        url = "https://megapc.tn/shop/category/ordinateur-portable"
        driver.get(url)
        time.sleep(10)
        
        print(f"Title: {driver.title}")
        
        articles = driver.find_elements(By.CSS_SELECTOR, "article.product-card")
        print(f"Articles: {len(articles)}")
        
        if articles:
            print(articles[0].text[:100])
        else:
            print("No articles. Dumping body:")
            print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML")[:2000])

            
        driver.quit()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_standard()
