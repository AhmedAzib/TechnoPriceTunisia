from bs4 import BeautifulSoup
import json
import re

def clean_price(price_str):
    if not price_str:
        return 0.0
    # specific fix for Tdiscount format "1 409.0 DT" -> 1409.0
    # Remove non-numeric except .
    clean = re.sub(r'[^\d.]', '', price_str.replace(' ', '').replace(',', '.'))
    try:
        return float(clean)
    except:
        return 0.0

def parse():
    with open('tdiscount_snippet.html', 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    products = []
    
    items = soup.select('li.product')
    print(f"Found {len(items)} items.")

    for el in items:
        try:
            # Check stock
            classes = el.get('class', [])
            if 'instock' not in classes:
                continue

            # Title
            title_elem = el.select_one('.woo-loop-product__title a')
            if not title_elem:
                continue
            title = title_elem.get_text(strip=True)
            link = title_elem['href']

            # Price extraction
            price = 0.0
            price_container = el.select_one('.price')
            if price_container:
                # Check for sale price first
                ins_price = price_container.select_one('ins .amount bdi')
                if ins_price:
                    price = clean_price(ins_price.get_text())
                else:
                    # Normal price
                    normal_price = price_container.select_one('.amount bdi')
                    if normal_price:
                        price = clean_price(normal_price.get_text())

            # Image - prioritize src, fallback to data-lazy-src
            img_elem = el.select_one('.mf-product-thumbnail img')
            image = ""
            if img_elem:
                image = img_elem.get('src') or img_elem.get('data-lazy-src')
            
            product = {
                "title": title,
                "price": price,
                "link": link,
                "image": image,
                "source": "Tdiscount",
                "category": "Smartphones"
            }
            products.append(product)
            print(f"Added: {title} - {price} DT")

        except Exception as e:
            print(f"Error parsing item: {e}")

    with open('frontend/src/data/tdiscount_products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(products)} products.")

if __name__ == "__main__":
    parse()
