
from curl_cffi import requests
import textwrap

def test_cache():
    # Google Cache URL format
    target_url = "https://www.mytek.tn/gigabyte-g6-kf-pc-portable-gamer-i7.html"
    cache_url = f"http://webcache.googleusercontent.com/search?q=cache:{target_url}"
    
    try:
        print(f"Requesting {cache_url}...")
        response = requests.get(
            cache_url, 
            impersonate="chrome110",
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            if "price" in html or "TND" in html:
                 print("SUCCESS: Price/TND found in Cache!")
                 with open("mytek_cache_debug.html", "w", encoding="utf-8") as f:
                     f.write(html)
            else:
                 print("Cache retrieved but no price found.")
        elif response.status_code == 404:
            print("Page not in Google Cache.")
        else:
            print(f"Error: {response.status_code}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_cache()
