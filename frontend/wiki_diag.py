from curl_cffi import requests
from bs4 import BeautifulSoup

url = "https://wiki.tn/ordinateur-pc-portable/"
print(f"Fetching {url}...")
try:
    response = requests.get(
        url, 
        impersonate="chrome110", 
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        },
        timeout=30
    )
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        products = soup.select('div.product-card--grid')
        print(f"Found {len(products)} products with selector 'div.product-card--grid'")
        
        if not products:
            print("Trying alternative selectors...")
            print(f"Num 'brxe-hopnez': {len(soup.select('.brxe-hopnez'))}")
            print(f"Num 'product-card': {len(soup.select('.product-card'))}")
            
            # Print first 500 chars of body to see if blocked
            print("Body preview:")
            print(soup.body.get_text()[:500] if soup.body else "No body")
            
except Exception as e:
    print(f"Error: {e}")
