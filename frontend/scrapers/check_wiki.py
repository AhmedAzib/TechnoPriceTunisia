
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://google.com'
}

try:
    url = "https://wiki.tn/smartphones"
    print(f"Checking {url}...")
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        products = soup.select('.product-card--grid, .product-small, .product') # Trying generic selectors
        print(f"Found {len(products)} products.")
        if products:
             print("First product HTML:")
             print(products[0].prettify()[:500])
             
             # Check for "En stock"
             stocks = soup.select('.stock-status-badge, .brxe-shortcode-dispo')
             print(f"Found {len(stocks)} stock badges.")
    else:
        print("Failed to access page.")

except Exception as e:
    print(f"Error: {e}")
