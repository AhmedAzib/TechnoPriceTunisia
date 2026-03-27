from bs4 import BeautifulSoup

with open("c:/Users/USER/Documents/programmation/spacenet_ram_page1.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

products = soup.select('.item-product') or soup.select('.product-miniature')

if products:
    print(products[0].prettify())
