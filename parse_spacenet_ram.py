from bs4 import BeautifulSoup
import json

with open("c:/Users/USER/Documents/programmation/spacenet_ram_page1.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

products = soup.select('.item-product') or soup.select('.product-miniature')

if not products:
    print("No products found with common selectors.")
else:
    print(f"Found {len(products)} products.")
    for i, p in enumerate(products[:2]):
        print(f"--- Product {i+1} ---")
        title_elem = p.select_one('.h3.product-title a') or p.select_one('.product-title a')
        title = title_elem.text.strip() if title_elem else 'No title'
        link = title_elem['href'] if title_elem else 'No link'
        
        price_elem = p.select_one('.price')
        price = price_elem.text.strip() if price_elem else 'No price'
        
        img_elem = p.select_one('img')
        img = img_elem['src'] if img_elem else 'No image'
        
        stock_elem = p.select_one('.product-availability') or p.select_one('.in-stock') or p.select_one('.statut')
        stock = stock_elem.text.strip() if stock_elem else 'No stock info'
        
        desc_elem = p.select_one('.product-description-short') or p.select_one('.list-ds') or p.select_one('.product-desc')
        desc = desc_elem.text.strip() if desc_elem else 'No desc'

        brand_elem = p.select_one('.manufacturer-logo img')
        brand = brand_elem['alt'] if brand_elem and brand_elem.has_attr('alt') else 'No brand'
        
        print(f"Title: {title}")
        print(f"Link: {link}")
        print(f"Price: {price}")
        print(f"Image: {img}")
        print(f"Stock: {stock}")
        print(f"Desc: {desc}")
        print(f"Brand: {brand}")
