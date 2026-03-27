
from bs4 import BeautifulSoup

with open("spacenet_debug.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
products = soup.select(".product-miniature")

if products:
    print(f"Found {len(products)} products.")
    first_product = products[4] # Get the 5th one, usually better populated
    print(first_product.prettify())
else:
    print("No .product-miniature found.")
