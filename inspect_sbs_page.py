import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def check_page(page_num):
    url = f"https://www.sbsinformatique.com/carte-mere-tunisie?page={page_num}"
    print(f"Checking Page {page_num}...")
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(r.content, "html.parser")
        items = soup.find_all('article', class_='product-miniature')
        print(f"Found {len(items)} items.")
        
        for item in items:
            title_tag = item.find('div', class_='product-title').find('a')
            title = title_tag.get_text().strip()
            
            # Check stock
            stock_status = "In Stock"
            cart_btn = item.find('button', class_='add-to-cart')
            if not cart_btn or cart_btn.has_attr('disabled') or 'disable' in cart_btn.get('class', []):
                 stock_status = "Out (Button)"
            
            available = item.find('span', class_='product-availability')
            if available:
                 avail_text = available.get_text().strip()
                 print(f"    Avail Text: '{avail_text}'")
                 if "rupture" in avail_text.lower() or "stock épuisé" in avail_text.lower():
                      stock_status = "Out (Label)"
            else:
                 print("    Avail Text: None")
            
            print(f"  [{stock_status}] {title}")
            
    except Exception as e:
        print(f"Error: {e}")

check_page(1)
check_page(2)
