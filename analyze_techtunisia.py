
from bs4 import BeautifulSoup
import re

try:
    with open("debug_techtunisia.html", "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    
    print("--- HTML ANALYSIS ---")
    
    # Try to find product containers
    # Common PrestaShop classes: product-miniature, ajax_block_product, item
    products = soup.find_all(class_=re.compile("product"))
    print(f"Found {len(products)} elements with 'product' class.")
    
    # Specific checks
    miniatures = soup.find_all(class_="product-miniature")
    print(f"product-miniature count: {len(miniatures)}")
    
    if miniatures:
        p = miniatures[0]
        print("\n--- FIRST PRODUCT SAMPLE ---")
        print(p.prettify()[:1000])
        
        # Check Title
        title = p.find("h3", class_="product-title")
        if title: print(f"Title Tag: {title}")
        else: print("Title h3.product-title NOT found")
        
        # Check Price
        price = p.find(class_="price")
        if price: print(f"Price Tag: {price.text.strip()}")
        else: print("Price .price NOT found")
        
    else:
        print("\n No 'product-miniature' found. Dumping first 1000 chars of body:")
        print(soup.body.prettify()[:1000] if soup.body else "No body tag")

except Exception as e:
    print(f"Error: {e}")
