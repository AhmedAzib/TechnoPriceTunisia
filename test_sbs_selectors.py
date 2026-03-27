from bs4 import BeautifulSoup

with open('c:/Users/USER/Documents/programmation/sbs_ram_sample.html', 'r', encoding='utf-8') as f:
    html = f.read()
    
soup = BeautifulSoup(html, 'html.parser')

products = soup.select('.item-product') or soup.select('.product-miniature')
print(f"Products found in sample: {len(products)}")

for i, product in enumerate(products):
    print(f"\n--- Product {i} ---")
    cart_btn = product.select_one('button.tvproduct-add-to-cart')
    print(f"Cart btn found: {cart_btn is not None}")
    if cart_btn:
        print(f"Cart btn classes: {cart_btn.get('class')}")
        print(f"Cart btn disabled attr: {cart_btn.has_attr('disabled')}")
        
    title_elem = product.select_one('.tvproduct-name h6') or product.select_one('.product-title h6')
    print(f"Title elem: {title_elem.text.strip() if title_elem else 'None'}")
