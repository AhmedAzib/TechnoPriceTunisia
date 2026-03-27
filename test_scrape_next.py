import requests
from bs4 import BeautifulSoup
import json

URL = "https://megapc.tn/shop/COMPOSANTS/PROCESSEUR"

try:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    r = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Check for Next.js data
    next_data = soup.find("script", {"id": "__NEXT_DATA__"})
    if next_data:
        print("FOUND __NEXT_DATA__!")
        data = json.loads(next_data.string)
        # Print a snippet to verify structure
        print(json.dumps(data, indent=2)[:500])
        
        # Try to find products in props
        try:
            props = data.get("props", {}).get("pageProps", {})
            # Usually products are deep inside. Just printing keys to see structure.
            print("Keys in pageProps:", props.keys())
        except:
            print("Could not traverse props")
    else:
        print("NO __NEXT_DATA__ found.")
        # Check title to see if we got blocked
        print("Page Title:", soup.title.string if soup.title else "No Title")

except Exception as e:
    print(f"Error: {e}")
