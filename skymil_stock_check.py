import requests
from bs4 import BeautifulSoup

url = "https://skymil-informatique.com/30-memoire-ram-tunisie?page=2"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

products = soup.select('article.product-miniature')

for p in products:
    title_elem = p.select_one('.product-title a')
    title = title_elem.text.strip() if title_elem else "Unknown"
    
    in_stock_btn = p.select_one('.add-to-cart')
    has_btn = "YES" if in_stock_btn else "NO"
    
    price_elem = p.select_one('span.price')
    price = getattr(price_elem, 'text', '').encode('ascii', 'ignore').decode('ascii').strip()
    
    print(f"Title: {title[:30]} | Has Add-To-Cart: {has_btn} | Price: {price}")
