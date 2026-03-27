import requests
from bs4 import BeautifulSoup

url = "https://spacenet.tn/cartes-meres/97356-carte-mere-biostar-h81m-ide-lga-1150-ddr3.html"
headers = {"User-Agent": "Mozilla/5.0"}

try:
    r = requests.get(url, headers=headers, timeout=10)
    html = r.text
    
    index = html.find("En stock")
    if index != -1:
        start = max(0, index - 300)
        end = min(len(html), index + 300)
        print(f"Context around 'En stock':\n{html[start:end]}")
        
    # Also look for classes that might be relevant
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup.find_all(True):
        if "stock" in tag.get_text().lower() and len(tag.get_text()) < 50:
            print(f"Tag with 'stock' text: {tag.name} Class: {tag.get('class')} Text: {tag.get_text(strip=True)}")

except Exception as e:
    print(e)
