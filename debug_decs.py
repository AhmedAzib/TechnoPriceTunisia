import requests
from bs4 import BeautifulSoup
import json

url = "https://www.sbsinformatique.com/cartes-graphiques-tunisie/carte-graphique-gigabyte-geforce-rtx-5050-windforce-oc-8g-tunisie"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# Check tvproduct-page-decs
decs = soup.find('div', class_='tvproduct-page-decs')
if decs:
    print("Found div.tvproduct-page-decs:")
    print(decs.get_text()[:500])
else:
    print("div.tvproduct-page-decs NOT found")

# Check product-details data attribute
details_div = soup.find('div', id='product-details')
if details_div and details_div.has_attr('data-product'):
    print("\nFound data-product JSON:")
    try:
        data = json.loads(details_div['data-product'])
        print(f"Description Short: {data.get('description_short', '')[:200]}...")
        print(f"Description: {data.get('description', '')[:200]}...")
    except:
        print("Failed to parse JSON")
else:
    print("\ndiv#product-details with data-product NOT found")
