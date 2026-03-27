import requests
from bs4 import BeautifulSoup

url = "https://www.sbsinformatique.com/barrettes-pc-de-bureau-tunisie"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

products = soup.select('.product-miniature')

if (not products):
    print("No products found with .product-miniature. Trying .item-product...")
    products = soup.select('.item-product')

print(f"Found {len(products)} products on page 1.")

if products:
    first_product = products[0]
    with open('c:/Users/USER/Documents/programmation/sbs_ram_sample.html', 'w', encoding='utf-8') as f:
        f.write(first_product.prettify())
        
        # Try looking for pagination
        pagination = soup.select('.pagination')
        f.write(f"\n\nPagination found: {len(pagination) > 0}\n")
        if pagination:
            f.write(pagination[0].prettify())
            
    print("HTML saved to sbs_ram_sample.html")
