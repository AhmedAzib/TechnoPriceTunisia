import requests
from bs4 import BeautifulSoup
import re

url = "https://www.sbsinformatique.com/cartes-graphiques-tunisie/carte-graphique-gigabyte-geforce-rtx-5050-windforce-oc-8g-tunisie"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

desc = soup.find('div', class_='product-description')
if desc:
    print("Content of product-description:")
    print(desc.prettify())
