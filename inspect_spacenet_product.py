import requests
from bs4 import BeautifulSoup

url = "https://spacenet.tn/cartes-meres/97356-carte-mere-biostar-h81m-ide-lga-1150-ddr3.html"
headers = {"User-Agent": "Mozilla/5.0"}

try:
    r = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {r.status_code}")
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Check availability-related elements
    print("\n--- Availability Elements ---")
    
    # Method 1: ID
    avail_id = soup.find(id="product-availability")
    if avail_id:
        print(f"ID 'product-availability': '{avail_id.get_text(strip=True)}'")
        print(f"Classes: {avail_id.get('class')}")
        print(str(avail_id))
    else:
        print("ID 'product-availability' NOT FOUND")
        
    # Method 2: Common Prestashop classes
    for cls in ["product-availability", "availability", "stock", "label-availability"]:
        els = soup.find_all(class_=cls)
        for el in els:
            print(f"Class '{cls}': '{el.get_text(strip=True)}'")
            
    # Method 3: Text search
    if "En stock" in r.text:
        print("\n'En stock' found in text.")
    else:
        print("\n'En stock' NOT found in text.")

except Exception as e:
    print(e)
