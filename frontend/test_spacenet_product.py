
from curl_cffi import requests
from bs4 import BeautifulSoup

def test_product_scrape_meta():
    url = "https://spacenet.tn/pc-portable-gamer-tunisie/40376-pc-portable-dell-5500-g5-i5-10300h-8go-1to-ssd-noir.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        print(f"Fetching {url}...")
        response = requests.get(url, headers=headers, impersonate="chrome110", timeout=20)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Meta Extraction Strategy
        
        # Title
        title_tag = soup.find("meta", property="og:title")
        title = title_tag["content"] if title_tag else "No Title"
        
        # Price
        price_tag = soup.find("meta", property="product:price:amount")
        price = price_tag["content"] if price_tag else "0.000"
        
        # Image
        image_tag = soup.find("meta", property="og:image")
        image = image_tag["content"] if image_tag else ""
        
        # Ref / Brand
        brand_tag = soup.find("meta", property="product:brand")
        brand = brand_tag["content"] if brand_tag else "Unknown"

        ref_tag = soup.find("meta", property="product:retailer_item_id") 
        ref = ref_tag["content"] if ref_tag else ""

        link = url

        # 2. Filter Logic (Simulation)
        exclude_keywords = ['chargeur', 'sacoche', 'souris', 'clavier', 'casque', 'cable', 'adaptateur', 'support', 'refroidisseur', 'micro', 'protection', 'etui']
        
        should_skip = False
        title_lower = title.lower()
        if any(bad in title_lower for bad in exclude_keywords):
             should_skip = True
             print(f"DEBUG: Would SKIP based on keywords.")

        # 3. Formatting
        # Price needs to be formatted as "3 450.000 TND" or similar if we want consistency, but raw float is fine too.
        # The user's system likely expects consistent strings. "2999.00" -> "2 999.000 TND" maybe?
        # For now, I'll keep it as scraped string + " TND".

        print("-" * 20)
        print(f"Title: {title}")
        print(f"Price: {price} TND")
        print(f"Image: {image}")
        print(f"Ref:   {ref}")
        print(f"Brand: {brand}")
        print(f"Skip?: {should_skip}")
        print("-" * 20)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_product_scrape_meta()
