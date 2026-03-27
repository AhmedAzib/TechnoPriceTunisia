import requests
from bs4 import BeautifulSoup
import re
from .models import Product

# ⛔ THE SMART FILTER: Blacklist "junk" words
KEYWORDS_TO_IGNORE = [
    "coque", "etui", "étui", "film", "verre", "protection", 
    "cable", "câble", "chargeur", "adaptateur", "support", 
    "ecouteur", "silicone", "pack de protection",
    "toner", "cartouche", "encre"
]

def is_valid_product(name):
    """Returns False if the name contains a banned word."""
    name_lower = name.lower()
    for word in KEYWORDS_TO_IGNORE:
        if word in name_lower:
            return False # Trash it!
    return True # Keep it!

# ==========================================
# 🛒 SHOP 1: MYTEK
# ==========================================
def scrape_mytek(query):
    search_term = query.replace(' ', '+')
    url = f"https://www.mytek.tn/catalogsearch/result/?q={search_term}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    
    print(f"🕵️  MyTek is hunting for: {query}...")
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all('div', class_='product-item-info')
        
        count = 0
        for item in items[:10]: 
            try:
                link_tag = item.find('a', class_='product-item-link')
                name = link_tag.text.strip()
                
                # 🛑 FILTER CHECK
                if not is_valid_product(name):
                    continue 

                product_url = link_tag['href']
                price_tag = item.find('span', class_='price')
                
                if price_tag:
                    clean_price = re.sub(r'[^\d.]', '', price_tag.text.strip().replace(',', '.'))
                    Product.objects.update_or_create(
                        url=product_url,
                        defaults={'name': name, 'price': clean_price, 'shop_name': "MyTek"}
                    )
                    count += 1
            except: continue
        return count
    except Exception as e:
        print(f"MyTek Error: {e}")
        return 0

# ==========================================
# 🛒 SHOP 2: TUNISIANET (Deep Search)
# ==========================================
def scrape_tunisianet(query):
    search_term = query.replace(' ', '+')
    url = f"https://www.tunisianet.com.tn/recherche?controller=search&s={search_term}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    
    print(f"🕵️  Tunisianet is hunting deep for: {query}...")
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        titles = soup.find_all('h2', class_='product-title')
        
        count = 0
        # Look at top 30 items to skip past the cases
        for title in titles[:30]:
            try:
                link_tag = title.find('a')
                if not link_tag: continue
                name = link_tag.text.strip()

                # 🛑 FILTER CHECK
                if not is_valid_product(name):
                    continue

                product_url = link_tag['href']
                price_tag = title.find_next('span', class_='price')
                
                if price_tag:
                    raw_price = price_tag.text.strip()
                    clean_price = re.sub(r'[^\d.]', '', raw_price.replace(',', '.').replace(' ', ''))
                    
                    Product.objects.update_or_create(
                        url=product_url,
                        defaults={'name': name, 'price': clean_price, 'shop_name': "Tunisianet"}
                    )
                    count += 1
            except: continue
        return count
    except Exception as e:
        print(f"Tunisianet Error: {e}")
        return 0