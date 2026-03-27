import requests
from bs4 import BeautifulSoup
import json

URL = "https://www.sbsinformatique.com/cartes-graphiques-tunisie/carte-graphique-gigabyte-geforce-rtx-5050-windforce-oc-8g-tunisie"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def debug_details():
    print(f"Fetching {URL}...")
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 1. Check tvproduct-page-decs
    desc = soup.find('div', class_='tvproduct-page-decs')
    if desc:
        print("\n--- FOUND class='tvproduct-page-decs' ---")
        print(desc.prettify()[:2000]) # Print first 2000 chars
    else:
        print("\n--- NOT FOUND class='tvproduct-page-decs' ---")
        
    # 2. Check data-sheet
    sheet = soup.find('dl', class_='data-sheet')
    if sheet:
        print("\n--- FOUND class='data-sheet' ---")
        print(sheet.prettify()[:2000])
    else:
        print("\n--- NOT FOUND class='data-sheet' ---")

    # 3. Check for the text "Cœurs CUDA" anywhere
    if "Cœurs CUDA" in response.text:
        print("\n--- FOUND 'Cœurs CUDA' in raw text ---")
    else:
        print("\n--- 'Cœurs CUDA' NOT FOUND in raw text ---")

    # 4. Dump all text in main column ?
    main_col = soup.find('div', class_='product-information')
    if main_col:
       print("\n--- Product Info Dump ---")
       print(main_col.get_text('\n')[:1000])

if __name__ == "__main__":
    debug_details()
