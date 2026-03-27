
import requests
from bs4 import BeautifulSoup

url = "https://spacenet.tn/130-smartphone-tunisie"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print(f"Testing access to {url}...")
try:
    res = requests.get(url, headers=headers, timeout=15)
    print(f"Status Code: {res.status_code}")
    if res.status_code == 200:
        soup = BeautifulSoup(res.content, 'html.parser')
        products = soup.select('.item-product') # Guessing selector, will adjust
        if not products:
             products = soup.select('.product-miniature') # Common PrestaShop
        
        print(f"Found {len(products)} products on page 1.")
        if products:
            print("First product HTML:")
            print(products[0].prettify()[:500])
    else:
        print("Failed to access website.")
except Exception as e:
    print(f"Error: {e}")
