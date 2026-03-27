
from curl_cffi import requests

def test_mytek():
    url = "https://www.mytek.tn/informatique/ordinateurs-portables/pc-gamer.html"
    print(f"Testing URL: {url}")
    try:
        response = requests.get(url, impersonate="chrome110", timeout=20)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            print(f"HTML Length: {len(html)}")
            
            if "product-item-link" in html:
                print("SUCCESS: Found 'product-item-link' in HTML!")
            else:
                print("FAILURE: 'product-item-link' NOT found.")
                
            if "TND" in html:
                 print("SUCCESS: Found 'TND' in HTML!")
            
            with open("mytek_curl_debug.html", "w", encoding="utf-8") as f:
                f.write(html)
        else:
            print("Failed to retrieve page.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_mytek()
