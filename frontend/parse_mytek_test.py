
from bs4 import BeautifulSoup

def parse_html():
    try:
        with open("mytek_product_test.html", "r", encoding="utf-8") as f:
            html = f.read()
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Title
        title_tag = soup.find('h1', class_='page-title')
        title = title_tag.get_text().strip() if title_tag else "No Title Found"
        
        # Price
        # Magento usually has price-box
        price_box = soup.find('div', class_='price-box')
        price = "No Price Found"
        if price_box:
            price_tag = price_box.find('span', class_='price')
            if price_tag:
                price = price_tag.get_text().strip()
        
        print(f"Title: {title}")
        print(f"Price: {price}")
        
        # Image
        # .gallery-placeholder > img
        img_tag = soup.find('img', class_='gallery-placeholder__image') # Magento specific?
        if not img_tag:
             # Try standard product image
             img_tag = soup.find('img', alt=title)
        
        print(f"Image: {img_tag['src'] if img_tag else 'No Image'}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parse_html()
