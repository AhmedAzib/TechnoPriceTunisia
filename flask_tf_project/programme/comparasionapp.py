import requests
from bs4 import BeautifulSoup

# 1. The Target: We are hunting for a specific phone on MyTek (Example)
# (I chose a stable link for a Samsung phone to test)
url = "https://www.mytek.tn/telephonie-tunisie/smartphone-mobile-tunisie/smartphone-tunisie/smartphone-samsung-galaxy-a05-4go-64go-noir.html"

# 2. The Disguise: We tell the website we are a normal browser (Chrome), not a robot
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print("Searching for price...")

try:
    # 3. The Attack: Go to the website
    response = requests.get(url, headers=headers)
    
    # 4. The Analysis: Read the page code
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 5. The Extraction: Find the price tag
    # (MyTek usually stores price in a generic class, let's try to find the main price)
    price_box = soup.find('span', class_='price')
    
    if price_box:
        price = price_box.text.strip()
        print(f"SUCCESS! Found Price: {price}")
    else:
        print("Connected to site, but couldn't find the specific price tag. The site structure might have changed.")

except Exception as e:
    print(f"Error: {e}")