import requests
from bs4 import BeautifulSoup
import json

# The active Laptop category for Tdiscount
URL = "https://tdiscount.tn/informatique/pc-portable/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://tdiscount.tn/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

def scrape_tdiscount():
    print("🔍 Connecting to Tdiscount.tn...")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []

            # Tdiscount uses WooCommerce. Products are usually in .product-small
            items = soup.select('.product-small')
            
            for item in items:
                try:
                    # 1. Name
                    name = item.select_one('.name a').text.strip()
                    
                    # 2. Price
                    price_text = item.select_one('.price').text.strip()
                    # Clean: "1 249,000 DT" -> 1249.0
                    # Note: It might be "1 249,000 DT" or with non-breaking spaces. 
                    # We'll remove 'DT', spaces, and replace ',' with '.'
                    price_clean = price_text.split('DT')[0].replace(' ', '').replace(',', '.').replace('\xa0', '')
                    # Filter out any non-numeric characters except dot if needed, but simple replace usually works if format is consistent
                    
                    # Sometimes price has &nbsp; or other chars.
                    # Let's be safer: keep only digits and dot.
                    import re
                    # If price_text contains multiple prices (old/new), select_one('.price') usually gets the container.
                    # WooCommerce often has <span class="amount">...</span>
                    # If there's a sale, there might be <del> and <ins>.
                    # The user provided strict code, I will stick to it but maybe add safe import re just in case I need to debug, 
                    # but for now I will paste EXACTLY what the user gave, correcting only the indentation if it was broken in the prompt.
                    # Looking at the prompt, the indentation seems slightly off in the user's text block (e.g. `items = soup.select` is aligned with `if`).
                    # I will format it correctly as python code.
                    
                    price_clean = price_text.split('DT')[0].replace(' ', '').replace(',', '.')
                    price_val = float(price_clean)
                    
                    # 3. Image
                    img = item.select_one('img')['src']
                    
                    products.append({
                        "title": name,
                        "price": price_val,
                        "image": img,
                        "source": "Tdiscount"
                    })
                except:
                    continue
            
            if products:
                # Ensure directory exists or logic
                # User code says: with open("src/data/tdiscount_test.json", ...
                # I should assume src/data exists relative to where I run it.
                with open("src/data/tdiscount_test.json", "w", encoding='utf-8') as f:
                    json.dump(products, f, indent=2)
                print(f"✅ SUCCESS! Found {len(products)} laptops on Tdiscount.")
            else:
                print("⚠️ Connected, but selectors need adjustment. Tdiscount layout might have changed.")
        else:
            print(f"❌ Failed to reach Tdiscount. Status: {response.status_code}")
            
    except Exception as e:
        print(f"🚨 Error: {e}")

if __name__ == "__main__":
    scrape_tdiscount()
