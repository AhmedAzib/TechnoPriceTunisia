import requests
from bs4 import BeautifulSoup

url = "https://megapc.tn/shop/COMPOSANTS/BARETTE%20M%C3%89MOIRE"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, 'html.parser')

items = soup.select(".border-gray-100")
if not items:
    items = soup.select("a[href*='/shop/product/']")

print(f"Found {len(items)} items")

for el in items[:5]:
    img = el.select_one("img")
    if img:
        print("IMG HTML:", img)
