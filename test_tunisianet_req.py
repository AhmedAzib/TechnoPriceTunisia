import requests
from bs4 import BeautifulSoup

url = "https://www.tunisianet.com.tn/421-processeur?order=product.price.asc"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    print(f"Checking URL: {url}")
    r = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {r.status_code}")
    
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'html.parser')
        products = soup.select("article.product-miniature")
        print(f"Found {len(products)} products on page 1.")
        
        # Check first product
        if products:
            p = products[0]
            title = p.select_one(".product-title a").get_text(strip=True)
            print(f"First product: {title}")
            
            # Check stock
            stock = p.select_one(".in-stock")
            print(f"Stock tag found: {stock is not None}")
            if stock: print(f"Stock text: {stock.get_text(strip=True)}")
    else:
        print("Failed to access page (non-200).")

except Exception as e:
    print(f"Error: {e}")
