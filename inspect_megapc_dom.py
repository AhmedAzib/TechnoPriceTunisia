import requests
from bs4 import BeautifulSoup
import json

URL = "https://megapc.tn/shop/COMPOSANTS/PROCESSEUR"

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(URL, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 1. Try to find product list containers
    # Common classes: product-layout, product-grid, item, card
    products = soup.select('.product-layout') or soup.select('.product-thumb') or soup.select('.item')
    
    print(f"Found {len(products)} product candidates.")
    
    if products:
        first = products[0]
        print("\n--- FIRST PRODUCT SAMPLE ---")
        # Print class names and structure
        print(first.prettify()[:1000]) 
        
        # Try to find specific elements in the first product
        title = first.select_one('h4 a') or first.select_one('.name a') or first.select_one('.caption h4 a')
        price = first.select_one('.price-new') or first.select_one('.price') or first.select_one('.price-normal')
        stock = first.select_one('.stock') or first.select_one('.availability') or first.select_one('.label-success')
        
        print("\n--- DETECTED DATA ---")
        print(f"Title: {title.get_text(strip=True) if title else 'Not Found'}")
        print(f"Price: {price.get_text(strip=True) if price else 'Not Found'}")
        print(f"Stock Badge Class/Text: {stock}")
    # 2. Check for Next.js Data Blob (Common in SPAs)
    next_data = soup.find('script', id='__NEXT_DATA__')
    if next_data:
        print("\n--- FOUND NEXT.JS DATA ---")
        try:
            json_blob = json.loads(next_data.string)
            print("Keys in Root:", list(json_blob.keys()))
            
            # Navigate to props
            props = json_blob.get('props', {})
            page_props = props.get('pageProps', {})
            print("Keys in pageProps:", list(page_props.keys()))
            
            # Try to find products in pageProps
            # Common keys: products, category, initialState
            if 'products' in page_props:
                prods = page_props['products']
                print(f"Found {len(prods)} products in JSON props.")
                if len(prods) > 0:
                    print("Sample Product in JSON:", prods[0].get('name', 'No Name'))
            elif 'category' in page_props:
                 cat = page_props['category']
                 print("Category Data Found:", cat.get('name'))
                 # Sometimes products are nested in category
            
        except Exception as e:
            print(f"Error parsing JSON blob: {e}")
    else:
        print("No __NEXT_DATA__ script found.")

except Exception as e:
    print(f"Error: {e}")
