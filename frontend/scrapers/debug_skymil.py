import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://skymil-informatique.com/29-carte-graphique-tunisie?page=1"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

print(f"Fetching {url}...")
response = requests.get(url, headers=headers, verify=False)
soup = BeautifulSoup(response.content, 'html.parser')

items = soup.select('.product-miniature')
print(f"Found {len(items)} items.")

for i, item in enumerate(items[:3]):
    print(f"\nItem {i+1}:")
    title = item.select_one('.product-title a')
    print(f"  Title: {title.get_text().strip() if title else 'N/A'}")
    
    stock_elem = item.select_one('.product-availability')
    if stock_elem:
        print(f"  Stock Spec (raw): '{stock_elem.get_text()}'")
        print(f"  Stock Spec (stripped): '{stock_elem.get_text().strip()}'")
        classes = stock_elem.get("class", [])
        print(f"  Stock Classes: {classes}")
    else:
        print("  Stock Element: Not Found")

    # Also print the entire HTML of the first item to see if we missed something
    if i == 0:
         link = item.select_one('.product-title a')['href']
         print(f"Fetching Product Page: {link}...")
         prod_resp = requests.get(link, headers=headers, verify=False)
         prod_soup = BeautifulSoup(prod_resp.content, 'html.parser')
         
         # Print availability section from product page
         avail = prod_soup.select_one('#product-availability') # guess ID
         if not avail:
             avail = prod_soup.select_one('.product-availability')
             
         print(f"Product Page Availability: {avail.prettify() if avail else 'Not Found'}")
         
         # Print first 2000 chars of product page to hunt for stock
         print("\nProduct Page HTML Snippet:")
         print(prod_soup.prettify()[:2000])
         break
