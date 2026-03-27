import os
import django
import requests
from bs4 import BeautifulSoup
import re

# ==========================================
# 🔌 THE CONNECTION
# ==========================================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()
from products.models import Product
# ==========================================

# TARGET: Samsung Galaxy A16
url = "https://www.mytek.tn/smartphone-samsung-galaxy-a16-4go-128go-noir.html"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
}

print(f"🕵️  Connecting to MyTek...")

try:
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    final_price = None

    # STRATEGY 1: Meta Tag (This worked before!)
    meta_tag = soup.find("meta", property="product:price:amount")
    if meta_tag:
        print(f"✅ Found Price (via Meta): {meta_tag['content']}")
        final_price = meta_tag['content']

    # STRATEGY 2: Visual Price Box (Backup)
    if not final_price:
        all_prices = soup.find_all('span', class_='price')
        for price in all_prices:
            text = price.text.strip()
            if text and any(char.isdigit() for char in text):
                print(f"✅ Found Price (via Box): {text}")
                final_price = text
                break

    # SAVE TO DATABASE
    if final_price:
        # CLEANING: Remove "TND", spaces, and fix comma
        # Turn "499,000" into "499.000"
        clean_price = str(final_price).replace('TND', '').replace('DT', '').replace(' ', '').replace(',', '.')
        # Remove invisible characters
        clean_price = re.sub(r'[^\d.]', '', clean_price)
        
        print(f"💾 Saving cleaned price '{clean_price}' to Database...")
        
        Product.objects.update_or_create(
            url=url,
            defaults={
                'name': "Samsung Galaxy A16 - 128GB",
                'price': clean_price,
                'shop_name': "MyTek"
            }
        )
        print("🎉 SUCCESS! Product saved in the Vault.")
        
    else:
        print("❌ Error: Could not find price with any strategy.")

except Exception as e:
    print(f"Critical Error: {e}")