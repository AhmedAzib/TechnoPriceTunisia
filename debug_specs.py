import requests
from bs4 import BeautifulSoup

url = "https://www.sbsinformatique.com/cartes-graphiques-tunisie/carte-graphique-gigabyte-geforce-rtx-5050-windforce-oc-8g-tunisie"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

print(f"Status Code: {response.status_code}")

# Check list-details
list_details = soup.find('ul', class_='list-details')
if list_details:
    print("Found ul.list-details:")
    print(list_details.prettify()[:1000]) # Print first 1000 chars
else:
    print("ul.list-details NOT found")

# Check data-sheet
data_sheet = soup.find('dl', class_='data-sheet')
if data_sheet:
    print("Found dl.data-sheet:")
    print(data_sheet.prettify()[:1000])
else:
    print("dl.data-sheet NOT found")

# Check for simpler description text if structured data is missing
desc = soup.find('div', class_='product-description')
if desc:
    print("Found product-description div")
else:
    print("product-description NOT found")
