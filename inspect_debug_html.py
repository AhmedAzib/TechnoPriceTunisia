from bs4 import BeautifulSoup

with open("debug_selenium.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# info
print(f"Page Title: {soup.title.text if soup.title else 'No Title'}")

# Try to find product list
product_items = soup.select(".product-item")
print(f"Found {len(product_items)} .product-item elements")

if not product_items:
    print("Checking other potential selectors...")
    # Check for anything that look like a product list
    items = soup.select("li.item.product.product-item")
    print(f"Found {len(items)} li.item.product.product-item")
    
    infos = soup.select(".product-item-info")
    print(f"Found {len(infos)} .product-item-info")

# If we found items, print the first one's structure
if product_items:
    first = product_items[0]
    print("\nFirst Item Structure:")
    print(first.prettify()[:500])
    
    # Check specific fields in first item
    print("\nChecking fields in first item:")
    link = first.select_one("a.product-item-photo")
    print(f"Link class .product-item-photo: {'Found' if link else 'Not Found'}")
    
    details = first.select_one(".product-item-details")
    print(f"Details class .product-item-details: {'Found' if details else 'Not Found'}")
