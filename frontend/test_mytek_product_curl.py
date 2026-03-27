
from curl_cffi import requests

def simple_test():
    url = "https://www.mytek.tn/gigabyte-g6-kf-pc-portable-gamer-i7.html"
    try:
        response = requests.get(url, impersonate="chrome110", timeout=20)
        if response.status_code == 200:
             with open("mytek_product_test.html", "w", encoding="utf-8") as f:
                 f.write(response.text)
             print("Success")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    simple_test()
