
from curl_cffi import requests
import textwrap

def test_cookies():
    url = "https://www.mytek.tn/gigabyte-g6-kf-pc-portable-gamer-i7.html"
    
    cookies = {
        "_gcl_au": "1.1.893701661.1767554404",
        "form_key": "KiJOGpuMS8rZsgTr",
        "mage-cache-sessid": "true",
        "_ga": "GA1.1.1813254457.1767554404",
        "section_data_ids": "{\"customer\":1767555619,\"cart\":1767555619}",
        "_ga_7ZZBB6THYG": "GS2.1.s1767554403$o1$g1$t1767555620$j60$l0$h0"
    }

    try:
        print(f"Requesting {url} with cookies...")
        response = requests.get(
            url, 
            cookies=cookies,
            impersonate="chrome110",
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        # Check for price
        html = response.text
        if "product-info-price" in html or "price-box" in html:
            print("SUCCESS: Price block found in HTML!")
            with open("mytek_cookie_success.html", "w", encoding="utf-8") as f:
                f.write(html)
        else:
            print("FAILURE: Price block NOT found.")
            with open("mytek_cookie_fail.html", "w", encoding="utf-8") as f:
                f.write(html)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_cookies()
