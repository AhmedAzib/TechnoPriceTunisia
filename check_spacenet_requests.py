import requests

url = "https://spacenet.tn/22-carte-mere"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    print(f"Fetching {url}...")
    r = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        print("Success! Content length:", len(r.text))
        if "product-miniature" in r.text:
            print("Found product cards in HTML.")
        else:
            print("No product cards found in HTML (might be JS rendered).")
    else:
        print("Failed to fetch.")
except Exception as e:
    print(f"Error: {e}")
