import requests

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

url = "https://megapc.tn/shop/category/ordinateur-portable"

try:
    r = requests.get(url, headers=header, timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("Success!")
        print(r.text[:500])
        if "product" in r.text or "article" in r.text:
            print("Found product keywords.")
    else:
        print("Failed.")
except Exception as e:
    print(f"Error: {e}")
