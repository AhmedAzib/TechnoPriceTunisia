
import requests

url = "https://tunisiatech.tn/25-smartphones-tunisie"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print(f"Fetching {url}...")
try:
    res = requests.get(url, headers=headers, timeout=15)
    if res.status_code == 200:
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(res.text)
        print("Saved debug_page.html")
    else:
        print(f"Failed: {res.status_code}")
except Exception as e:
    print(f"Error: {e}")
